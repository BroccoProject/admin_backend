import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from api.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
)
from services.categories import crud as category_crud

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=CategoryListResponse)
async def list_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    sort_by: str = Query("title"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List categories with pagination, search, and sorting."""
    categories, total = await category_crud.get_categories(
        db, page=page, page_size=page_size, search=search, sort_by=sort_by, sort_order=sort_order
    )
    total_pages = max(1, math.ceil(total / page_size))

    return CategoryListResponse(
        items=[CategoryResponse.model_validate(c) for c in categories],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single category by ID."""
    category = await category_crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse.model_validate(category)


@router.get("/{category_id}/delete-preview")
async def get_category_delete_preview(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return cascade impact counts before deleting a category."""
    category = await category_crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    preview = await category_crud.get_delete_preview(db, category_id)
    return preview


@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new category."""
    category = await category_crud.create_category(db, data)
    return CategoryResponse.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Partially update a category."""
    category = await category_crud.update_category(db, category_id, data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}", status_code=200)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a category. Returns an error message if constrained by related data."""
    try:
        deleted = await category_crud.delete_category(db, category_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"detail": "Category deleted successfully"}
    except IntegrityError as e:
        await db.rollback()
        error_msg = str(e.orig) if hasattr(e, "orig") and e.orig else str(e)
        if "DETAIL:" in error_msg:
            detail_part = error_msg.split("DETAIL:")[1].strip()
            detail = f"Cannot delete category: {detail_part}"
        else:
            detail = f"Cannot delete category due to a database constraint: {error_msg}"
        raise HTTPException(status_code=409, detail=detail)
