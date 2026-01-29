# API Usage Examples

This file contains practical examples for using the authentication API from different frontend frameworks.

## Frontend Environment Setup

### React (.env)
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_KEY=sk_your_api_key_from_create_api_client_command
REACT_APP_CLIENT_ID=550e8400-e29b-41d4-a716-446655440000
```

### Vue (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=sk_your_api_key_from_create_api_client_command
VITE_CLIENT_ID=550e8400-e29b-41d4-a716-446655440000
```

### Angular (environment.ts)
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',
  apiKey: 'sk_your_api_key_from_create_api_client_command',
  clientId: '550e8400-e29b-41d4-a716-446655440000'
};
```

---

## CURL Examples

### 1. Register Creator

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "johndoe",
    "password": "SecurePassword123!",
    "password2": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "john@example.com",
    "username": "johndoe",
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

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePassword123!"
  }'
```

### 3. Get Profile

```bash
curl -X GET http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "X-API-Key: sk_your_api_key"
```

### 4. Update Profile

```bash
curl -X PATCH http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith"
  }'
```

### 5. Refresh Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

### 6. Change Password

```bash
curl -X POST http://localhost:8000/api/v1/auth/change-password/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePassword123!",
    "new_password": "NewPassword456!",
    "new_password2": "NewPassword456!"
  }'
```

### 7. Logout

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

---

## React Implementation

### Authentication Service

```javascript
// services/authService.js

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;
const API_KEY = process.env.REACT_APP_API_KEY;
const CLIENT_ID = process.env.REACT_APP_CLIENT_ID;

const api = axios.create({
  baseURL: `${API_URL}/api/auth`,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
    'X-Client-ID': CLIENT_ID,
  }
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_URL}/api/v1/auth/token/refresh/`, {
          refresh: refreshToken
        });
        localStorage.setItem('access_token', response.data.access);
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return api(originalRequest);
      } catch (err) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(err);
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  register: (data) => api.post('/register/', data),
  login: (email, password) => 
    api.post('/token/', { email, password }),
  getProfile: () => api.get('/profile/'),
  updateProfile: (data) => api.patch('/profile/', data),
  changePassword: (oldPassword, newPassword) =>
    api.post('/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
      new_password2: newPassword,
    }),
  logout: () => {
    const refreshToken = localStorage.getItem('refresh_token');
    return api.post('/logout/', { refresh: refreshToken });
  },
  refreshToken: () => {
    const refreshToken = localStorage.getItem('refresh_token');
    return api.post('/token/refresh/', { refresh: refreshToken });
  }
};

export default api;
```

### Register Component

```jsx
// components/Register.jsx

import React, { useState } from 'react';
import { authService } from '../services/authService';
import { useNavigate } from 'react-router-dom';

function Register() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: '',
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await authService.register(formData);
      const { access, refresh, user } = response.data;

      // Store tokens
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user', JSON.stringify(user));

      navigate('/dashboard');
    } catch (err) {
      setError(
        err.response?.data?.email?.[0] ||
        err.response?.data?.username?.[0] ||
        'Registration failed'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      
      <input
        type="text"
        name="first_name"
        placeholder="First Name"
        value={formData.first_name}
        onChange={handleChange}
      />
      
      <input
        type="text"
        name="last_name"
        placeholder="Last Name"
        value={formData.last_name}
        onChange={handleChange}
      />
      
      <input
        type="email"
        name="email"
        placeholder="Email"
        value={formData.email}
        onChange={handleChange}
        required
      />
      
      <input
        type="text"
        name="username"
        placeholder="Username"
        value={formData.username}
        onChange={handleChange}
        required
      />
      
      <input
        type="password"
        name="password"
        placeholder="Password"
        value={formData.password}
        onChange={handleChange}
        required
      />
      
      <input
        type="password"
        name="password2"
        placeholder="Confirm Password"
        value={formData.password2}
        onChange={handleChange}
        required
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Registering...' : 'Register'}
      </button>
    </form>
  );
}

export default Register;
```

### Login Component

```jsx
// components/Login.jsx

import React, { useState } from 'react';
import { authService } from '../services/authService';
import { useNavigate } from 'react-router-dom';

function Login() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await authService.login(
        formData.email,
        formData.password
      );
      const { access, refresh } = response.data;

      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);

      navigate('/dashboard');
    } catch (err) {
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      
      <input
        type="email"
        name="email"
        placeholder="Email"
        value={formData.email}
        onChange={handleChange}
        required
      />
      
      <input
        type="password"
        name="password"
        placeholder="Password"
        value={formData.password}
        onChange={handleChange}
        required
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}

export default Login;
```

### Protected Route

```jsx
// components/ProtectedRoute.jsx

import React from 'react';
import { Navigate } from 'react-router-dom';

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    return <Navigate to="/login" />;
  }

  return children;
}

export default ProtectedRoute;
```

---

---

## Testing with Postman

1. **Create Environment Variables**:
   - `api_url`: http://localhost:8000
   - `access_token`: (empty, will be filled)
   - `refresh_token`: (empty, will be filled)

2. **Register Request**:
   - Method: POST
   - URL: `{{api_url}}/api/v1/auth/register/`
   - Body:
     ```json
     {
       "email": "test@example.com",
       "username": "testuser",
       "password": "Test123!",
       "password2": "Test123!",
       "first_name": "Test",
       "last_name": "User"
     }
     ```
   - Pre-request Script: (none)
   - Tests:
     ```javascript
     pm.environment.set("access_token", pm.response.json().access);
     pm.environment.set("refresh_token", pm.response.json().refresh);
     ```

3. **Login Request**:
   - Method: POST
   - URL: `{{api_url}}/api/v1/auth/token/`
   - Body:
     ```json
     {
       "email": "test@example.com",
       "password": "Test123!"
     }
     ```

4. **Get Profile Request**:
   - Method: GET
   - URL: `{{api_url}}/api/v1/auth/profile/`
   - Headers:
     - Authorization: `Bearer {{access_token}}`
     - X-API-Key: `sk_your_api_key`

---

## Common Issues & Solutions

### Issue: "Invalid API Key"
**Solution**: 
- Create API client: `python manage.py create_api_client --name "My App" --type web`
- Use the returned API key in the `X-API-Key` header

### Issue: "Token has expired"
**Solution**: 
- Use refresh token endpoint to get new access token
- Implement auto-refresh in your API interceptor

### Issue: CORS errors
**Solution**: 
- Add frontend URL to `CORS_ALLOWED_ORIGINS` in `.env`
- Restart Django server

### Issue: "User type cannot be changed"
**Solution**: 
- `user_type` is read-only in serializers
- Change via Django admin if needed for staff/admin promotion
