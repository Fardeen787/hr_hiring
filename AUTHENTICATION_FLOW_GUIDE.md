# 🔐 Complete Authentication Flow Guide

## 🎯 Overview

Your authentication system supports two main flows:
1. **Traditional Email/Password Authentication**
2. **Firebase Google Sign-In Authentication**

Both flows result in JWT tokens that are used for all subsequent API calls.

## 📊 System Architecture

```
Frontend App ↔ FastAPI Backend ↔ MySQL Database
     ↕               ↕
Firebase Auth    JWT Tokens
     ↕
Google OAuth
```

## 🔑 Flow 1: Email/Password Authentication

### Step 1: User Registration (`/api/auth/signup`)

**Frontend Request:**
```javascript
const response = await fetch('API_URL/api/auth/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: "user@example.com",
    name: "John Doe",
    password: "SecurePass123",
    role: "user"
  })
});
```

**Backend Process:**
1. **Validate Input** - Check email format, password strength
2. **Check Duplicates** - Ensure email doesn't exist
3. **Hash Password** - Use bcrypt to hash password
4. **Create User** - Insert into MySQL database
5. **Assign Permissions** - Based on user role
6. **Generate Tokens** - Create JWT access & refresh tokens
7. **Send Email** - Verification email (if configured)
8. **Return Response** - Tokens to frontend

**Database Changes:**
```sql
INSERT INTO users (email, name, hashed_password, role, is_active)
VALUES ('user@example.com', 'John Doe', '$2b$12$...', 'user', true);

INSERT INTO user_sessions (user_id, refresh_token, expires_at)
VALUES (1, 'refresh_token_here', '2025-08-18 10:00:00');
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Step 2: User Login (`/api/auth/login`)

**Frontend Request:**
```javascript
const formData = new FormData();
formData.append('username', 'user@example.com');  // OAuth2 standard
formData.append('password', 'SecurePass123');

const response = await fetch('API_URL/api/auth/login', {
  method: 'POST',
  body: formData
});
```

**Backend Process:**
1. **Find User** - Query database by email
2. **Verify Password** - Compare with hashed password
3. **Check Account Status** - Ensure user is active
4. **Update Login Time** - Record last_login timestamp
5. **Generate Tokens** - New JWT access & refresh tokens
6. **Store Session** - Save refresh token in database
7. **Return Tokens** - Send to frontend

**Database Changes:**
```sql
UPDATE users SET last_login = NOW() WHERE email = 'user@example.com';

INSERT INTO user_sessions (user_id, refresh_token, expires_at, ip_address)
VALUES (1, 'new_refresh_token', '2025-08-18 10:00:00', '192.168.1.1');
```

## 🔥 Flow 2: Firebase Google Sign-In

### Step 1: Frontend Google Authentication

**Frontend Process:**
```javascript
import { signInWithPopup, GoogleAuthProvider } from 'firebase/auth';

// User clicks "Sign in with Google"
const result = await signInWithPopup(auth, googleProvider);
const idToken = await result.user.getIdToken();

// Send Firebase ID token to backend
const response = await fetch('API_URL/api/auth/firebase-login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ id_token: idToken })
});
```

**What Happens:**
1. **Google OAuth Popup** - User signs in with Google
2. **Firebase Handles Auth** - Validates with Google
3. **ID Token Generated** - Firebase creates secure token
4. **Token Contains** - User email, name, Google UID

### Step 2: Backend Firebase Verification (`/api/auth/firebase-login`)

**Backend Process:**
1. **Verify Firebase Token** - Using Firebase Admin SDK
2. **Extract User Data** - Email, name, Firebase UID from token
3. **Find or Create User** - Check if user exists in database
4. **Update Firebase UID** - Link Firebase account to database user
5. **Generate JWT Tokens** - Standard access & refresh tokens
6. **Return Response** - Same format as email/password login

**Database Changes:**
```sql
-- If new user
INSERT INTO users (email, name, firebase_uid, role, is_active, is_email_verified)
VALUES ('user@gmail.com', 'John Doe', 'firebase_uid_123', 'user', true, true);

-- If existing user
UPDATE users SET firebase_uid = 'firebase_uid_123', last_login = NOW()
WHERE email = 'user@gmail.com';
```

## 🛡️ Protected API Calls

### Making Authenticated Requests

**Frontend Implementation:**
```javascript
// Store tokens after login
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);

