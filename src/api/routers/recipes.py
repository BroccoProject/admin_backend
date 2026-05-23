import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from domain.exceptions import ResourceInUseError

from api.schemas.recipe import RecipeListResponse, RecipeResponse, RecipeDeletePreview, RecipeUpdate
from api.schemas.recipe_draft import RecipeDraft
from services.recipes.recipe_service import RecipeService
from api.dependencies.services import get_recipe_service

router = APIRouter(prefix="/recipes", tags=["Recipes"])

@router.post("", response_model=dict)
async def create_recipe(
    draft: RecipeDraft,
    service: RecipeService = Depends(get_recipe_service)
):
    """Save a fully parsed and verified recipe draft to the database."""
    try:
        recipe_id = await service.create_recipe_from_draft(draft)
        return {"id": recipe_id, "status": "success"}
    except Exception as e:
        # TODO: Better exception handling mapped to domain layer
        raise HTTPException(status_code=500, detail=f"Error saving recipe: {str(e)}")

@router.get("", response_model=RecipeListResponse)
async def list_recipes(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    sort_by: str = Query("title"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    service: RecipeService = Depends(get_recipe_service),
):
    """List recipes with pagination, search, and sorting."""
    recipes, total = await service.get_recipes(
        page=page, page_size=page_size, search=search, sort_by=sort_by, sort_order=sort_order
    )
    total_pages = max(1, math.ceil(total / page_size))

    return RecipeListResponse(
        items=[RecipeResponse.model_validate(r) for r in recipes],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: UUID,
    service: RecipeService = Depends(get_recipe_service),
):
    """Get a single recipe by ID."""
    recipe = await service.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return RecipeResponse.model_validate(recipe)


@router.get("/{recipe_id}/delete-preview", response_model=RecipeDeletePreview)
async def get_recipe_delete_preview(
    recipe_id: UUID,
    service: RecipeService = Depends(get_recipe_service),
):
    """Return cascade impact counts before deleting a recipe."""
    recipe = await service.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    preview = await service.get_delete_preview(recipe_id)
    return RecipeDeletePreview(
        recipe_ingredients=preview.recipe_ingredients,
        steps=preview.steps,
        step_ingredients=preview.step_ingredients,
        step_items=preview.step_items,
        roadmap_nodes=preview.roadmap_nodes,
    )


@router.patch("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: UUID,
    update_data: RecipeUpdate,
    service: RecipeService = Depends(get_recipe_service),
):
    """Update a single recipe by ID."""
    updated_recipe = await service.update_recipe(recipe_id, update_data.model_dump(exclude_unset=True))
    if not updated_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return RecipeResponse.model_validate(updated_recipe)


@router.delete("/{recipe_id}", status_code=200)
async def delete_recipe(
    recipe_id: UUID,
    service: RecipeService = Depends(get_recipe_service),
):
    """Delete a recipe. Returns 409 if blocked by a roadmap node reference."""
    try:
        deleted = await service.delete_recipe(recipe_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return {"detail": "Recipe deleted successfully"}
    except ResourceInUseError as e:
        error_msg = e.detail or str(e)
        if "DETAIL:" in error_msg:
            detail_part = error_msg.split("DETAIL:")[1].strip()
            detail = f"Cannot delete recipe: {detail_part}"
        else:
            detail = (
                "Cannot delete this recipe because it is still used by one or more "
                "roadmap nodes. Remove or reassign those nodes first."
            )
        raise HTTPException(status_code=409, detail=detail)
