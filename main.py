from fastapi import FastAPI,HTTPException,Depends,Header,WebSocket,WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import json
from model import signupreq,userloginres,userlogin,CreateClassRequest,AddStudentRequest,attendancestartReq
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
import bcrypt
import jwt
from datetime import datetime,timedelta


load_dotenv()
print(os.getenv("DB_URL"))
client=MongoClient(os.getenv("DB_URL"))
db=client["attendence_db"]
users=db["users"]
classes=db["classes"]
attendance_records=db["attendance"]

# Global in-memory state for active attendance session
activeSession = None

# Store all active WebSocket connections
active_connections: List[WebSocket] = []

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, "secret token", algorithms=["HS256"])
        email = payload.get("email")
        user_id = payload.get("id")

        if not email or not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        user = users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return {
            "_id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

def require_teacher(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Forbidden, teacher access required"
        )
    return current_user
def require_student(current_user:dict=Depends(get_current_user)):
    if current_user["role"]!="student":
        raise HTTPException(
            status_code=403,
            detail="Forbidden student access required"
        )
    return current_user
app=FastAPI()

@app.get("/")
async def get():
    return {"this is attendece":"backend"}


@app.post("/signup")
def signup(user:signupreq):
    existing= users.find_one({"email":user.email})
    if existing:
        raise HTTPException(
            status_code=410,
            detail="user already existed"
        )

    hashed=bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    result=users.insert_one(
        {
            "name":user.name,
            "email":user.email,
            "password":hashed,
            "role":user.role
        }
    )

    created_user = users.find_one({"_id": result.inserted_id})

    return {
        "success": True,
        "data": {
            "_id": str(created_user["_id"]),
            "name": created_user["name"],
            "email": created_user["email"],
            "role": created_user["role"]
        }
    }


@app.post("/login")
def login(req:userlogin):
    user=users.find_one({"email":req.email})
    if not user:
        raise HTTPException(
            status_code=410,
            detail="USER NOT FOUND"
        )

    if not bcrypt.checkpw(req.password.encode('utf-8'), user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )
    tokenobj={
    "email": req.email, 
    "id": str(user["_id"]),
    "exp": datetime.utcnow() + timedelta(days=1)}
    
    token=jwt.encode(tokenobj, "secret token", algorithm="HS256")

    print(token)

    return {"token":token,
            "type":"bearer"}



@app.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "data": current_user
    }


@app.post("/class", status_code=201)
def create_class(request: CreateClassRequest, teacher: dict = Depends(require_teacher)):

    new_class = {
        "className": request.className,
        "teacherId": ObjectId(teacher["_id"]),
        "studentIds": []
    }

    result = classes.insert_one(new_class)
    created_class = classes.find_one({"_id": result.inserted_id})

    return {
        "success": True,
        "data": {
            "_id": str(created_class["_id"]),
            "className": created_class["className"],
            "teacherId": str(created_class["teacherId"]),
            "studentIds": created_class["studentIds"]
        }
    }


@app.post("/class/{class_id}/add-student")
def add_student_to_class(class_id: str, request: AddStudentRequest, teacher: dict = Depends(require_teacher)):
   
    # Find the class
    class_doc = classes.find_one({"_id": ObjectId(class_id)})
    if not class_doc:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    # Check if teacher owns this class
    if str(class_doc["teacherId"]) != teacher["_id"]:
        raise HTTPException(
            status_code=403,
            detail="Forbidden, not class teacher"
        )

    # Verify student exists and has student role
    student = users.find_one({"_id": ObjectId(request.studentId)})
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    if student["role"] != "student":
        raise HTTPException(
            status_code=400,
            detail="User is not a student"
        )

    # Check if student already in class
    student_oid = ObjectId(request.studentId)
    if student_oid in class_doc["studentIds"]:
        raise HTTPException(
            status_code=400,
            detail="Student already in class"
        )

    # Add student to class
    classes.update_one(
        {"_id": ObjectId(class_id)},
        {"$push": {"studentIds": student_oid}}
    )

    # Get updated class
    updated_class = classes.find_one({"_id": ObjectId(class_id)})

    return {
        "success": True,
        "data": {
            "_id": str(updated_class["_id"]),
            "className": updated_class["className"],
            "teacherId": str(updated_class["teacherId"]),
            "studentIds": [str(sid) for sid in updated_class["studentIds"]]
        }
    }

