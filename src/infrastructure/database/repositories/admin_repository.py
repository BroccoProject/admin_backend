from uuid import UUID
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.admin_auth.admin_profile import AdminProfile
from infrastructure.database.models.admin_auth.access_request import AccessRequest
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
            role=UserRole(profile.role),
            auth_provider=profile.auth_provider,
            provider_id=profile.provider_id
        )

    async def get_by_provider(self, provider: str, provider_id: str) -> AdminUser | None:
        result = await self.db.execute(
            select(AdminProfile).where(
                AdminProfile.auth_provider == provider,
                AdminProfile.provider_id == provider_id
            )
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            return None
            
        return AdminUser(
            id=profile.id,
            email=profile.email,
            role=UserRole(profile.role),
            auth_provider=profile.auth_provider,
            provider_id=profile.provider_id
        )

    async def get_by_email(self, email: str) -> AdminUser | None:
        result = await self.db.execute(
            select(AdminProfile).where(AdminProfile.email == email).order_by(AdminProfile.created_at.desc()).limit(1)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            return None
            
        return AdminUser(
            id=profile.id,
            email=profile.email,
            role=UserRole(profile.role),
            auth_provider=profile.auth_provider,
            provider_id=profile.provider_id
        )

    async def create_profile(
        self,
        email: str,
        role: str,
        auth_provider: str,
        provider_id: str | None,
        password_hash: str | None = None,
        created_by: UUID | None = None
    ) -> AdminUser:
        new_profile = AdminProfile(
            email=email,
            role=role,
            auth_provider=auth_provider,
            provider_id=provider_id,
            password_hash=password_hash,
            created_by=created_by
        )
        self.db.add(new_profile)
        await self.db.commit()
        await self.db.refresh(new_profile)
        return AdminUser(
            id=new_profile.id,
            email=new_profile.email,
            role=UserRole(new_profile.role),
            auth_provider=new_profile.auth_provider,
            provider_id=new_profile.provider_id
        )

    async def create_access_request(self, email: str, message: str | None, user_id: UUID | None = None):
        result = await self.db.execute(
            select(AccessRequest).where(
                AccessRequest.email == email,
                AccessRequest.status == "pending"
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="A pending request for this email already exists.")
            
        req = AccessRequest(email=email, message=message, profile_id=user_id)
        self.db.add(req)
        await self.db.commit()
        await self.db.refresh(req)
        return req

    async def get_access_request_by_token(self, token: UUID):
        result = await self.db.execute(select(AccessRequest).where(AccessRequest.token == token))
        return result.scalar_one_or_none()

    async def get_access_request_by_email(self, email: str):
        result = await self.db.execute(
            select(AccessRequest).where(AccessRequest.email == email).order_by(AccessRequest.created_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_access_requests(self, status: str | None = None):
        query = select(AccessRequest).order_by(AccessRequest.created_at.desc())
        if status:
            query = query.where(AccessRequest.status == status)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_access_request_by_id(self, request_id: UUID):
        result = await self.db.execute(select(AccessRequest).where(AccessRequest.id == request_id))
        return result.scalar_one_or_none()

    async def approve_access_request(self, request, resolved_by: UUID | None, bypass_expiry: bool = False) -> AdminProfile:
        is_expired = request.token_expires_at < datetime.now(timezone.utc)
        if request.status != "pending" or request.token_used or (is_expired and not bypass_expiry):
            raise HTTPException(status_code=400, detail="Invalid, used, or expired token.")

        request.status = "approved"
        request.token_used = True
        request.resolved_at = datetime.now(timezone.utc)
        request.resolved_by = resolved_by

        if getattr(request, 'profile_id', None):
            result = await self.db.execute(select(AdminProfile).where(AdminProfile.id == request.profile_id))
            existing_profile = result.scalar_one_or_none()
            if existing_profile:
                existing_profile.role = "editor"
                self.db.add(existing_profile)
                new_profile = existing_profile
            else:
                raise HTTPException(status_code=404, detail="Profile associated with this request not found.")
        else:
            # Fallback for older requests without profile_id
            result = await self.db.execute(select(AdminProfile).where(AdminProfile.email == request.email).limit(1))
            existing_profile = result.scalar_one_or_none()
            
            if existing_profile:
                existing_profile.role = "editor"
                self.db.add(existing_profile)
                new_profile = existing_profile
            else:
                new_profile = AdminProfile(
                    email=request.email,
                    role="editor",
                    auth_provider='local',
                    provider_id=None,
                    password_hash=None
                )
                self.db.add(new_profile)

        await self.db.commit()
        await self.db.refresh(new_profile)
        return new_profile

    async def reject_access_request(self, request, resolved_by: UUID) -> None:
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
