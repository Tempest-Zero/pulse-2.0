# Backend API Reference

## Base URL
- **Local**: `http://localhost:8000`
- **Production**: `https://back-end-304.up.railway.app`

## Health Check
```
GET /health
Response: {"status": "healthy", "database": "connected"}
```

## Authentication Endpoints

### Signup
```
POST /auth/signup
Body: {"email": "user@example.com", "username": "user", "password": "secret"}
Response: {"access_token": "...", "token_type": "bearer", "user": {...}}
```

### Login
```
POST /auth/login
Body: {"email": "user@example.com", "password": "secret"}
Response: {"access_token": "...", "token_type": "bearer", "user": {...}}
```

### Get Current User
```
GET /auth/me
Headers: Authorization: Bearer <token>
Response: {"id": 1, "email": "...", "username": "..."}
```

## Tasks Endpoints

### List Tasks
```
GET /tasks
Headers: Authorization: Bearer <token>
Response: [{"id": 1, "title": "...", ...}]
```

### Create Task
```
POST /tasks
Headers: Authorization: Bearer <token>
Body: {"title": "...", "description": "...", "priority": 3}
Response: {"id": 1, ...}
```

## AI Endpoints

### Get Recommendation
```
GET /ai/recommendation
Headers: Authorization: Bearer <token>
Response: {
    "action_type": "DEEP_FOCUS",
    "task": {...},
    "explanation": "...",
    "suggested_duration": 90,
    "confidence": 0.85
}
```

### Submit Feedback
```
POST /ai/feedback
Headers: Authorization: Bearer <token>
Body: {"recommendation_id": 1, "outcome": "completed", "rating": 5}
Response: {"status": "recorded", "reward": 1.2}
```

### Get Agent Stats
```
GET /ai/stats
Response: {
    "total_recommendations": 150,
    "phase": "learned",
    "exploration_rate": 0.05
}
```

## Schedule Endpoints

### List Blocks
```
GET /schedule
Query: ?date=2024-01-15
Response: [{"id": 1, "title": "...", "start": "...", ...}]
```

## Extension Endpoints

### Sync Data
```
POST /api/v1/extension/sync
Headers: Authorization: Bearer <token>, X-Extension-Version: 1.0.0
Body: {"sessions": [...], "timestamp": 1234567890}
Response: {"synced": 5}
```
