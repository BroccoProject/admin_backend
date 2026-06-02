import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from domain.exceptions import ResourceInUseError

from api.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    CategoryCreateWithNodes,
    CategoryNodeResponse,
    CategoryUpdateWithNodes,
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
    category_area: str | None = Query(None),
    category_type: str | None = Query(None),
    service: CategoryService = Depends(get_category_service),
):
    """List categories with pagination, search, and sorting."""
    categories, total = await service.get_categories(
        page=page,
        page_size=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        category_area=category_area,
        category_type=category_type,
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
    data: CategoryCreateWithNodes,
    service: CategoryService = Depends(get_category_service),
):
    """Create a new category with optional roadmap nodes."""
    data_dict = data.model_dump()
    nodes_data = data_dict.pop("nodes", [])
    if nodes_data:
        category = await service.create_category_with_nodes(data_dict, nodes_data)
    else:
        category = await service.create_category(data_dict)
    return CategoryResponse.model_validate(category)


@router.get("/{category_id}/nodes", response_model=list[CategoryNodeResponse], dependencies=[CanReadRecipes])
async def get_category_nodes(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
):
    """Get all roadmap nodes for a given category."""
    category = await service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    nodes = await service.get_category_nodes(category_id)
    return nodes


@router.patch("/{category_id}", response_model=CategoryResponse, dependencies=[CanManageUsers])
async def update_category(
    category_id: UUID,
    data: CategoryUpdateWithNodes,
    service: CategoryService = Depends(get_category_service),
):
    """Update a category and its nodes."""
    data_dict = data.model_dump(exclude_unset=True)
    if "nodes" in data_dict:
        nodes_data = data_dict.pop("nodes")
        if nodes_data is not None:
            category = await service.update_category_with_nodes(category_id, data_dict, nodes_data)
        else:
            category = await service.update_category(category_id, data_dict)
    else:
        category = await service.update_category(category_id, data_dict)
        
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
