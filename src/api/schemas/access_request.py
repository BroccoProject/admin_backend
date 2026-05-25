from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class AccessRequestCreate(BaseModel):
    email: EmailStr
    message: str | None = None

class AccessRequestResponse(BaseModel):
    id: UUID
    email: str
    message: str | None
    status: str
    created_at: datetime
    resolved_at: datetime | None

    model_config = {"from_attributes": True}

class AccessRequestListResponse(BaseModel):
    items: list[AccessRequestResponse]
    total: int

class TeamMemberResponse(BaseModel):
    id: UUID
    email: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}

class TeamMemberListResponse(BaseModel):
    items: list[TeamMemberResponse]
    total: int

class UpdateRoleRequest(BaseModel):
    role: str
