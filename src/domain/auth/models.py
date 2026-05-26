from dataclasses import dataclass
from enum import Enum
from uuid import UUID

class UserRole(str, Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"

@dataclass
class AdminUser:
    id: UUID
    email: str
    role: UserRole
