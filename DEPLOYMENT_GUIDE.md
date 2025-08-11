# FastAPI Authentication System - Deployment Guide

## 🚀 Quick Deployment Options

### Option 1: Render (Free - Recommended)

1. **Create account**: https://render.com
2. **Connect GitHub**: Link your repository
3. **Create Web Service**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Add Environment Variables**:
   ```
   SECRET_KEY=your-production-secret-key
   MYSQL_HOST=your-mysql-host
   MYSQL_PASSWORD=your-mysql-password
   MYSQL_DATABASE=auth_database
   FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
   ```

### Option 2: Railway (Easy)

1. **Create account**: https://railway.app
2. **Deploy from GitHub**: Connect your repo
3. **Add MySQL database**: One-click MySQL service
4. **Set environment variables** (same as above)

### Option 3: Heroku (Popular)

1. **Create Heroku app**: `heroku create your-app-name`
2. **Add MySQL addon**: `heroku addons:create jawsdb:kitefin`
3. **Set config vars**: `heroku config:set SECRET_KEY=...`
4. **Deploy**: `git push heroku main`

### Option 4: VPS/DigitalOcean

1. **Create droplet** with Ubuntu
2. **Install Python/MySQL**: 
   ```bash
   sudo apt update
   sudo apt install python3-pip mysql-server nginx
   ```
3. **Setup project**:
   ```bash
   git clone your-repo
   pip3 install -r requirements.txt
   ```
4. **Configure Nginx** as reverse proxy

## 🔧 Production Configuration

### Environment Variables (.env for production):
```env
SECRET_KEY=your-super-secret-production-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Production MySQL Database
MYSQL_HOST=your-production-mysql-host
MYSQL_PORT=3306
MYSQL_USER=your-mysql-user
MYSQL_PASSWORD=your-production-mysql-password
MYSQL_DATABASE=auth_database

# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Production Email
MAIL_USERNAME=your-production-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
MAIL_FROM=your-production-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False

# Frontend URL (update with actual frontend domain)
FRONTEND_URL=https://your-frontend-domain.com
```

## 🔒 Security Checklist

- [ ] Generate strong SECRET_KEY (32+ characters)
- [ ] Use production MySQL database
- [ ] Configure CORS with specific frontend domain
- [ ] Enable HTTPS
- [ ] Set up Firebase production credentials
- [ ] Configure email service
- [ ] Set up database backups

## 📊 Database Setup

### MySQL Commands:
```sql
CREATE DATABASE auth_database;
CREATE USER 'auth_user'@'%' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON auth_database.* TO 'auth_user'@'%';
FLUSH PRIVILEGES;
```

## 🌐 API Endpoints

Your deployed API will be available at: `https://your-domain.com`

All endpoints documented in `API_DOCUMENTATION.md`
