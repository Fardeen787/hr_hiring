# FastAPI Authentication System

A complete authentication system built with FastAPI, MySQL, and Firebase integration featuring role-based access control, email verification, and session management.

## Features

- **User Registration & Authentication**
  - Email/password authentication
  - Firebase authentication integration
  - JWT token-based authentication
  - Refresh token mechanism
  - Email verification

- **Password Management**
  - Secure password hashing (bcrypt)
  - Password reset via email
  - Password strength validation

- **Role-Based Access Control**
  - Multiple user roles (User, Admin, HR, Candidate)
  - Permission-based access control
  - Fine-grained permission system

- **Email Integration**
  - Email verification
  - Password reset emails
  - Customizable email templates

- **Session Management**
  - Database-stored refresh tokens
  - Session tracking with IP and user agent
  - Logout functionality

- **Admin Dashboard**
  - User management
  - Role and permission management
  - Dashboard statistics

## Setup Instructions

### 1. Environment Setup

The application can run with default settings, but for production you should create a `.env` file in the root directory with your actual configuration:

**Option A: Create .env file manually**
```bash
# Copy the template and rename it
copy env_template.txt .env
# Then edit .env with your actual values
```

**Option B: Use default settings (for development)**
The application will use default values defined in `app/config.py`. You can modify them directly for development or create a `.env` file to override them.

**Environment Variables:**
```env
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# MySQL Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=Khan@123
MYSQL_DATABASE=auth_database

# Firebase (optional)
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False

# Redis (optional, for session management)
REDIS_URL=redis://localhost:6379

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### 2. Database Setup

Create a MySQL database:

```sql
CREATE DATABASE auth_database;
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Migrations (Optional)

If you want to use Alembic for database migrations:

```bash
# Initialize Alembic
alembic init alembic

# Create first migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 5. Firebase Setup (Optional)

1. Create a Firebase project
2. Generate a service account key
3. Save it as `firebase-credentials.json` in the project root
4. Update the `FIREBASE_CREDENTIALS_PATH` in your `.env` file

### 6. Run the Application

You have several options to run the application:

**Option 1: Using the run.py script (Recommended)**
```bash
python run.py
```

**Option 2: Using uvicorn directly**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option 3: From the app directory**
```bash
python app/main.py
```

**Option 4: Using Python module execution**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/firebase-login` - Firebase authentication
- `GET /api/auth/verify-email/{token}` - Email verification
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout

### User Management
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update user profile
- `PUT /api/users/change-password` - Change password
- `DELETE /api/users/me` - Delete user account

### Admin
- `GET /api/admin/users` - Get all users (Admin/HR only)
- `GET /api/admin/users/{user_id}` - Get specific user
- `PUT /api/admin/users/{user_id}/role` - Update user role
- `PUT /api/admin/users/{user_id}/permissions` - Update user permissions
- `PUT /api/admin/users/{user_id}/status` - Toggle user status
- `DELETE /api/admin/users/{user_id}` - Delete user
- `GET /api/admin/dashboard/stats` - Dashboard statistics
- `GET /api/admin/permissions` - Get all permissions

## User Roles

- **User**: Basic user with read permissions
- **HR**: Can manage users and has read/write permissions
- **Admin**: Full access to all features and permissions
- **Candidate**: Similar to user, intended for job applicants

## Permissions

- **read**: Can read data
- **write**: Can write data
- **delete**: Can delete data
- **manage_users**: Can manage users
- **manage_roles**: Can manage roles

## Security Features

- Password hashing with bcrypt
- JWT tokens with expiration
- Refresh token rotation
- Email verification required
- Rate limiting ready (implement as needed)
- CORS configuration
- SQL injection protection via SQLAlchemy ORM

## Database Schema

The system uses the following main tables:
- `users` - User accounts and profile information
- `permissions` - Available permissions
- `user_permissions` - Many-to-many relationship between users and permissions
- `user_sessions` - Active user sessions with refresh tokens

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
