"""
Authentication models for ECES
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserRole(str, Enum):
    """User roles in ECES system"""
    SUPER_ADMIN = "super_admin"      # Full access including matrix editing
    ADMIN = "admin"                  # Administrative access, no matrix editing
    USER = "user"                    # Standard user access
    VIEWER = "viewer"                # Read-only access

class User(BaseModel):
    """User model"""
    id: str
    username: str
    email: EmailStr
    full_name: str
    role: UserRole
    department: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    # Consenso esplicito all'uso aggregato/anonimo dei propri dati per la
    # conoscenza semantica di Lizzy (HANDOFF.md, punti 16-17, 25/07/2026).
    # Opt-in: default False. Gli utenti esistenti al momento dell'introduzione
    # di questo campo non hanno la chiave in users.json -- il default Pydantic
    # qui sotto li rende non-consenzienti automaticamente, senza bisogno di
    # nessuna migrazione dati sul file JSON.
    consents_to_aggregate_analysis: bool = False

class UserLogin(BaseModel):
    """Login request model"""
    username: str
    password: str

class UserCreate(BaseModel):
    """User creation model"""
    username: str
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.USER
    department: Optional[str] = None
    consents_to_aggregate_analysis: bool = False

class Token(BaseModel):
    """JWT Token model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User

class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
    role: Optional[UserRole] = None

class UserRegistration(BaseModel):
    """User registration model (public)"""
    username: str
    email: EmailStr
    full_name: str
    password: str
    department: Optional[str] = None
    # Checkbox esplicita nel form di registrazione (punto 17): default False,
    # l'utente deve attivarla volontariamente. Revocabile/attivabile in
    # qualunque momento dopo la registrazione via PUT /auth/consent.
    consents_to_aggregate_analysis: bool = False

class UserRoleUpdate(BaseModel):
    """User role update model"""
    username: str
    new_role: UserRole

class UserListResponse(BaseModel):
    """User list response model"""
    users: list[User]
    total_count: int

class RegistrationResponse(BaseModel):
    """Registration response model"""
    success: bool
    message: str
    user: Optional[User] = None

class PasswordChange(BaseModel):
    """Password change model"""
    current_password: str
    new_password: str

class PasswordChangeResponse(BaseModel):
    """Password change response model"""
    success: bool
    message: str

class ConsentUpdate(BaseModel):
    """
    Aggiornamento del consenso all'uso aggregato/anonimo dei dati (punto 17).
    Revocabile in qualunque momento dall'utente stesso, da UserProfile.tsx.
    L'effetto riguarda solo le sottomissioni future, non retroattivo sui
    contatori gia' aggregati (non si puo' "disaggregare" un conteggio fatto).
    """
    consents_to_aggregate_analysis: bool

class ConsentUpdateResponse(BaseModel):
    """Risposta all'aggiornamento del consenso"""
    success: bool
    message: str
    consents_to_aggregate_analysis: bool