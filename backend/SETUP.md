# Setup Guide - Multi-Frontend JWT Authentication

This guide walks you through setting up the new multi-frontend JWT authentication system.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Create Database Migrations

```bash
python manage.py makemigrations customauth creators
python manage.py migrate
```

## Step 3: Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

This creates an admin user who can access the admin dashboard.

## Step 4: Create API Clients

Create an API client for your frontend application(s):

```bash
# Creator Frontend Application
python manage.py create_api_client \
  --name "Creator Web App" \
  --type web \
  --description "Main creator application" \
  --rate-limit 1000

# Admin Dashboard Frontend
python manage.py create_api_client \
  --name "Admin Dashboard" \
  --type web \
  --description "Admin management dashboard" \
  --rate-limit 500
```

## Step 5: Configure Environment Variables

Create or update your `.env` file:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-random-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/creator_monetization

# Allowed Hosts
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# CORS - Update with your frontend URLs
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,https://app.example.com
```

## Step 6: Test the API

### Register a New Creator

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "creator@example.com",
    "username": "creator123",
    "password": "SecurePassword123!",
    "password2": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response** (includes tokens):
```json
{
  "user": {
    "id": 2,
    "email": "creator@example.com",
    "username": "creator123",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "creator",
    "is_active": true,
    "date_joined": "2026-01-28T10:00:00Z"
  },
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Login (Obtain Tokens)

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "creator@example.com",
    "password": "SecurePassword123!"
  }'
```

### Get User Profile

```bash
curl -X GET http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-API-Key: sk_your_api_key_here"
```

### Update Profile

```bash
curl -X PATCH http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith"
  }'
```

### Change Password

```bash
curl -X POST http://localhost:8000/api/v1/auth/change-password/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePassword123!",
    "new_password": "NewSecurePassword456!",
    "new_password2": "NewSecurePassword456!"
  }'
```

### Refresh Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

### Logout

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

## Frontend Integration

### React/Vue/Angular Frontend

#### 1. Store tokens securely

```javascript
// After registration/login
const response = await fetch('http://api.example.com/api/v1/auth/token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});

const data = await response.json();
localStorage.setItem('access_token', data.access);
localStorage.setItem('refresh_token', data.refresh);
localStorage.setItem('user_type', data.user.user_type);
```

#### 2. Send tokens in requests

```javascript
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
  'X-API-Key': process.env.REACT_APP_API_KEY,  // From environment
  'X-Client-ID': process.env.REACT_APP_CLIENT_ID  // From environment
};

fetch('http://api.example.com/api/v1/auth/profile/', { headers });
```

#### 3. Handle token expiration

```javascript
async function refreshAccessToken() {
  const response = await fetch('http://api.example.com/api/v1/auth/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: localStorage.getItem('refresh_token') })
  });

  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    return true;
  }
  // Token expired, redirect to login
  return false;
}
```

## Admin Dashboard

1. Navigate to `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Manage users and assign staff/admin roles
4. View and manage API clients
5. Monitor user activity and creator profiles

## User Type Management

### Creating Staff Users

1. Go to Admin Dashboard
2. Users → Add User
3. Set `user_type` to "Staff"
4. Enable `is_staff` checkbox
5. Save

### Creating Admin Users

Use the `createsuperuser` command (already set `is_staff` and `is_superuser`)

### Self-Registered Users (Creators)

- Use `/api/v1/auth/register/` endpoint
- Automatically set as `user_type='creator'`
- Cannot become staff/admin via API

## API Documentation

- Swagger UI: `http://localhost:8000/api/schema/swagger/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`

## Common Issues

### CORS Errors

**Problem**: Frontend getting CORS errors
**Solution**: 
1. Add frontend URL to `CORS_ALLOWED_ORIGINS` in `.env`
2. Restart Django server
3. Ensure `django-cors-headers` is installed

### Token Expired

**Problem**: Getting 401 Unauthorized
**Solution**: 
1. Use refresh token to get new access token
2. Or have user login again

### Invalid API Key

**Problem**: X-API-Key header showing invalid
**Solution**: 
1. Check API key is correct in `.env`
2. Verify client is active in admin dashboard
3. Regenerate key if needed

## Next Steps

1. Read [AUTHENTICATION.md](AUTHENTICATION.md) for detailed architecture info
2. Create custom permission classes for specific endpoints
3. Add creator profile serializers in the creators app
4. Implement additional authentication methods (OAuth, social login)
5. Set up monitoring and analytics per API client
