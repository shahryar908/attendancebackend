# 📚 Live Attendance System - Backend

Real-time attendance tracking system with WebSocket support, JWT authentication, and role-based access control.

## 🎯 Features

- ✅ User Authentication (JWT with 1-day expiration)
- ✅ Role-based Access Control (Teacher/Student)
- ✅ Class Management CRUD
- ✅ Real-time Attendance via WebSocket
- ✅ MongoDB Persistence
- ✅ Docker Support
- ✅ Production-Ready

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB
- **Authentication**: JWT + bcrypt
- **Real-time**: WebSocket
- **Containerization**: Docker (Multi-stage build)
- **Package Manager**: uv

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose
- MongoDB Atlas account (or local MongoDB)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <your-repo>
cd attendencebackend

# Create .env file
echo "DB_URL=your_mongodb_connection_string" > .env

# Build and run
docker-compose up --build

# Server runs on http://localhost:8000
```

### Option 2: Local Development

```bash
# Install dependencies
pip install uv
uv sync

# Create .env file
echo "DB_URL=your_mongodb_connection_string" > .env

# Run server
uv run uvicorn main:app --reload --port 8000
```

## 📡 API Endpoints

### Authentication
- `POST /signup` - Register new user
- `POST /login` - Login and get JWT token
- `GET /me` - Get current user info

### Class Management
- `POST /class` - Create class (Teacher only)
- `POST /class/{id}/add-student` - Add student to class
- `GET /class/{id}` - Get class details
- `GET /students` - List all students (Teacher only)

### Attendance
- `POST /attendance/start` - Start attendance session
- `GET /class/{id}/my-attendance` - Check persisted attendance

### WebSocket
- `ws://localhost:8000/ws?token=<JWT>` - Real-time attendance updates

## 🔌 WebSocket Events

### Teacher Events (Broadcast)
```json
// Mark Attendance
{"event": "ATTENDANCE_MARKED", "data": {"studentId": "123", "status": "present"}}

// Get Summary
{"event": "TODAY_SUMMARY"}

// Finalize & Persist
{"event": "DONE"}
```

### Student Events (Unicast)
```json
// Check Status
{"event": "MY_ATTENDANCE"}
```

## 🐳 Docker Commands

```bash
# Build image
docker build -t attendance-backend .

# Run container
docker run -p 8000:8000 --env-file .env attendance-backend

# Using docker-compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## 📊 Database Models

### User
```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string",
  "password": "hashed_string",
  "role": "teacher | student"
}
```

### Class
```json
{
  "_id": "ObjectId",
  "className": "string",
  "teacherId": "ObjectId",
  "studentIds": ["ObjectId"]
}
```

### Attendance
```json
{
  "_id": "ObjectId",
  "classId": "ObjectId",
  "studentId": "ObjectId",
  "status": "present | absent"
}
```

## 🔒 Security

- Passwords hashed with bcrypt
- JWT tokens with expiration
- Role-based authorization
- Input validation with Pydantic

## 📝 Environment Variables

```env
DB_URL=mongodb+srv://user:pass@cluster.mongodb.net/dbname
```

## 🧪 Testing with Swagger

Visit `http://localhost:8000/docs` for interactive API documentation.

## 📈 Production Deployment

### Deploy to Render/Railway/Heroku

1. Connect GitHub repository
2. Add environment variable: `DB_URL`
3. Deploy automatically

### Manual Deployment

```bash
# Build production image
docker build -t attendance-backend:prod .

# Push to registry
docker tag attendance-backend:prod your-registry/attendance-backend:prod
docker push your-registry/attendance-backend:prod

# Deploy
docker run -d -p 8000:8000 --env-file .env your-registry/attendance-backend:prod
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📄 License

MIT License

---

**Built with ❤️ using FastAPI and MongoDB**
