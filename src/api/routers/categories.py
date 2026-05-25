import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from domain.exceptions import ResourceInUseError

from api.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
)
from services.categories.category_service import CategoryService
from api.dependencies.services import get_category_service
from api.dependencies.auth import CanReadRecipes, CanManageUsers

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=CategoryListResponse, dependencies=[CanReadRecipes])
async def list_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    sort_by: str = Query("title"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    service: CategoryService = Depends(get_category_service),
):
    """List categories with pagination, search, and sorting."""
    categories, total = await service.get_categories(
        page=page, page_size=page_size, search=search, sort_by=sort_by, sort_order=sort_order
    )
    total_pages = max(1, math.ceil(total / page_size))

    return CategoryListResponse(
        items=[CategoryResponse.model_validate(c) for c in categories],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{category_id}", response_model=CategoryResponse, dependencies=[CanReadRecipes])
async def get_category(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
):
    """Get a single category by ID."""
    category = await service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse.model_validate(category)


@router.get("/{category_id}/delete-preview", dependencies=[CanReadRecipes])
async def get_category_delete_preview(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
):
    """Return cascade impact counts before deleting a category."""
    category = await service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    preview = await service.get_delete_preview(category_id)
    return preview


@router.post("", response_model=CategoryResponse, status_code=201, dependencies=[CanManageUsers])
async def create_category(
    data: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    """Create a new category."""
    category = await service.create_category(data.model_dump())
    return CategoryResponse.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryResponse, dependencies=[CanManageUsers])
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
):
    """Partially update a category."""
    category = await service.update_category(category_id, data.model_dump(exclude_unset=True))
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}", status_code=200, dependencies=[CanManageUsers])
async def delete_category(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
):
    """Delete a category. Returns an error message if constrained by related data."""
    try:
        deleted = await service.delete_category(category_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"detail": "Category deleted successfully"}
    except ResourceInUseError as e:
        error_msg = e.detail or str(e)
        if "DETAIL:" in error_msg:
            detail_part = error_msg.split("DETAIL:")[1].strip()
            detail = f"Cannot delete category: {detail_part}"
        else:
            detail = f"Cannot delete category due to a database constraint: {error_msg}"
        raise HTTPException(status_code=409, detail=detail)
