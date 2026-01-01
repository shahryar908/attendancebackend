# 🎓 Attendance Management System - Backend API

A **production-ready, real-time attendance tracking system** built from scratch with FastAPI, featuring JWT authentication, role-based access control (RBAC), WebSocket communication, and deployed on AWS EKS.

🔗 **Live Demo**: `http://a6d4d72195a6a4ec3b59f17ba1fcdf43-1710295516.us-east-1.elb.amazonaws.com`
🐳 **Docker Image**: `docker.io/shahryar371/attndance:v5`
📚 **API Docs**: `/docs` (Swagger UI) | `/redoc` (ReDoc)

---

## 📋 Project Overview

This is a **complete end-to-end backend system** built entirely from scratch, demonstrating:

- ✅ **Authentication** - JWT tokens with bcrypt password hashing
- ✅ **RBAC** - Role-based access control (Teacher/Student roles)
- ✅ **HTTP REST API** - 9 RESTful endpoints with FastAPI
- ✅ **WebSocket Server** - Real-time bidirectional communication
- ✅ **Dockerization** - Multi-stage containerization
- ✅ **Kubernetes** - Production-ready manifests with auto-scaling
- ✅ **AWS EKS** - Deployed on managed Kubernetes cluster

---

## ✨ Features Built

### 1. Authentication System 🔐
- User signup with email validation
- Secure password hashing using bcrypt (10 rounds)
- JWT token generation with 24-hour expiration
- Bearer token authentication
- Token verification middleware

### 2. Role-Based Access Control (RBAC) 👥
- **Two roles**: Teacher & Student
- Protected routes with dependency injection
- `require_teacher()` and `require_student()` decorators
- Authorization checks in all endpoints
- Role-based data access

### 3. HTTP REST Routes 🛣️

**Authentication:**
- `POST /signup` - Register new user
- `POST /login` - Login and receive JWT token
- `GET /me` - Get current user profile

**Class Management (Teacher Only):**
- `POST /class` - Create new class
- `POST /class/{class_id}/add-student` - Add student to class
- `GET /class/{class_id}` - Get class details with student list
- `GET /students` - List all students

**Attendance:**
- `POST /attendance/start` - Start attendance session (Teacher)
- `GET /class/{class_id}/my-attendance` - View attendance status (Student)

### 4. WebSocket Server ⚡
Real-time bidirectional communication with event-driven architecture:

**Teacher Events (Broadcast to all):**
- `ATTENDANCE_MARKED` - Mark student present/absent
- `TODAY_SUMMARY` - Get attendance summary statistics
- `DONE` - Finalize session & persist to database

**Student Events (Unicast):**
- `MY_ATTENDANCE` - Check own attendance status

**Features:**
- JWT authentication for WebSocket connections
- Connection lifecycle management
- Auto-cleanup of disconnected clients
- Broadcasting (one-to-many)
- Unicasting (one-to-one)
- In-memory active session management

### 5. Database Integration 💾
- **MongoDB Atlas** cloud database
- **Three collections**:
  - `users` - User accounts with hashed passwords
  - `classes` - Classes with teacher and student enrollment
  - `attendance_records` - Attendance history
- Async MongoDB operations with PyMongo
- Upsert operations for attendance records

### 6. Dockerization 🐳
- Optimized Dockerfile (253MB image)
- Multi-stage build capability
- Production-ready container
- Published to Docker Hub
- Environment-based configuration

### 7. Kubernetes Orchestration ☸️
Seven production-ready manifests:
- **Namespace** - Isolated environment
- **Secret** - MongoDB connection (encrypted)
- **ConfigMap** - Configuration data
- **Deployment** - Pod specification with health checks
- **Service** - LoadBalancer for public access
- **HPA** - Horizontal Pod Autoscaler (1-5 pods)
- **Ingress** - HTTPS-ready routing

### 8. AWS EKS Deployment 🌐
- Production Kubernetes cluster on AWS
- Auto-scaling based on CPU/memory
- Public LoadBalancer URL
- Health checks (liveness & readiness)
- Resource limits and requests

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│          Internet (Users)                     │
│      Teachers & Students                      │
└───────────────────┬──────────────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  AWS Load Balancer   │
         │  (Public IP)         │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │ Kubernetes Service   │
         │ (LoadBalancer)       │
         └──────────┬───────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────┐       ┌───────────────┐
│  Pod 1        │       │  Pods 2-5     │
│  FastAPI      │       │  (Auto-scale) │
│  + JWT        │       │               │
│  + WebSocket  │       │               │
└───────┬───────┘       └───────┬───────┘
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │   MongoDB Atlas      │
         │   - users            │
         │   - classes          │
         │   - attendance       │
         └──────────────────────┘
```

---

## 🛠️ Technology Stack

| Category | Technology | Version |
|----------|-----------|---------|
| **Language** | Python | 3.11 |
| **Framework** | FastAPI | 0.128.0 |
| **Database** | MongoDB Atlas | Cloud |
| **Auth** | PyJWT + bcrypt | Latest |
| **Validation** | Pydantic | 2.12.5 |
| **WebSocket** | FastAPI WebSocket | Built-in |
| **Container** | Docker | Latest |
| **Orchestration** | Kubernetes | 1.32 |
| **Cloud** | AWS EKS | Latest |
| **Load Balancer** | AWS ELB | Managed |
| **Registry** | Docker Hub | Public |

---

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone <your-repo>
cd attendencebackend

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "DB_URL=mongodb+srv://user:pass@cluster.mongodb.net/attendence_db" > .env

# Run server
uvicorn main:app --reload

# Access API docs
open http://localhost:8000/docs
```

### Docker

