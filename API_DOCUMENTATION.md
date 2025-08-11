# FastAPI Authentication API Documentation

## 🌐 Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-deployed-api.com`

## 📋 Authentication Overview

This API uses **JWT (JSON Web Tokens)** for authentication. Include the token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🔐 Authentication Endpoints

### 1. User Registration
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+1234567890",
  "password": "SecurePass123",
  "role": "user"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. User Login
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=SecurePass123
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Firebase Google Sign-In
```http
POST /api/auth/firebase-login
Content-Type: application/json

{
  "id_token": "firebase-id-token-from-frontend"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 4. Refresh Token
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "your-refresh-token"
}
```

### 5. Logout
```http
POST /api/auth/logout
Authorization: Bearer your-access-token
```

### 6. Password Reset Request
```http
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### 7. Password Reset
```http
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePass123"
}
```

### 8. Email Verification
```http
GET /api/auth/verify-email/{token}
```

## 👤 User Management Endpoints

### 1. Get Current User Profile
```http
GET /api/users/me
Authorization: Bearer your-access-token
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+1234567890",
  "role": "user",
  "is_active": true,
  "is_email_verified": true,
  "created_at": "2025-08-11T07:53:26",
  "last_login": "2025-08-11T09:34:18",
  "permissions": ["read"]
}
```

### 2. Update User Profile
```http
PUT /api/users/me
Authorization: Bearer your-access-token
Content-Type: application/json

{
  "name": "John Smith",
  "phone": "+1987654321"
}
```

### 3. Change Password
```http
PUT /api/users/change-password
Authorization: Bearer your-access-token
Content-Type: application/json

{
  "current_password": "OldPassword123",
  "new_password": "NewPassword123"
}
```

### 4. Delete Account
```http
DELETE /api/users/me
Authorization: Bearer your-access-token
```

## 👨‍💼 Admin Endpoints (Admin/HR Only)

### 1. Get All Users
```http
GET /api/admin/users?skip=0&limit=100
Authorization: Bearer admin-access-token
```

### 2. Get Specific User
```http
GET /api/admin/users/{user_id}
Authorization: Bearer admin-access-token
```

### 3. Update User Role
```http
PUT /api/admin/users/{user_id}/role
Authorization: Bearer admin-access-token
Content-Type: application/json

{
  "role": "admin"
}
```

### 4. Update User Permissions
```http
PUT /api/admin/users/{user_id}/permissions
Authorization: Bearer admin-access-token
Content-Type: application/json

["read", "write", "manage_users"]
```

### 5. Toggle User Status
```http
PUT /api/admin/users/{user_id}/status
Authorization: Bearer admin-access-token
Content-Type: application/json

{
  "is_active": false
}
```

### 6. Delete User
```http
DELETE /api/admin/users/{user_id}
Authorization: Bearer admin-access-token
```

### 7. Dashboard Statistics
```http
GET /api/admin/dashboard/stats
Authorization: Bearer admin-access-token
```

**Response:**
```json
{
  "total_users": 150,
  "verified_users": 120,
  "active_users": 140,
  "users_by_role": {
    "user": 130,
    "admin": 10,
    "hr": 8,
    "candidate": 2
  },
  "recent_registrations": 15
}
```

### 8. Get All Permissions
```http
GET /api/admin/permissions
Authorization: Bearer admin-access-token
```

## 🔒 User Roles & Permissions

### Roles:
- **user**: Basic user with read permissions
- **hr**: Can manage users, has read/write permissions
- **admin**: Full access to all features and permissions
- **candidate**: Similar to user, intended for job applicants

### Permissions:
- **read**: Can read data
- **write**: Can write data
- **delete**: Can delete data
- **manage_users**: Can manage users
- **manage_roles**: Can manage roles

## 🌐 CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000` (development)
- Your production frontend domain

## 📱 Interactive API Documentation

Visit these URLs when your API is running:
- **Swagger UI**: `{base_url}/docs`
- **ReDoc**: `{base_url}/redoc`

## 🔥 Firebase Integration

### Frontend Setup (React Example):

```javascript
// firebase.js
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyDGcGLNQZpsgDOP7wVLibK7a_9OsXehEKI",
  authDomain: "login-signup-auth-8e3e0.firebaseapp.com",
  projectId: "login-signup-auth-8e3e0",
  storageBucket: "login-signup-auth-8e3e0.firebasestorage.app",
  messagingSenderId: "344732054033",
  appId: "1:344732054033:web:9126babe559ccc127637b0",
  measurementId: "G-TTLS9PTZZE"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();

// Google Sign-In Function
export const signInWithGoogle = async () => {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const idToken = await result.user.getIdToken();
    
    // Send to your API
    const response = await fetch('YOUR_API_URL/api/auth/firebase-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_token: idToken })
    });
    
    const data = await response.json();
    return data; // Contains access_token and refresh_token
  } catch (error) {
    console.error('Firebase sign-in error:', error);
    throw error;
  }
};
```

## ⚠️ Error Responses

### Common Error Codes:
- **400**: Bad Request (invalid data)
- **401**: Unauthorized (invalid/missing token)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **422**: Validation Error

### Error Response Format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## 🧪 Testing

### Test User Credentials:
- **Email**: `fardeen@gmail.com`
- **Password**: `Khan@123`
- **Role**: `user`

### Example API Test:
```bash
# Test login
curl -X POST "YOUR_API_URL/api/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=fardeen@gmail.com&password=Khan@123"
```

## 📞 Support

For any integration questions or issues, contact the backend team.
