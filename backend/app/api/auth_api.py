"""
Authentication API endpoints for ECES
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer

from ..auth.auth_service import AuthService
from ..auth.models import (
    UserLogin, Token, User, UserCreate, UserRole, 
    UserRegistration, UserRoleUpdate, UserListResponse, RegistrationResponse,
    PasswordChange, PasswordChangeResponse
)
from ..auth.dependencies import get_current_active_user, require_super_admin, require_admin
from ..services.email_service import email_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
auth_service = AuthService()

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Login endpoint for ECES users
    
    **ISPRA Internal Use Only**
    """
    user = auth_service.authenticate_user(
        user_credentials.username, 
        user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_service.create_access_token(user)
    return token

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    """
    return current_user

@router.post("/users", response_model=User)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_super_admin)
):
    """
    Create new user (Super Admin only)
    """
    return auth_service.create_user(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password=user_data.password,
        role=user_data.role,
        department=user_data.department
    )

@router.get("/permissions")
async def get_user_permissions(current_user: User = Depends(get_current_active_user)):
    """
    Get current user permissions
    """
    return {
        "user": current_user.username,
        "role": current_user.role,
        "permissions": {
            "can_view": True,
            "can_use_recognition": current_user.role in [UserRole.USER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
            "can_use_conversion": current_user.role in [UserRole.USER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
            "can_view_matrix": current_user.role in [UserRole.USER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
            "can_edit_matrix": current_user.role == UserRole.SUPER_ADMIN,
            "can_manage_users": current_user.role == UserRole.SUPER_ADMIN,
            "can_access_admin": current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
        }
    }

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout endpoint (client-side token removal)
    """
    return {"message": "Successfully logged out"}

@router.get("/health")
async def auth_health():
    """
    Authentication service health check
    """
    return {
        "status": "healthy",
        "service": "ECES Authentication",
        "environment": "ISPRA Internal",
        "timestamp": "2024-12-25T12:00:00Z"
    }

@router.post("/register", response_model=RegistrationResponse)
async def register_user(
    registration_data: UserRegistration,
    background_tasks: BackgroundTasks
):
    """
    Public user registration endpoint
    
    Creates new user with 'viewer' role automatically.
    Sends email notification to admin.
    """
    try:
        # Register new user with viewer role
        new_user = auth_service.register_user(
            username=registration_data.username,
            email=registration_data.email,
            full_name=registration_data.full_name,
            password=registration_data.password,
            department=registration_data.department
        )
        
        # Send email notification in background
        user_data = {
            'username': new_user.username,
            'email': new_user.email,
            'full_name': new_user.full_name,
            'department': new_user.department
        }
        background_tasks.add_task(email_service.send_registration_notification, user_data)
        
        return RegistrationResponse(
            success=True,
            message="Registrazione completata con successo. Hai accesso in sola lettura al sistema.",
            user=new_user
        )
        
    except HTTPException as e:
        return RegistrationResponse(
            success=False,
            message=e.detail
        )
    except Exception as e:
        return RegistrationResponse(
            success=False,
            message="Errore durante la registrazione. Riprova più tardi."
        )

@router.get("/users", response_model=UserListResponse)
async def get_all_users(current_user: User = Depends(require_super_admin)):
    """
    Get all users (Super Admin only)
    """
    users = auth_service.get_all_users()
    return UserListResponse(
        users=users,
        total_count=len(users)
    )

@router.put("/users/role", response_model=User)
async def update_user_role(
    role_update: UserRoleUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_super_admin)
):
    """
    Update user role (Super Admin only)
    """
    # Get current user data for email notification
    current_user_data = auth_service.get_user(role_update.username)
    if not current_user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    
    old_role = current_user_data.role.value
    
    # Update role
    updated_user = auth_service.update_user_role(
        username=role_update.username,
        new_role=role_update.new_role
    )
    
    # Send email notification in background
    user_data = {
        'username': updated_user.username,
        'email': updated_user.email,
        'full_name': updated_user.full_name
    }
    background_tasks.add_task(
        email_service.send_role_change_notification, 
        user_data, 
        old_role, 
        role_update.new_role.value
    )
    
    return updated_user

@router.put("/users/{username}/deactivate", response_model=User)
async def deactivate_user(
    username: str,
    current_user: User = Depends(require_super_admin)
):
    """
    Deactivate user (Super Admin only)
    """
    return auth_service.deactivate_user(username)

@router.put("/users/{username}/activate", response_model=User)
async def activate_user(
    username: str,
    current_user: User = Depends(require_super_admin)
):
    """
    Activate user (Super Admin only)
    """
    return auth_service.activate_user(username)

@router.put("/change-password", response_model=PasswordChangeResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user)
):
    """
    Change current user's password
    """
    try:
        auth_service.change_password(
            username=current_user.username,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        return PasswordChangeResponse(
            success=True,
            message="Password cambiata con successo"
        )
        
    except HTTPException as e:
        return PasswordChangeResponse(
            success=False,
            message=e.detail
        )
    except Exception as e:
        return PasswordChangeResponse(
            success=False,
            message="Errore durante il cambio password. Riprova più tardi."
        )

@router.delete("/users/{username}")
async def delete_user_permanently(
    username: str,
    current_user: User = Depends(require_super_admin)
):
    """
    Permanently delete a user (Super Admin only)
    WARNING: This action cannot be undone!
    """
    return auth_service.delete_user_permanently(username, current_user)

@router.get("/users")
async def list_users(
    current_user: User = Depends(require_admin)
):
    """
    List all users (Admin and Super Admin only)
    """
    return auth_service.list_all_users(current_user)

@router.get("/users/{username}")
async def get_user(
    username: str,
    current_user: User = Depends(require_admin)
):
    """
    Get user information (Admin and Super Admin only)
    """
    user_info = auth_service.get_user_info(username)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    return user_info