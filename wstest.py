from fastapi import FastAPI,WebSocket,WebSocketDisconnect

app=FastAPI()

@app.websocket("/ws?token")
async def websocket_endpoint(token: str, websocket: WebSocket):
               
    await websocket.accept()
   
    try:
      while True:
        data =await websocket.receive_text()
        print(f"Message text was: {data}")
        await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")

        
        
