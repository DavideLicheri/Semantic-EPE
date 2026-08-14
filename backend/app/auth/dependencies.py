"""
Authentication dependencies for FastAPI
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .auth_service import AuthService
from .models import User, UserRole

# Security scheme
# auto_error=False: senza questo, HTTPBearer solleva "Not authenticated" da solo
# quando manca l'header Authorization, PRIMA che get_current_user_optional possa
# restituire None come dovrebbe -- rendendo "optional" inutile in pratica (bug
# preesistente, scoperto il 24/07/2026 testando /convert e /parse dopo averci
# aggiunto get_current_user_optional). Con auto_error=False la scelta se
# richiedere o meno l'autenticazione la fanno le funzioni sotto.
security = HTTPBearer(auto_error=False)

# Auth service instance
auth_service = AuthService()

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> User:
    """Get current authenticated user"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    token_data = auth_service.verify_token(credentials.credentials)
    user = auth_service.get_user(token_data.username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    return current_user

def require_role(required_role: UserRole):
    """Dependency factory for role-based access control"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not auth_service.has_permission(current_user.role, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_role.value}"
            )
        return current_user
    return role_checker

def require_super_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require Super Admin role"""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required"
        )
    return current_user

def require_matrix_edit_permission(current_user: User = Depends(get_current_active_user)) -> User:
    """Require matrix editing permission (Super Admin only)"""
    if not auth_service.can_edit_matrix(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Matrix editing requires Super Admin privileges"
        )
    return current_user

# Optional authentication (for public endpoints that can benefit from user context)
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        token_data = auth_service.verify_token(credentials.credentials)
        return auth_service.get_user(token_data.username)
    except HTTPException:
        return None
def require_rings_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require Rings Admin or Super Admin role (rings_admin sostituisce il
    precedente admin generico, 14/08/2026 -- vedi app/auth/models.py)"""
    if current_user.role not in [UserRole.RINGS_ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rings Admin access required"
        )
    return current_user