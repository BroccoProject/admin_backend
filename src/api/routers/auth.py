from fastapi import APIRouter, Response, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from api.dependencies.db import get_admin_db
from api.dependencies.auth import get_current_admin_user
from api.dependencies.admin import get_admin_service
from services.admin.admin_service import AdminService
from infrastructure.auth.google_oauth import get_google_auth_url, exchange_code_for_token, get_google_user_info
import infrastructure.auth.github_oauth as github_oauth
from infrastructure.auth.jwt_handler import create_jwt
from infrastructure.database.repositories.admin_repository import SQLAdminRepository
from domain.auth.models import AdminUser
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/google")
async def login_via_google():
    auth_url = get_google_auth_url()
    return RedirectResponse(url=auth_url)

@router.get("/google/callback")
async def google_oauth_callback(code: str, service: AdminService = Depends(get_admin_service)):
    token_response = await exchange_code_for_token(code)
    access_token = token_response.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received from Google")
        
    user_info = await get_google_user_info(access_token)
    google_sub = user_info.get("sub")
    email = user_info.get("email")
    if not google_sub or not email:
        raise HTTPException(status_code=400, detail="Invalid user info from Google")
        
    admin_user = await service.get_or_create_oauth_profile("google", google_sub, email)
    if not admin_user:
        status = await service.get_auth_status_for_email(email)
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/pending?status={status}")
        
    jwt_token = create_jwt(admin_user.id, admin_user.role.value if hasattr(admin_user.role, 'value') else admin_user.role)
    
    response = RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard")
    response.set_cookie(
        key="admin_session",
        value=jwt_token,
        httponly=True,
        secure=settings.is_production,
        samesite="none" if settings.is_production else "lax",
        max_age=3600,
    )
    return response

@router.get("/github")
async def login_via_github():
    auth_url = github_oauth.get_github_auth_url()
    return RedirectResponse(url=auth_url)

@router.get("/github/callback")
async def github_oauth_callback(code: str, service: AdminService = Depends(get_admin_service)):
    token_response = await github_oauth.exchange_code_for_token(code)
    access_token = token_response.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received from GitHub")
        
    user_info = await github_oauth.get_github_user_info(access_token)
    github_id = user_info.get("id")
    email = user_info.get("email")
    if not github_id or not email:
        raise HTTPException(status_code=400, detail="Invalid user info from GitHub")
        
    admin_user = await service.get_or_create_oauth_profile("github", github_id, email)
    if not admin_user:
        status = await service.get_auth_status_for_email(email)
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/pending?status={status}")
        
    jwt_token = create_jwt(admin_user.id, admin_user.role.value if hasattr(admin_user.role, 'value') else admin_user.role)
    
    response = RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard")
    response.set_cookie(
        key="admin_session",
        value=jwt_token,
        httponly=True,
        secure=settings.is_production,
        samesite="none" if settings.is_production else "lax",
        max_age=3600,
    )
    return response

@router.post("/register")
async def register_local(request: LoginRequest, service: AdminService = Depends(get_admin_service)):
    await service.register_local(request.email, request.password)
    return {"detail": "Registration successful. Request access to use the panel."}

@router.post("/login")
async def login_local(request: LoginRequest, service: AdminService = Depends(get_admin_service)):
    profile = await service.login_local(request.email, request.password)
    jwt_token = create_jwt(profile.id, profile.role)
    
    response = Response(content='{"role": "' + profile.role + '"}', media_type="application/json")
    response.set_cookie(
        key="admin_session",
        value=jwt_token,
        httponly=True,
        secure=settings.is_production,
        samesite="none" if settings.is_production else "lax",
        max_age=3600,
    )
    return response

@router.delete("/session")
async def delete_session(response: Response):
    response.delete_cookie(
        key="admin_session",
        httponly=True,
        secure=settings.is_production,
        samesite="none" if settings.is_production else "lax"
    )
    return {"detail": "Logged out"}

@router.get("/me")
async def get_current_user_info(
    current_user: AdminUser = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service)
):
    status = await service.get_auth_status_for_email(current_user.email)
    return {
        "email": current_user.email, 
        "role": current_user.role,
        "access_status": status
    }