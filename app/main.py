from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import sys
import os

# Add the parent directory to the Python path to enable app imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import engine, Base
from app.routers import auth, users, admin
from app.firebase_config import initialize_firebase

# Create tables (with error handling)
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not connect to database: {e}")
    print("💡 Make sure MySQL is running and the database 'auth_database' exists")
    print("🔧 You can still start the API server, but database operations will fail")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_firebase()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Authentication API",
    description="Backend API with MySQL, Firebase integration and role-based access",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "https://*.ngrok.io",  # Allow ngrok tunnels
        "https://*.trycloudflare.com",  # Allow Cloudflare tunnels
        "*"  # Allow all origins for development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {"message": "Authentication API with MySQL is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
