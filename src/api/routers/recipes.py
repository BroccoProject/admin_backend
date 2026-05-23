import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db
from api.schemas.recipe import RecipeListResponse, RecipeResponse, RecipeDeletePreview, RecipeUpdate
from api.schemas.recipe_draft import RecipeDraft
from services.recipes import crud as recipe_crud
from services.recipes.save_recipe import create_recipe_from_draft

router = APIRouter(prefix="/recipes", tags=["Recipes"])

@router.post("", response_model=dict)
async def create_recipe(
    draft: RecipeDraft,
    db: AsyncSession = Depends(get_db)
):
    """Save a fully parsed and verified recipe draft to the database."""
    try:
        recipe_id = await create_recipe_from_draft(db, draft)
        return {"id": recipe_id, "status": "success"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving recipe: {str(e)}")

@router.get("", response_model=RecipeListResponse)
async def list_recipes(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    sort_by: str = Query("title"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """List recipes with pagination, search, and sorting."""
    recipes, total = await recipe_crud.get_recipes(
        db, page=page, page_size=page_size, search=search, sort_by=sort_by, sort_order=sort_order
    )
    total_pages = max(1, math.ceil(total / page_size))

    return RecipeListResponse(
        items=recipes,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single recipe by ID."""
    recipe = await recipe_crud.get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.get("/{recipe_id}/delete-preview", response_model=RecipeDeletePreview)
async def get_recipe_delete_preview(
    recipe_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return cascade impact counts before deleting a recipe."""
    recipe = await recipe_crud.get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return await recipe_crud.get_delete_preview(db, recipe_id)


@router.patch("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: UUID,
    update_data: RecipeUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a single recipe by ID."""
    updated_recipe = await recipe_crud.update_recipe(db, recipe_id, update_data)
    if not updated_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return updated_recipe


@router.delete("/{recipe_id}", status_code=200)
async def delete_recipe(
    recipe_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a recipe. Returns 409 if blocked by a roadmap node reference."""
    try:
        deleted = await recipe_crud.delete_recipe(db, recipe_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return {"detail": "Recipe deleted successfully"}
    except IntegrityError as e:
        await db.rollback()
        error_msg = str(e.orig) if hasattr(e, "orig") and e.orig else str(e)
        if "DETAIL:" in error_msg:
            detail_part = error_msg.split("DETAIL:")[1].strip()
            detail = f"Cannot delete recipe: {detail_part}"
        else:
            detail = (
                "Cannot delete this recipe because it is still used by one or more "
                "roadmap nodes. Remove or reassign those nodes first."
            )
        raise HTTPException(status_code=409, detail=detail)
