from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base

# Association table for user permissions
user_permissions = Table(
    'user_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    HR = "hr"
    CANDIDATE = "candidate"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    firebase_uid = Column(String(255), unique=True, nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Email verification
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expire = Column(DateTime, nullable=True)
    
    # Password reset
    reset_password_token = Column(String(255), nullable=True)
    reset_password_expire = Column(DateTime, nullable=True)
    
    # Relationships
    permissions = relationship("Permission", secondary=user_permissions, back_populates="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    
    # Relationship
    users = relationship("User", secondary=user_permissions, back_populates="permissions")

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    refresh_token = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="sessions")
