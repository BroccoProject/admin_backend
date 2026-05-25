from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_admin_db
from infrastructure.database.repositories.admin_repository import SQLAdminRepository
from services.admin.admin_service import AdminService


async def get_admin_service(db: AsyncSession = Depends(get_admin_db)) -> AdminService:
    repo = SQLAdminRepository(db)
    return AdminService(repo)
