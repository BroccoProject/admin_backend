from uuid import UUID
from fastapi import Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_admin_db
from infrastructure.auth.jwt_handler import decode_jwt
from infrastructure.database.repositories.admin_repository import SQLAdminRepository
from domain.auth.models import AdminUser
from domain.auth.permissions import Permission, has_permission

async def get_current_admin_user(
    request: Request,
    db: AsyncSession = Depends(get_admin_db)
) -> AdminUser:
    token = request.cookies.get("admin_session")
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication cookie")

    payload = decode_jwt(token)
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Invalid token payload")
        
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID format")

    repo = SQLAdminRepository(db)
    admin_user = await repo.get_by_id(user_id)

    if not admin_user:
        raise HTTPException(status_code=403, detail="User is not authorized for the admin panel")

    return admin_user

def require_permission(permission: Permission):
    async def permission_checker(user: AdminUser = Depends(get_current_admin_user)):
        if not has_permission(user.role, permission):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return permission_checker

CanReadRecipes = Depends(require_permission(Permission.RECIPE_READ))
CanWriteRecipes = Depends(require_permission(Permission.RECIPE_WRITE))
CanDeleteRecipes = Depends(require_permission(Permission.RECIPE_DELETE))
CanRunAgent = Depends(require_permission(Permission.AGENT_RUN))
CanManageUsers = Depends(require_permission(Permission.USER_MANAGE))
IsAuthenticated = Depends(get_current_admin_user)