@app.get("/class/{class_id}")
def get_class(class_id: str, current_user: dict = Depends(get_current_user)):
    # Find the class
    class_doc = classes.find_one({"_id": ObjectId(class_id)})
    if not class_doc:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )
    
    # Authorization check
    if current_user["role"] == "teacher":
        # Teacher must own the class
        if str(class_doc["teacherId"]) != current_user["_id"]:
            raise HTTPException(
                status_code=403,
                detail="Forbidden, not class teacher"
            )
    elif current_user["role"] == "student":
        # Student must be enrolled
        if ObjectId(current_user["_id"]) not in class_doc["studentIds"]:
            raise HTTPException(
                status_code=403,
                detail="Forbidden, not enrolled in class"
            )
    
    # Populate students
    students = []
    for student_id in class_doc["studentIds"]:
        student = users.find_one({"_id": student_id})
        if student:
            students.append({
                "_id": str(student["_id"]),
                "name": student["name"],
                "email": student["email"]
            })
    
    return {
        "success": True,
        "data": {
            "_id": str(class_doc["_id"]),
            "className": class_doc["className"],
            "teacherId": str(class_doc["teacherId"]),
            "students": students
        }
    }


@app.get("/students")
def students(current_user:dict=Depends(require_teacher)):
    result=[]
    for student in users.find({"role":"student"}):
        result.append({
         "_id": str(student["_id"]),
        "name": student["name"],
        "email": student["email"]   
        })
    
    return {
      "success":True,
      "data":result
}

@app.post("/attendance/start")
def start_attendance(req: attendancestartReq, teacher: dict = Depends(require_teacher)):
 
    global activeSession

    # Find the class
    class_doc = classes.find_one({"_id": ObjectId(req.classId)})
    if not class_doc:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    # Check if teacher owns this class
    if str(class_doc["teacherId"]) != teacher["_id"]:
        raise HTTPException(
            status_code=403,
            detail="Forbidden, not class teacher"
        )

    # Create ISO timestamp
    started_at = datetime.utcnow().isoformat() + "Z"

    # Set active session
    activeSession = {
        "classId": req.classId,
        "startedAt": started_at,
        "attendance": {}
    }

    return {
        "success": True,
        "data": {
            "classId": req.classId,
            "startedAt": started_at
        }
    }


@app.get("/class/{class_id}/my-attendance")
def get_my_attendance(class_id: str, student: dict = Depends(require_student)):
   
    # Find the class
    class_doc = classes.find_one({"_id": ObjectId(class_id)})
    if not class_doc:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    # Check if student is enrolled
    if ObjectId(student["_id"]) not in class_doc["studentIds"]:
        raise HTTPException(
            status_code=403,
            detail="Forbidden, not enrolled in class"
        )

    # Check if attendance is persisted in DB
    attendance_record = attendance_records.find_one({
        "classId": ObjectId(class_id),
        "studentId": ObjectId(student["_id"])
    })

    if attendance_record:
        return {
            "success": True,
            "data": {
                "classId": class_id,
                "status": attendance_record["status"]
            }
        }
    else:
        return {
            "success": True,
            "data": {
                "classId": class_id,
                "status": None
            }
        }


# WebSocket Helper Functions
async def broadcast_message(message: dict):
    """Send message to all connected WebSocket clients"""
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            disconnected.append(connection)

    # Remove disconnected clients
    for conn in disconnected:
        if conn in active_connections:
            active_connections.remove(conn)


async def send_error(websocket: WebSocket, error_message: str):
    """Send error message to a specific WebSocket client"""
    await websocket.send_json({
        "event": "ERROR",
        "data": {
            "message": error_message
        }
    })


# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
   
    global activeSession

    # Accept connection
    await websocket.accept()

    # Verify JWT token
    if not token:
        await send_error(websocket, "Unauthorized or invalid token")
        await websocket.close()
        return

    try:
        payload = jwt.decode(token, "secret token", algorithms=["HS256"])
        user_id = payload.get("id")
        email = payload.get("email")

        if not user_id or not email:
            await send_error(websocket, "Unauthorized or invalid token")
            await websocket.close()
            return

        # Get user from database
        user = users.find_one({"_id": ObjectId(user_id)})
        if not user:
            await send_error(websocket, "Unauthorized or invalid token")
            await websocket.close()
            return

        # Attach user info to websocket
        websocket.user = {
            "userId": user_id,
            "role": user["role"]
        }

        # Add to active connections
        active_connections.append(websocket)

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_json()
                event = data.get("event")
                event_data = data.get("data", {})

                # Handle different events
                if event == "ATTENDANCE_MARKED":
                    # Teacher only
                    if websocket.user["role"] != "teacher":
                        await send_error(websocket, "Forbidden, teacher event only")
                        continue

                    if not activeSession:
                        await send_error(websocket, "No active attendance session")
                        continue

                    student_id = event_data.get("studentId")
                    status = event_data.get("status")

                    # Update in-memory attendance
                    activeSession["attendance"][student_id] = status

                    # Broadcast to all clients
                    await broadcast_message({
                        "event": "ATTENDANCE_MARKED",
                        "data": {
                            "studentId": student_id,
                            "status": status
                        }
                    })

                elif event == "TODAY_SUMMARY":
                    # Teacher only
                    if websocket.user["role"] != "teacher":
                        await send_error(websocket, "Forbidden, teacher event only")
                        continue

                    if not activeSession:
                        await send_error(websocket, "No active attendance session")
                        continue

                    # Calculate summary
                    attendance_dict = activeSession["attendance"]
                    present = len([s for s in attendance_dict.values() if s == "present"])
                    absent = len([s for s in attendance_dict.values() if s == "absent"])
                    total = present + absent

                    # Broadcast to all clients
                    await broadcast_message({
                        "event": "TODAY_SUMMARY",
                        "data": {
                            "present": present,
                            "absent": absent,
                            "total": total
                        }
                    })

                elif event == "MY_ATTENDANCE":
                    # Student only
                    if websocket.user["role"] != "student":
                        await send_error(websocket, "Forbidden, student event only")
                        continue

                    if not activeSession:
                        await send_error(websocket, "No active attendance session")
                        continue

                    # Get student's status
                    student_status = activeSession["attendance"].get(websocket.user["userId"], "not yet updated")

                    # Send to this student only (unicast)
                    await websocket.send_json({
                        "event": "MY_ATTENDANCE",
                        "data": {
                            "status": student_status
                        }
                    })

                elif event == "DONE":
                    # Teacher only
                    if websocket.user["role"] != "teacher":
                        await send_error(websocket, "Forbidden, teacher event only")
                        continue

                    if not activeSession:
                        await send_error(websocket, "No active attendance session")
                        continue

                    # Get all students in the active class
                    class_doc = classes.find_one({"_id": ObjectId(activeSession["classId"])})
                    if class_doc:
                        # Mark absent for students not in attendance dict
                        for student_id in class_doc["studentIds"]:
                            student_id_str = str(student_id)
                            if student_id_str not in activeSession["attendance"]:
                                activeSession["attendance"][student_id_str] = "absent"

                        # Persist to MongoDB
                        for student_id_str, status in activeSession["attendance"].items():
                            attendance_records.update_one(
                                {
                                    "classId": ObjectId(activeSession["classId"]),
                                    "studentId": ObjectId(student_id_str)
                                },
                                {
                                    "$set": {
                                        "classId": ObjectId(activeSession["classId"]),
                                        "studentId": ObjectId(student_id_str),
                                        "status": status
                                    }
                                },
                                upsert=True
                            )

                        # Calculate final summary
                        present = len([s for s in activeSession["attendance"].values() if s == "present"])
                        absent = len([s for s in activeSession["attendance"].values() if s == "absent"])
                        total = present + absent

                        # Broadcast to all clients
                        await broadcast_message({
                            "event": "DONE",
                            "data": {
                                "message": "Attendance persisted",
                                "present": present,
                                "absent": absent,
                                "total": total
                            }
                        })

                        # Clear active session
                        activeSession = None

        except WebSocketDisconnect:
            active_connections.remove(websocket)
        except Exception as e:
            print(f"WebSocket error: {e}")
            if websocket in active_connections:
                active_connections.remove(websocket)

    except jwt.ExpiredSignatureError:
        await send_error(websocket, "Unauthorized or invalid token")
        await websocket.close()
    except jwt.InvalidTokenError:
        await send_error(websocket, "Unauthorized or invalid token")
        await websocket.close()


