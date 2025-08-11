from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.database_models import User, Permission
from app.models.schemas import UserResponse, UserRole, PermissionResponse
from app.auth.dependencies import require_role, require_permission

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.HR])),
    db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            role=user.role,
            permissions=[p.name for p in user.permissions],
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            created_at=user.created_at,
            last_login=user.last_login
        )
        for user in users
    ]

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.HR])),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        phone=user.phone,
        role=user.role,
        permissions=[p.name for p in user.permissions],
        is_active=user.is_active,
        is_email_verified=user.is_email_verified,
        created_at=user.created_at,
        last_login=user.last_login
    )

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: UserRole,
    current_user: User = Depends(require_permission(["manage_roles"])),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.role = role
    user.updated_at = datetime.utcnow()
    
    # Update permissions based on new role
    if role == UserRole.ADMIN:
        permissions = db.query(Permission).all()
        user.permissions = permissions
    elif role == UserRole.HR:
        permissions = db.query(Permission).filter(
            Permission.name.in_(["read", "write", "manage_users"])
        ).all()
        user.permissions = permissions
    else:
        permission = db.query(Permission).filter(Permission.name == "read").first()
        user.permissions = [permission] if permission else []
    
    db.commit()
    
    return {"message": f"User role updated to {role}"}

@router.put("/users/{user_id}/permissions")
async def update_user_permissions(
    user_id: int,
    permission_names: List[str],
    current_user: User = Depends(require_permission(["manage_users"])),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get permissions
    permissions = db.query(Permission).filter(
        Permission.name.in_(permission_names)
    ).all()
    
    user.permissions = permissions
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "User permissions updated"}

@router.put("/users/{user_id}/status")
async def toggle_user_status(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = is_active
    user.updated_at = datetime.utcnow()
    db.commit()
    
    status_text = "activated" if is_active else "deactivated"
    return {"message": f"User {status_text} successfully"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission(["delete"])),
    db: Session = Depends(get_db)
):
    # Prevent self-deletion
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    from sqlalchemy import func
    
    # Get statistics
    total_users = db.query(User).count()
    verified_users = db.query(User).filter(User.is_email_verified == True).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # Count by role
    role_counts = {}
    for role in UserRole:
        count = db.query(User).filter(User.role == role.value).count()
        role_counts[role.value] = count
    
    # Recent registrations (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_registrations = db.query(User).filter(
        User.created_at >= seven_days_ago
    ).count()
    
    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "active_users": active_users,
        "users_by_role": role_counts,
        "recent_registrations": recent_registrations
    }

@router.get("/permissions", response_model=List[PermissionResponse])
async def get_all_permissions(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    permissions = db.query(Permission).all()
    return permissions
