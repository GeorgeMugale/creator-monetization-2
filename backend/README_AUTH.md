# Multi-Frontend JWT Authentication System

### User Types
```
┌─────────────────────────────────────────────────────────────┐
│  CREATORS                  STAFF            ADMIN/SUPERUSER  │
│  (Self-register)           (Admin-created)  (Admin-created)  │
│  ✓ Public signup           ✓ Can be staff   ✓ Full access    │
│  ✓ Creator app only        ✓ Admin access   ✓ Admin access   │
│  ✗ Cannot be staff         ✗ Not superuser  ✓ Superuser      │
└─────────────────────────────────────────────────────────────┘
```

### 🔑 Authentication Flow
```
User Registration/Login
    ↓
JWT Token Generation (access + refresh)
    ↓
Protected API Endpoints with Authorization
    ↓
Token Refresh when Expired
    ↓
Token Logout & Blacklist
```

### 🌐 Multi-Frontend Architecture
```
API Server (localhost:8000)
    ├── API Client 1 (Creator Web App)
    │   └── X-API-Key: sk_xxx | X-Client-ID: yyy
    ├── API Client 2 (Admin Dashboard)
    │   └── X-API-Key: sk_zzz | X-Client-ID: www
    └── API Client 3 (Mobile App - Future)
        └── X-API-Key: sk_aaa | X-Client-ID: bbb

All clients use standard JWT bearer tokens
Each has isolated rate limits and can be monitored separately
```

---


## 🚀 Quick Start (5 Steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py makemigrations customauth creators
python manage.py migrate

# 3. Create admin user
python manage.py createsuperuser

# 4. Create API clients
python manage.py create_api_client --name "Creator Web App" --type web --rate-limit 1000

# 5. Run server
python manage.py runserver

# Now visit:
# - http://localhost:8000/admin/ (manage users/clients)
# - http://localhost:8000/api/v1/auth/register/ (create creator)
# - http://localhost:8000/api/schema/swagger/ (API docs)
```

---

## 📱 API Endpoints

### Authentication
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/v1/auth/register/` | POST | ❌ | Self-register as creator |
| `/api/v1/auth/token/` | POST | ❌ | Login, get JWT tokens |
| `/api/v1/auth/token/refresh/` | POST | ❌ | Refresh access token |
| `/api/v1/auth/logout/` | POST | ✅ | Logout, blacklist token |

### User Profile
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/v1/auth/profile/` | GET | ✅ | Get current user |
| `/api/v1/auth/profile/` | PATCH | ✅ | Update profile |
| `/api/v1/auth/profile/` | PUT | ✅ | Full update |

### Password
| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/v1/auth/change-password/` | POST | ✅ | Change password |

---

## 💡 Custom Permissions (Ready to Use)

```python
from utils.permissions import IsCreator, IsAdminUser, IsStaffUser

# Only creators can access
class CreatorAPI(APIView):
    permission_classes = [IsAuthenticated, IsCreator]

# Only staff/admins can access  
class AdminAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

# Use in your own APIs
class MyView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]
```

---

## Frontend Integration Examples

The documentation includes working code for:

### React 18
- Auth service with Axios
- Register component
- Login component
- Protected routes
- Token refresh logic

### Vue 3
- Pinia auth store
- Register component
- Token management
- Auth interceptor

### Angular 16+
- Auth service with HttpClient
- JWT interceptor
- Protected guards
- Token refresh

### Plus: CURL, Postman, and raw fetch() examples

---

## 📊 Scalability

### Current Setup (Day 1)
```
1 API Server
├── 1-2 Frontend Apps
├── Admin Dashboard
└── ~100-1000 concurrent users
```


### Architecture Supports
- ✅ Multiple frontends with isolated API keys
- ✅ Per-client rate limiting
- ✅ API versioning without breaking clients
- ✅ Client-specific analytics
- ✅ Easy to add OAuth/social login
- ✅ Ready for GraphQL alongside REST

---

## 📋 What's NOT Yet Implemented (For Future)

- ❌ Social login (Google, Facebook, etc.)
- ❌ Two-factor authentication
- ❌ Email verification/confirmation
- ❌ Password reset flow
- ❌ Webhook support
- ❌ GraphQL endpoint
- ❌ Admin analytics dashboard
- ❌ Audit logging

---

## ✅ Registration vs Login

### Registration (NEW CREATORS)
```
POST /api/v1/auth/register/
{
  "email": "creator@example.com",
  "username": "mycreator",
  "password": "SecurePassword123!",
  "password2": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}

Response:
{
  "user": { "id": 1, "email": "...", "user_type": "creator", ... },
  "access": "eyJ...",  // Use this for API requests
  "refresh": "eyJ..."  // Use this to refresh access token
}

✓ No authentication required (AllowAny)
✓ User is automatically set as "creator" type
✓ Tokens returned immediately
```

### Login (EXISTING USERS)
```
POST /api/v1/auth/token/
{
  "email": "creator@example.com",
  "password": "SecurePassword123!"
}

Response:
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}

✓ Works for creators, staff, and admin
✓ Must provide correct password
✓ Returns only tokens (not user data)
```

---

## 🔄 Token Refresh Flow

```
1. User logs in
   ↓
2. Gets access_token (15 min) + refresh_token (7 days)
   ↓
3. Make API requests with access_token
   ↓
4. If access expires → POST /api/v1/auth/token/refresh/ with refresh_token
   ↓
5. Get new access_token (refresh_token also rotates)
   ↓
6. Continue making requests
   ↓
7. If refresh expires → User must login again
```

**Your frontend should handle this automatically** (see API_EXAMPLES.md for interceptor code)

---

## 🎓 Learning Path

1. **Read**: AUTHENTICATION.md (understand architecture)
2. **Setup**: Follow SETUP.md (get it running)
3. **Test**: Use CURL examples to test endpoints
4. **Integrate**: Follow API_EXAMPLES.md for your frontend

---
