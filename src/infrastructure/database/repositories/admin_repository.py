from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.admin_auth.admin_profile import AdminProfile
from domain.auth.models import AdminUser, UserRole

class SQLAdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, admin_id: UUID) -> AdminUser | None:
        result = await self.db.execute(
            select(AdminProfile).where(AdminProfile.id == admin_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            return None
            
        return AdminUser(
            id=profile.id,
            email=profile.email,
            role=UserRole(profile.role)
        )

    async def get_by_google_sub(self, google_sub: str) -> AdminUser | None:
        result = await self.db.execute(
            select(AdminProfile).where(AdminProfile.google_sub == google_sub)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            return None
            
        return AdminUser(
            id=profile.id,
            email=profile.email,
            role=UserRole(profile.role)
        )
