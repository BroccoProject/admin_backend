from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from infrastructure.database.repositories.admin_repository import SQLAdminRepository
from infrastructure.database.models.admin_auth.admin_profile import AdminProfile
from infrastructure.database.models.admin_auth.access_request import AccessRequest
from infrastructure.email.email_service import send_email, build_approval_request_email, build_approval_confirmation_email
from core.config import settings


class AdminService:
    def __init__(self, repository: SQLAdminRepository):
        self.repository = repository

    async def create_access_request(self, email: str, message: str | None, user_id: UUID | None = None) -> AccessRequest:
        req = await self.repository.create_access_request(email=email, message=message, user_id=user_id)
        
        approve_url = f"{settings.BACKEND_URL}/api/v1/access-requests/{req.token}/approve"
        subject, body = build_approval_request_email(email, message, approve_url)
        
        await send_email(settings.ADMIN_EMAIL, subject, body)
        return req

    async def get_auth_status_for_email(self, email: str) -> str:
        request = await self.repository.get_access_request_by_email(email)
        if not request:
            return 'not_registered'
        if request.status == 'pending':
            return 'waiting_approval'
        if request.status == 'rejected':
            return 'access_rejected'
        return 'not_registered'

    async def approve_via_token(self, token: UUID) -> AdminProfile:
        req = await self.repository.get_access_request_by_token(token)
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")
            
        profile = await self.repository.approve_access_request(req, resolved_by=None)
        
        subject, body = build_approval_confirmation_email(req.email)
        await send_email(req.email, subject, body)
        return profile

    async def approve_via_panel(self, request_id: UUID, resolved_by: UUID) -> AccessRequest:
        req = await self.repository.get_access_request_by_id(request_id)
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")
            
        await self.repository.approve_access_request(req, resolved_by=resolved_by, bypass_expiry=True)
        
        subject, body = build_approval_confirmation_email(req.email)
        await send_email(req.email, subject, body)
        return req

    async def reject_access_request(self, request_id: UUID, resolved_by: UUID) -> AccessRequest:
        req = await self.repository.get_access_request_by_id(request_id)
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")
            
        await self.repository.reject_access_request(req, resolved_by=resolved_by)
        return req

    async def get_access_requests(self, status: str | None = None) -> list[AccessRequest]:
        return await self.repository.get_access_requests(status=status)

    async def get_team_members(self) -> list[AdminProfile]:
        return await self.repository.get_team_members()

    async def update_team_member_role(self, member_id: UUID, role: str, current_admin_id: UUID) -> AdminProfile:
        if member_id == current_admin_id:
            raise HTTPException(status_code=400, detail="You cannot change your own role to avoid lockout")
            
        profile = await self.repository.update_team_member_role(member_id, role)
        if not profile:
            raise HTTPException(status_code=404, detail="Team member not found")
            
        return profile

    async def delete_team_member(self, member_id: UUID, current_admin_id: UUID) -> None:
        if member_id == current_admin_id:
            raise HTTPException(status_code=400, detail="You cannot revoke your own access")
            
        success = await self.repository.delete_team_member(member_id)
        if not success:
            raise HTTPException(status_code=404, detail="Team member not found")

    async def register_local(self, email: str, password: str) -> str:
        existing = await self.repository.get_by_email(email)
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")
            
        hashed_password = pwd_context.hash(password)
        await self.repository.create_profile(
            email=email,
            role='viewer',
            auth_provider='local',
            provider_id=None,
            password_hash=hashed_password
        )
        return "registered"

    async def login_local(self, email: str, password: str) -> AdminProfile:
        result = await self.repository.db.execute(select(AdminProfile).where(AdminProfile.email == email))
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
        if profile.auth_provider != 'local' or not profile.password_hash:
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
        if not pwd_context.verify(password, profile.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
            
        return profile

    async def get_or_create_oauth_profile(self, provider: str, provider_id: str, email: str) -> AdminProfile | None:
        result = await self.repository.db.execute(
            select(AdminProfile).where(
                AdminProfile.auth_provider == provider,
                AdminProfile.provider_id == provider_id
            )
        )
        profile = result.scalar_one_or_none()
        if profile:
            return profile
            
        new_profile = AdminProfile(
            email=email,
            role="viewer",
            auth_provider=provider,
            provider_id=provider_id,
            password_hash=None
        )
        self.repository.db.add(new_profile)
        await self.repository.db.commit()
        await self.repository.db.refresh(new_profile)
        return new_profile
