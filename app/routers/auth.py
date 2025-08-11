from fastapi import APIRouter, HTTPException, status, Depends, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models.database_models import User, UserSession, Permission
from app.models.schemas import UserCreate, UserLogin, UserResponse, Token, EmailRequest, PasswordReset
from app.auth.security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    generate_verification_token,
    hash_token,
    decode_token
)
from app.auth.dependencies import get_current_user
from app.utils.email import send_verification_email, send_password_reset_email
from app.firebase_config import create_firebase_user, verify_firebase_token

router = APIRouter()

def init_default_permissions(db: Session):
    """Initialize default permissions if they don't exist"""
    default_permissions = [
        {"name": "read", "description": "Can read data"},
        {"name": "write", "description": "Can write data"},
        {"name": "delete", "description": "Can delete data"},
        {"name": "manage_users", "description": "Can manage users"},
        {"name": "manage_roles", "description": "Can manage roles"}
    ]
    
    for perm_data in default_permissions:
        perm = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not perm:
            perm = Permission(**perm_data)
            db.add(perm)
    
    db.commit()

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Initialize permissions
    init_default_permissions(db)
    
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate verification token
    verification_token = generate_verification_token()
    
    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        phone=user_data.phone,
        role=user_data.role,
        hashed_password=get_password_hash(user_data.password),
        email_verification_token=hash_token(verification_token),
        email_verification_expire=datetime.utcnow() + timedelta(hours=24)
    )
    
    # Add default permissions based on role
    if user.role == "admin":
        permissions = db.query(Permission).all()
        user.permissions = permissions
    elif user.role == "hr":
        permissions = db.query(Permission).filter(
            Permission.name.in_(["read", "write", "manage_users"])
        ).all()
        user.permissions = permissions
    else:
        permission = db.query(Permission).filter(Permission.name == "read").first()
        if permission:
            user.permissions = [permission]
    
    # Create Firebase user (optional)
    firebase_uid = create_firebase_user(user_data.email, user_data.password, user_data.name)
    if firebase_uid:
        user.firebase_uid = firebase_uid
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Send verification email (with error handling)
    try:
        await send_verification_email(user.email, user.name, verification_token)
        print(f"✅ Verification email sent to {user.email}")
    except Exception as e:
        print(f"⚠️ Warning: Could not send verification email: {e}")
        print("💡 User can still login, but email verification is disabled")
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    # Store refresh token in session
    session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(session)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Find user
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    # Store refresh token in session
    session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent")
    )
    db.add(session)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/firebase-login", response_model=Token)
async def firebase_login(
    id_token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    try:
        # Verify Firebase token
        decoded_token = verify_firebase_token(id_token)
        email = decoded_token.get("email")
        firebase_uid = decoded_token.get("uid")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not found in Firebase token"
            )
        
        # Find or create user
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user from Firebase
            user = User(
                email=email,
                name=decoded_token.get("name", ""),
                firebase_uid=firebase_uid,
                role="user",
                is_active=True,
                is_email_verified=True,  # Firebase users are verified
                hashed_password=""  # No password for Firebase users
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update Firebase UID if not set
            if not user.firebase_uid:
                user.firebase_uid = firebase_uid
                db.commit()
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": email, "role": user.role, "user_id": user.id}
        )
        refresh_token = create_refresh_token(
            data={"sub": email, "user_id": user.id}
        )
        
        # Store refresh token
        session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(session)
        db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Firebase authentication failed: {str(e)}"
        )

@router.get("/verify-email/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    hashed_token = hash_token(token)
    
    # Find user with token
    user = db.query(User).filter(
        User.email_verification_token == hashed_token,
        User.email_verification_expire > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Update user
    user.is_email_verified = True
    user.email_verification_token = None
    user.email_verification_expire = None
    db.commit()
    
    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
async def forgot_password(
    email_request: EmailRequest,
    db: Session = Depends(get_db)
):
    # Find user
    user = db.query(User).filter(User.email == email_request.email).first()
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    reset_token = generate_verification_token()
    
    # Update user with reset token
    user.reset_password_token = hash_token(reset_token)
    user.reset_password_expire = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    
    # Send reset email (with error handling)
    try:
        await send_password_reset_email(user.email, user.name, reset_token)
        print(f"✅ Password reset email sent to {user.email}")
    except Exception as e:
        print(f"⚠️ Warning: Could not send password reset email: {e}")
        print("💡 Password reset email functionality is disabled")
    
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/reset-password")
async def reset_password(
    password_reset: PasswordReset,
    db: Session = Depends(get_db)
):
    hashed_token = hash_token(password_reset.token)
    
    # Find user with token
    user = db.query(User).filter(
        User.reset_password_token == hashed_token,
        User.reset_password_expire > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Update password
    user.hashed_password = get_password_hash(password_reset.new_password)
    user.reset_password_token = None
    user.reset_password_expire = None
    db.commit()
    
    return {"message": "Password reset successfully"}

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    payload = decode_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("user_id")
    
    # Verify refresh token exists in database
    session = db.query(UserSession).filter(
        UserSession.refresh_token == refresh_token,
        UserSession.user_id == user_id,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user = session.user
    
    # Create new access token
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Remove all user sessions
    db.query(UserSession).filter(UserSession.user_id == current_user.id).delete()
    db.commit()
    
    return {"message": "Successfully logged out"}
