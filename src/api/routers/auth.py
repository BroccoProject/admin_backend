from fastapi import Request
from infrastructure.auth.jwt_handler import decode_jwt
from fastapi import APIRouter, Response, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_admin_db
from api.dependencies.auth import get_current_admin_user
from infrastructure.auth.google_oauth import get_google_auth_url, exchange_code_for_token, get_google_user_info
from infrastructure.auth.jwt_handler import create_jwt
from infrastructure.database.repositories.admin_repository import SQLAdminRepository
from domain.auth.models import AdminUser

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/google")
async def login_via_google():
    auth_url = get_google_auth_url()
    return RedirectResponse(url=auth_url)

@router.get("/google/callback")
async def google_oauth_callback(code: str, db: AsyncSession = Depends(get_admin_db)):
    token_response = await exchange_code_for_token(code)
    access_token = token_response.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received from Google")
        
    user_info = await get_google_user_info(access_token)
    print(f"DEBUG google_sub: {user_info.get('sub')}")
    google_sub = user_info.get("sub")
    if not google_sub:
        raise HTTPException(status_code=400, detail="Invalid user info from Google")
        
    repo = SQLAdminRepository(db)
    admin_user = await repo.get_by_google_sub(google_sub)
    
    if not admin_user:
        raise HTTPException(status_code=403, detail="Not authorized as admin panel user")
        
    jwt_token = create_jwt(admin_user.id, admin_user.role.value)
    
    response = RedirectResponse(url="http://localhost:4200/dashboard")
    response.set_cookie(
        key="admin_session",
        value=jwt_token,
        httponly=True,
        secure=False, # Must be True in production
        samesite="lax",
        max_age=3600,
    )
    return response

@router.delete("/session")
async def delete_session(response: Response):
    response.delete_cookie(
        key="admin_session",
        httponly=True,
        secure=False, # Must be True in production
        samesite="lax"
    )
    return {"detail": "Logged out"}

@router.get("/me")
async def get_current_user_info(current_user: AdminUser = Depends(get_current_admin_user)):
    return {"email": current_user.email, "role": current_user.role}


# tymczasowo w api/routers/auth.py
@router.get("/auth/google/debug-sub")
async def debug_sub(request: Request):
    """TEMPORARY - remove before production"""
    token = request.cookies.get("admin_session")
    if not token:
        return {"error": "no cookie"}
    payload = decode_jwt(token)
    return payload