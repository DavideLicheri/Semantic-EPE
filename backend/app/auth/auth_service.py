"""
Authentication service for ECES
"""
import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from .models import User, UserRole, Token, TokenData

class AuthService:
    """Authentication service for ECES"""
    
    def __init__(self):
        self.secret_key = os.getenv("ECES_SECRET_KEY", "eces-ispra-secret-key-2024")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 480  # 8 hours for ISPRA workday
        # Use simple SHA256 hashing instead of bcrypt to avoid 72-byte limit
        # self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
        
        # Users database file
        self.users_file = Path("data/auth/users.json")
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize with default super admin if no users exist
        self._init_default_users()
    
    def _init_default_users(self):
        """Initialize default users if none exist"""
        if not self.users_file.exists():
            # Create default super admin (you!)
            default_users = {
                "admin": {
                    "id": "admin",
                    "username": "admin",
                    "email": "davide.licheri@isprambiente.it",
                    "full_name": "Davide Licheri",
                    "role": "super_admin",
                    "department": "ISPRA - DG SINA",
                    "password_hash": self.get_password_hash("admin"),  # Simple default password
                    "is_active": True,
                    "created_at": datetime.now().isoformat()
                }
            }
            
            with open(self.users_file, 'w') as f:
                json.dump(default_users, f, indent=2)
    
    def _load_users(self) -> Dict[str, Any]:
        """Load users from file"""
        if not self.users_file.exists():
            return {}
        
        with open(self.users_file, 'r') as f:
            return json.load(f)
    
    def _save_users(self, users: Dict[str, Any]):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash using SHA256"""
        password_hash = hashlib.sha256((plain_password + self.secret_key).encode()).hexdigest()
        return password_hash == hashed_password
    
    def get_password_hash(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256((password + self.secret_key).encode()).hexdigest()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        users = self._load_users()
        
        if username not in users:
            return None
        
        user_data = users[username]
        
        # Check if user is active
        if not user_data.get("is_active", True):
            return None
        
        if not self.verify_password(password, user_data["password_hash"]):
            return None
        
        # Update last login
        user_data["last_login"] = datetime.now().isoformat()
        users[username] = user_data
        self._save_users(users)
        
        # Return user without password hash
        user_dict = user_data.copy()
        del user_dict["password_hash"]
        return User(**user_dict)
    
    def create_access_token(self, user: User) -> Token:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode = {
            "sub": user.username,
            "role": user.role.value,
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": "ECES-ISPRA"
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return Token(
            access_token=encoded_jwt,
            expires_in=self.access_token_expire_minutes * 60,
            user=user
        )
    
    def verify_token(self, token: str) -> TokenData:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            role: str = payload.get("role")
            
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            return TokenData(username=username, role=UserRole(role))
        
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        users = self._load_users()
        
        if username not in users:
            return None
        
        user_data = users[username].copy()
        del user_data["password_hash"]
        return User(**user_data)
    
    def create_user(self, username: str, email: str, full_name: str, 
                   password: str, role: UserRole = UserRole.USER, 
                   department: str = None) -> User:
        """Create new user (Super Admin only)"""
        users = self._load_users()
        
        if username in users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        user_data = {
            "id": username,
            "username": username,
            "email": email,
            "full_name": full_name,
            "role": role.value,
            "department": department,
            "password_hash": self.get_password_hash(password),
            "is_active": True,
            "created_at": datetime.now().isoformat()
        }
        
        users[username] = user_data
        self._save_users(users)
        
        # Return user without password hash
        user_dict = user_data.copy()
        del user_dict["password_hash"]
        return User(**user_dict)
    
    def has_permission(self, user_role: UserRole, required_role: UserRole) -> bool:
        """Check if user has required permission level"""
        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.USER: 2,
            UserRole.ADMIN: 3,
            UserRole.SUPER_ADMIN: 4
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
    
    def can_edit_matrix(self, user_role: UserRole) -> bool:
        """Check if user can edit matrix (Super Admin only)"""
        return user_role == UserRole.SUPER_ADMIN
    
    def register_user(self, username: str, email: str, full_name: str, 
                     password: str, department: str = None) -> User:
        """Register new user with viewer role (public registration)"""
        users = self._load_users()
        
        # Check if username already exists
        if username in users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username già esistente"
            )
        
        # Check if email already exists
        for user_data in users.values():
            if user_data.get("email") == email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email già registrata"
                )
        
        # Create new user with viewer role
        user_data = {
            "id": username,
            "username": username,
            "email": email,
            "full_name": full_name,
            "role": UserRole.VIEWER.value,  # Default role for new registrations
            "department": department or "ISPRA",
            "password_hash": self.get_password_hash(password),
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "registration_ip": None,  # Can be added later
            "email_verified": False
        }
        
        users[username] = user_data
        self._save_users(users)
        
        # Return user without password hash
        user_dict = user_data.copy()
        del user_dict["password_hash"]
        return User(**user_dict)
    
    def get_all_users(self) -> list[User]:
        """Get all users (Super Admin only)"""
        users = self._load_users()
        user_list = []
        
        for user_data in users.values():
            user_dict = user_data.copy()
            del user_dict["password_hash"]
            user_list.append(User(**user_dict))
        
        return sorted(user_list, key=lambda x: x.created_at, reverse=True)
    
    def update_user_role(self, username: str, new_role: UserRole) -> User:
        """Update user role (Super Admin only)"""
        users = self._load_users()
        
        if username not in users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utente non trovato"
            )
        
        # Don't allow changing the super admin role
        if users[username]["role"] == UserRole.SUPER_ADMIN.value and new_role != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Non è possibile modificare il ruolo del Super Admin"
            )
        
        users[username]["role"] = new_role.value
        users[username]["updated_at"] = datetime.now().isoformat()
        self._save_users(users)
        
        # Return updated user
        user_dict = users[username].copy()
        del user_dict["password_hash"]
        return User(**user_dict)
    
    def deactivate_user(self, username: str) -> User:
        """Deactivate user (Super Admin only)"""
        users = self._load_users()
        
        if username not in users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utente non trovato"
            )
        
        # Don't allow deactivating super admin
        if users[username]["role"] == UserRole.SUPER_ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Non è possibile disattivare il Super Admin"
            )
        
        users[username]["is_active"] = False
        users[username]["deactivated_at"] = datetime.now().isoformat()
        self._save_users(users)
        
        # Return updated user
        user_dict = users[username].copy()
        del user_dict["password_hash"]
        return User(**user_dict)
    
    def activate_user(self, username: str) -> User:
        """Activate user (Super Admin only)"""
        users = self._load_users()
        
        if username not in users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utente non trovato"
            )
        
        users[username]["is_active"] = True
        users[username]["activated_at"] = datetime.now().isoformat()
        self._save_users(users)
        
        # Return updated user
        user_dict = users[username].copy()
        del user_dict["password_hash"]
        return User(**user_dict)
    
    def change_password(self, username: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        users = self._load_users()
        
        if username not in users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utente non trovato"
            )
        
        user_data = users[username]
        
        # Verify current password
        if not self.verify_password(current_password, user_data["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password attuale non corretta"
            )
        
        # Validate new password
        if len(new_password) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nuova password deve essere di almeno 4 caratteri"
            )
        
        # Update password
        users[username]["password_hash"] = self.get_password_hash(new_password)
        users[username]["password_changed_at"] = datetime.now().isoformat()
        self._save_users(users)
        
        return True
    def delete_user_permanently(self, username: str, admin_user: User):
        """
        Permanently delete a user from the system
        WARNING: This removes all user data and cannot be undone!
        
        Args:
            username: Username to delete
            admin_user: Admin user performing the deletion (must be super_admin)
        """
        if admin_user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo i Super Admin possono eliminare utenti definitivamente"
            )
        
        users = self._load_users()
        
        if username not in users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utente non trovato"
            )
        
        # Prevent deletion of the last super admin
        super_admins = [u for u in users.values() if u.get("role") == "super_admin" and u.get("is_active", True)]
        if len(super_admins) <= 1 and users[username].get("role") == "super_admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Non è possibile eliminare l'ultimo Super Admin"
            )
        
        # Remove user from users dictionary
        deleted_user = users.pop(username)
        self._save_users(users)
        
        return {
            "message": f"Utente '{username}' eliminato definitivamente",
            "deleted_user": {
                "username": deleted_user["username"],
                "email": deleted_user["email"],
                "role": deleted_user["role"],
                "created_at": deleted_user["created_at"]
            }
        }
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information (without password hash)"""
        users = self._load_users()
        
        if username not in users:
            return None
        
        user_data = users[username].copy()
        if "password_hash" in user_data:
            del user_data["password_hash"]
        
        return user_data
    
    def list_all_users(self, admin_user: User) -> List[Dict[str, Any]]:
        """
        List all users in the system
        
        Args:
            admin_user: Admin user requesting the list (must be admin or super_admin)
        """
        if admin_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accesso negato: privilegi amministrativi richiesti"
            )
        
        users = self._load_users()
        user_list = []
        
        for username, user_data in users.items():
            user_info = user_data.copy()
            if "password_hash" in user_info:
                del user_info["password_hash"]
            user_list.append(user_info)
        
        return user_list