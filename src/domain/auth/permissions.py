from enum import Enum
from .models import UserRole

class Permission(str, Enum):
    RECIPE_READ = "recipe_read"
    RECIPE_WRITE = "recipe_write"
    RECIPE_DELETE = "recipe_delete"
    USER_MANAGE = "user_manage"
    AGENT_RUN = "agent_run"

ROLE_PERMISSIONS = {
    "viewer": set(),
    "editor": {
        Permission.RECIPE_READ,
        Permission.RECIPE_WRITE,
        Permission.AGENT_RUN,
    },
    "admin": {
        Permission.RECIPE_READ,
        Permission.RECIPE_WRITE,
        Permission.RECIPE_DELETE,
        Permission.AGENT_RUN,
        Permission.USER_MANAGE,
    },
}

def has_permission(role: UserRole, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
