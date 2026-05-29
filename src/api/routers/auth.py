from fastapi import APIRouter, Response, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from api.dependencies.db import get_admin_db
from api.dependencies.auth import get_current_admin_user
from api.dependencies.admin import get_admin_service
from services.admin.admin_service import AdminService
from infrastructure.auth.google_oauth import get_google_auth_url, exchange_code_for_token, get_google_user_info
from infrastructure.auth.jwt_handler import create_jwt
from infrastructure.database.repositories.admin_repository import SQLAdminRepository
from domain.auth.models import AdminUser

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/google")
async def login_via_google():
    auth_url = get_google_auth_url()
    return RedirectResponse(url=auth_url)

@router.get("/google/callback") #TODO zrobic serwis zamiast wywolywania repo bezposrednio w endpointcie
async def google_oauth_callback(code: str, db: AsyncSession = Depends(get_admin_db)):
    token_response = await exchange_code_for_token(code)
    access_token = token_response.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received from Google")
        
    user_info = await get_google_user_info(access_token)
    google_sub = user_info.get("sub")
    print("Sub:" + google_sub)
    email = user_info.get("email")
    if not google_sub or not email:
        raise HTTPException(status_code=400, detail="Invalid user info from Google")
        
    repo = SQLAdminRepository(db)
    admin_user = await repo.get_by_google_sub(google_sub) 
    
    if not admin_user:
        admin_user = await repo.get_by_email(email)
        if admin_user:
            admin_user = await repo.update_google_sub(admin_user.id, google_sub)
        else:
            admin_user = await repo.create_viewer_profile(email=email, google_sub=google_sub)
        
    jwt_token = create_jwt(admin_user.id, admin_user.role.value)
    
    response = RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard")
    response.set_cookie(
        key="admin_session",
        value=jwt_token,
        httponly=True,
        secure=False, # musi byc true na produkcji
        samesite="lax",
        max_age=3600,
    )
    return response

@router.delete("/session")
async def delete_session(response: Response):
    response.delete_cookie(
        key="admin_session",
        httponly=True,
        secure=False, # musi byc true na produkcji
        samesite="lax"
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