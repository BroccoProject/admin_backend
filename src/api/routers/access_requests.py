from uuid import UUID
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import RedirectResponse

from core.config import settings
from api.dependencies.auth import IsAuthenticated, CanManageUsers, get_current_admin_user
from api.dependencies.admin import get_admin_service
from services.admin.admin_service import AdminService
from domain.auth.models import AdminUser
from api.schemas.access_request import (
    AccessRequestCreate, 
    AccessRequestResponse, 
    AccessRequestListResponse, 
    TeamMemberResponse, 
    TeamMemberListResponse, 
    UpdateRoleRequest
)

router = APIRouter(prefix="/access-requests", tags=["Access Requests"])

@router.post("", response_model=AccessRequestResponse, status_code=201, dependencies=[IsAuthenticated])
async def create_access_request(
    data: AccessRequestCreate,
    current_user: AdminUser = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service)
):
    req = await service.create_access_request(email=data.email, message=data.message, user_id=current_user.id)
    return AccessRequestResponse.model_validate(req)

@router.get("/{token}/approve")
async def approve_access_request(
    token: UUID,
    service: AdminService = Depends(get_admin_service)
):
    await service.approve_via_token(token)
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/access-requests/approved")

@router.patch("/{id}/reject", response_model=AccessRequestResponse, dependencies=[CanManageUsers])
async def reject_access_request(
    id: UUID,
    current_admin: AdminUser = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service)
):
    req = await service.reject_access_request(request_id=id, resolved_by=current_admin.id)
    return AccessRequestResponse.model_validate(req)

@router.get("", response_model=AccessRequestListResponse, dependencies=[CanManageUsers])
async def get_access_requests(
    status: str | None = Query(None),
    service: AdminService = Depends(get_admin_service)
):
    reqs = await service.get_access_requests(status=status)
    return AccessRequestListResponse(
        items=[AccessRequestResponse.model_validate(r) for r in reqs],
        total=len(reqs)
    )

@router.post("/{id}/approve", response_model=AccessRequestResponse, dependencies=[CanManageUsers])
async def approve_access_request_direct(
    id: UUID,
    current_admin: AdminUser = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service)
):
    req = await service.approve_via_panel(request_id=id, resolved_by=current_admin.id)
    return AccessRequestResponse.model_validate(req)

@router.get("/team", response_model=TeamMemberListResponse, dependencies=[CanManageUsers])
async def get_team(
    service: AdminService = Depends(get_admin_service)
):
    members = await service.get_team_members()
    return TeamMemberListResponse(
        items=[TeamMemberResponse.model_validate(m) for m in members],
        total=len(members)
    )

@router.patch("/team/{id}/role", response_model=TeamMemberResponse, dependencies=[CanManageUsers])
async def update_team_member_role(
    id: UUID,
    data: UpdateRoleRequest,
    current_admin: AdminUser = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service)
):
    profile = await service.update_team_member_role(member_id=id, role=data.role, current_admin_id=current_admin.id)
    return TeamMemberResponse.model_validate(profile)

@router.delete("/team/{id}", status_code=204, dependencies=[CanManageUsers])
async def delete_team_member(
    id: UUID,
    current_admin: AdminUser = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service)
):
    await service.delete_team_member(member_id=id, current_admin_id=current_admin.id)
    return Response(status_code=204)