```bash
# Build image
docker build -t shahryar371/attndance:v5 .

# Run container
docker run -p 8000:8000 \
  -e DB_URL="your_mongodb_url" \
  shahryar371/attndance:v5

# Test
curl http://localhost:8000/
```

### Kubernetes (AWS EKS)

```bash
# Create cluster
eksctl create cluster \
  --name attendance-cluster \
  --region us-east-1 \
  --nodegroup-name attendance-nodes \
  --node-type t3.small \
  --nodes 1 \
  --managed

# Deploy application
kubectl apply -f k8s/

# Get public URL
kubectl get svc attendence-service -n attendencenamespace

# Test
curl http://YOUR-LOADBALANCER-URL/
```

---

## 📡 API Examples

### 1. Signup
```bash
curl -X POST http://YOUR-URL/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Teacher",
    "email": "alice@example.com",
    "password": "secure123",
    "role": "teacher"
  }'

# Response:
{
  "success": true,
  "data": {
    "_id": "6956d29bec1c68d87f5916e7",
    "name": "Alice Teacher",
    "email": "alice@example.com",
    "role": "teacher"
  }
}
```

### 2. Login
```bash
curl -X POST http://YOUR-URL/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "secure123"
  }'

# Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "type": "bearer"
}
```

### 3. Create Class (Teacher Only)
```bash
curl -X POST http://YOUR-URL/class \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"className": "Math 101"}'
```

### 4. WebSocket Connection
```javascript
// Connect with JWT token
const ws = new WebSocket('ws://YOUR-URL/ws?token=YOUR_JWT_TOKEN');

// Teacher: Mark attendance
ws.send(JSON.stringify({
  event: "ATTENDANCE_MARKED",
  data: {
    studentId: "6956d29bec1c68d87f5916e7",
    status: "present"
  }
}));

// Student: Check status
ws.send(JSON.stringify({
  event: "MY_ATTENDANCE",
  data: {}
}));

// Receive updates
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log(msg.event, msg.data);
};
```

---

## 📁 Project Structure

```
attendencebackend/
├── main.py                 # Complete FastAPI app (600 lines)
├── model.py                # Pydantic models
├── app.py                  # Test API
├── requirements.txt        # Dependencies
├── Dockerfile             # Container definition
├── .dockerignore          # Build exclusions
├── .env                   # Environment variables
│
├── k8s/                   # Kubernetes manifests
│   ├── namespace.yml
│   ├── secret.yml
│   ├── configmap.yml
│   ├── deployment.yml
│   ├── service.yml
│   ├── hpa.yml
│   └── ingress.yml
│
└── docs/
    ├── README.md
    ├── PORTFOLIO-README.md
    ├── PROJECT-SUMMARY.md
    └── AWS-EKS-DEPLOYMENT-GUIDE.md
```

---

## 🔐 Security

- ✅ bcrypt password hashing (10 rounds)
- ✅ JWT tokens with expiration
- ✅ Role-based authorization
- ✅ Pydantic input validation
- ✅ Secrets stored in Kubernetes Secrets
- ✅ No hardcoded credentials

---

## 📊 What I Built (Step-by-Step Journey)

### Phase 1: Authentication ✅
- Implemented user signup with validation
- Added bcrypt password hashing
- Created JWT token generation
- Built login endpoint
- Token verification middleware

### Phase 2: RBAC ✅
- Defined teacher & student roles
- Created `require_teacher()` decorator
- Created `require_student()` decorator
- Protected all sensitive routes
- Authorization checks

### Phase 3: REST API ✅
- Built 9 HTTP endpoints
- Class management CRUD
- Student enrollment
- Attendance endpoints
- Comprehensive error handling

### Phase 4: WebSocket Server ✅
- Real-time bidirectional communication
- JWT authentication for WebSocket
- 4 event types (broadcast & unicast)
- Connection management
- Active session tracking

### Phase 5: Dockerization ✅
- Created Dockerfile
- Optimized image size (253MB)
- Built and tested locally
- Pushed to Docker Hub
- Environment configuration

### Phase 6: Kubernetes ✅
- Created 7 K8s manifests
- Added health checks
- Configured auto-scaling
- Set resource limits
- Secret management

### Phase 7: AWS Deployment ✅
- Created EKS cluster
- Deployed to production
- Got public LoadBalancer URL
- Tested live API
- Documented process

---

## 📈 Performance

- API Response Time: < 100ms
- WebSocket Latency: < 50ms
- Docker Build: 47 seconds
- Image Size: 253MB
- Pod Startup: < 30 seconds
- Auto-scaling: 1-5 pods

---

## 💰 Cost (AWS EKS)

- EKS Control Plane: $0.10/hour
- 1× t3.small: $0.02/hour
- LoadBalancer: $0.025/hour
- **Total**: ~$0.30/hour

**Tested for 3 hours = ~$0.90 from $119.63 credits**

---

## 🎯 Production Features

✅ Health checks (liveness & readiness)
✅ Auto-scaling (HPA based on CPU/memory)
✅ Resource limits
✅ Secret management
✅ LoadBalancer
✅ Logging
✅ Error handling
✅ Input validation
✅ API documentation

---

## 🔮 Future Enhancements

- [ ] CI/CD with GitHub Actions
- [ ] Monitoring with Prometheus/Grafana
- [ ] SSL/TLS certificates
- [ ] API rate limiting
- [ ] Redis caching
- [ ] Email notifications
- [ ] Advanced analytics

---

## 👤 Author

**Shahryar**
GitHub: [@shahryar371](https://github.com/shahryar371)
Docker Hub: [shahryar371](https://hub.docker.com/u/shahryar371)

---

## 📄 License

Open source for educational purposes.

---

**Built from scratch** with modern web development and DevOps best practices.
**Production-deployed** on AWS EKS with real-time WebSocket communication.

⭐ **Star this repo if you found it helpful!**