// Make protected API calls
const token = localStorage.getItem('access_token');
const response = await fetch('API_URL/api/users/me', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

**Backend JWT Verification Process:**
1. **Extract Token** - From Authorization header
2. **Verify Signature** - Using secret key
3. **Check Expiration** - Ensure token is not expired
4. **Extract Payload** - Get user email, role, permissions
5. **Find User** - Query database by email
6. **Check Status** - Ensure user is still active
7. **Return User Object** - For use in endpoint logic

**JWT Token Structure:**
```json
{
  "sub": "user@example.com",     // User email
  "role": "user",                // User role
  "user_id": 1,                  // Database user ID
  "exp": 1692624000,             // Expiration timestamp
  "type": "access"               // Token type
}
```

## 🔄 Token Refresh Flow

### When Access Token Expires

**Frontend Automatic Refresh:**
```javascript
// API call interceptor
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      
      try {
        const response = await fetch('API_URL/api/auth/refresh', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken })
        });
        
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        
        // Retry original request
        error.config.headers.Authorization = `Bearer ${data.access_token}`;
        return axios.request(error.config);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        window.location.href = '/login';
      }
    }
  }
);
```

**Backend Refresh Process:**
1. **Verify Refresh Token** - Check signature and expiration
2. **Find Session** - Query user_sessions table
3. **Check User Status** - Ensure user is still active
4. **Generate New Access Token** - Fresh token with current user data
5. **Return New Token** - Keep same refresh token

## 👤 User Management Flow

### Getting User Profile (`/api/users/me`)

**Request Flow:**
```
Frontend → Authorization: Bearer token → Backend
         ← User Profile Data ←
```

**Backend Process:**
1. **Verify JWT Token** - Extract user email
2. **Query Database** - Get complete user record
3. **Include Permissions** - Join with user_permissions table
4. **Return Profile** - All user data except sensitive fields

**Response Structure:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "permissions": ["read"],
  "is_active": true,
  "is_email_verified": true,
  "created_at": "2025-08-11T07:53:26",
  "last_login": "2025-08-11T09:34:18"
}
```

## 🔐 Role-Based Access Control

### Permission Checking Flow

**Backend Permission Verification:**
```python
# In app/auth/dependencies.py
def require_permission(required_permissions: List[str]):
    async def permission_checker(current_user: User = Depends(get_current_active_user)):
        user_permissions = [p.name for p in current_user.permissions]
        has_permission = any(perm in user_permissions for perm in required_permissions)
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        return current_user
    return permission_checker
```

**Usage in Endpoints:**
```python
@router.get("/admin/users")
async def get_all_users(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.HR]))
):
    # Only admin and HR users can access this endpoint
```

### Role Hierarchy:
```
admin: All permissions (read, write, delete, manage_users, manage_roles)
hr: Limited management (read, write, manage_users)
user: Basic access (read)
candidate: Basic access (read)
```

## 🚪 Logout Flow

### Frontend Logout Process:
```javascript
const logout = async () => {
  const token = localStorage.getItem('access_token');
  
  // Call backend logout (optional)
  await fetch('API_URL/api/auth/logout', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  // Clear local storage
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  
  // Redirect to login
  window.location.href = '/login';
};
```

**Backend Logout Process:**
1. **Verify Current User** - From JWT token
2. **Delete All Sessions** - Remove all refresh tokens for user
3. **Return Success** - Confirmation message

**Database Changes:**
```sql
DELETE FROM user_sessions WHERE user_id = 1;
```

## 🔄 Complete Authentication Lifecycle

### 1. Initial State (No Authentication)
```
User → Frontend (No tokens) → API Call → 401 Unauthorized → Redirect to Login
```

### 2. Authentication Process
```
Login Form → Backend Verification → JWT Generation → Token Storage → Dashboard Access
```

### 3. Normal Operation
```
API Call → Include Bearer Token → Backend Verification → Return Data → Update UI
```

### 4. Token Expiration
```
API Call → 401 Error → Auto Refresh → New Token → Retry Request → Success
```

### 5. Session End
```
Logout → Clear Tokens → Backend Session Cleanup → Return to Login
```

## 🔍 Security Features

### Password Security:
- **bcrypt hashing** with salt rounds
- **Password validation** (length, complexity)
- **No plain text storage**

### JWT Security:
- **HMAC SHA-256 signing**
- **Short expiration times** (30 minutes for access tokens)
- **Refresh token rotation**
- **Secure token storage**

### Session Security:
- **Database-stored sessions**
- **IP address tracking**
- **User agent logging**
- **Session invalidation on logout**

### Firebase Security:
- **Token verification** using Firebase Admin SDK
- **Google OAuth security**
- **No password storage** for Firebase users

## 🧪 Testing the Flow

### Manual Testing Steps:

1. **Test Registration:**
```bash
curl -X POST "API_URL/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test","password":"Test123"}'
```

2. **Test Login:**
```bash
curl -X POST "API_URL/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=Test123"
```

3. **Test Protected Endpoint:**
```bash
curl -X GET "API_URL/api/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

This comprehensive flow ensures secure, scalable authentication for your application! 🚀
