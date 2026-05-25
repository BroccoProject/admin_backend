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

    async def create_access_request(self, email: str, message: str | None, user_id: UUID | None = None):
        from fastapi import HTTPException
        from infrastructure.database.models.admin_auth.access_request import AccessRequest
        
        # Check for existing pending request for this email
        result = await self.db.execute(
            select(AccessRequest).where(
                AccessRequest.email == email,
                AccessRequest.status == "pending"
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="A pending request for this email already exists.")
            
        req = AccessRequest(email=email, message=message)
        self.db.add(req)
        await self.db.commit()
        await self.db.refresh(req)
        return req

    async def get_access_request_by_token(self, token: UUID):
        from infrastructure.database.models.admin_auth.access_request import AccessRequest
        result = await self.db.execute(select(AccessRequest).where(AccessRequest.token == token))
        return result.scalar_one_or_none()

    async def get_access_requests(self, status: str | None = None):
        from infrastructure.database.models.admin_auth.access_request import AccessRequest
        query = select(AccessRequest).order_by(AccessRequest.created_at.desc())
        if status:
            query = query.where(AccessRequest.status == status)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_access_request_by_id(self, request_id: UUID):
        from infrastructure.database.models.admin_auth.access_request import AccessRequest
        result = await self.db.execute(select(AccessRequest).where(AccessRequest.id == request_id))
        return result.scalar_one_or_none()

    async def approve_access_request(self, request, resolved_by: UUID | None, bypass_expiry: bool = False) -> AdminProfile:
        from fastapi import HTTPException
        from datetime import datetime, timezone
        
        is_expired = request.token_expires_at < datetime.now(timezone.utc)
        if request.status != "pending" or request.token_used or (is_expired and not bypass_expiry):
            raise HTTPException(status_code=400, detail="Invalid, used, or expired token.")

        request.status = "approved"
        request.token_used = True
        request.resolved_at = datetime.now(timezone.utc)
        request.resolved_by = resolved_by

        new_profile = AdminProfile(
            email=request.email,
            role="editor",
            google_sub=None # TODO: they will link their Google account on first login
        )
        self.db.add(new_profile)
        await self.db.commit()
        await self.db.refresh(new_profile)
        return new_profile

    async def reject_access_request(self, request, resolved_by: UUID) -> None:
        from fastapi import HTTPException
        from datetime import datetime, timezone
        if request.status != "pending":
            raise HTTPException(status_code=400, detail="Request is not pending.")
            
        request.status = "rejected"
        request.resolved_at = datetime.now(timezone.utc)
        request.resolved_by = resolved_by
        
        await self.db.commit()

    async def get_team_members(self) -> list[AdminProfile]:
        result = await self.db.execute(
            select(AdminProfile).order_by(AdminProfile.email)
        )
        return list(result.scalars().all())

    async def update_team_member_role(self, member_id: UUID, role: str) -> AdminProfile | None:
        result = await self.db.execute(
            select(AdminProfile).where(AdminProfile.id == member_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            return None
        
        profile.role = role
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def delete_team_member(self, member_id: UUID) -> bool:
        result = await self.db.execute(
            select(AdminProfile).where(AdminProfile.id == member_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            return False
            
        await self.db.delete(profile)
        await self.db.commit()
        return True
