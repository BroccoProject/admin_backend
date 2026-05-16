from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.recipe.recipe import Recipe
from infrastructure.database.models.recipe.recipe_ingredient import RecipeIngredient
from infrastructure.database.models.recipe.recipe_step import RecipeStep
from infrastructure.database.models.recipe.step_ingredient import StepIngredient
from infrastructure.database.models.recipe.step_item import StepItem
from infrastructure.database.models.roadmap.roadmap_node import RoadmapNode
from infrastructure.database.models.roadmap.category import Category
from api.schemas.recipe import RecipeResponse, RecipeDeletePreview


async def get_recipes(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    sort_by: str = "title",
    sort_order: str = "asc",
) -> tuple[list[RecipeResponse], int]:
    """Fetch paginated recipes with optional search and sorting.

    Also resolves roadmap category titles for each recipe.
    """
    query = select(Recipe)
    count_query = select(func.count()).select_from(Recipe)

    if search:
        search_filter = Recipe.title.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    allowed_sort_fields = {"title", "difficulty_level", "duration_minutes", "category", "area"}
    if sort_by in allowed_sort_fields:
        column = getattr(Recipe, sort_by)
        query = query.order_by(column.desc() if sort_order == "desc" else column.asc())
    else:
        query = query.order_by(Recipe.title.asc())

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    recipes: list[Recipe] = list(result.scalars().all())

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Resolve roadmap category titles for the returned page
    recipe_ids = [r.id for r in recipes]
    category_map: dict[UUID, list[str]] = {r.id: [] for r in recipes}

    if recipe_ids:
        cat_query = (
            select(RoadmapNode.recipe_id, Category.title)
            .join(Category, RoadmapNode.category_id == Category.id)
            .where(RoadmapNode.recipe_id.in_(recipe_ids))
        )
        cat_result = await db.execute(cat_query)
        for row in cat_result.all():
            recipe_id, cat_title = row
            if recipe_id in category_map:
                if cat_title not in category_map[recipe_id]:
                    category_map[recipe_id].append(cat_title)

    response_items = [
        RecipeResponse(
            id=r.id,
            title=r.title,
            image_url=r.image_url,
            difficulty_level=r.difficulty_level,
            duration_minutes=r.duration_minutes,
            category=r.category,
            area=r.area,
            tags=r.tags,
            roadmap_category_titles=category_map.get(r.id, []),
        )
        for r in recipes
    ]

    return response_items, total


async def get_recipe_by_id(db: AsyncSession, recipe_id: UUID) -> RecipeResponse | None:
    """Fetch a single recipe by ID, with roadmap category titles."""
    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        return None

    cat_query = (
        select(Category.title)
        .join(RoadmapNode, RoadmapNode.category_id == Category.id)
        .where(RoadmapNode.recipe_id == recipe_id)
        .distinct()
    )
    cat_result = await db.execute(cat_query)
    category_titles = [row[0] for row in cat_result.all()]

    return RecipeResponse(
        id=recipe.id,
        title=recipe.title,
        image_url=recipe.image_url,
        difficulty_level=recipe.difficulty_level,
        duration_minutes=recipe.duration_minutes,
        category=recipe.category,
        area=recipe.area,
        tags=recipe.tags,
        roadmap_category_titles=category_titles,
    )


async def get_delete_preview(db: AsyncSession, recipe_id: UUID) -> RecipeDeletePreview:
    """Return cascade/block impact counts before deleting a recipe."""

    async def count_query(model, fk_col):
        r = await db.execute(
            select(func.count()).select_from(model).where(fk_col == recipe_id)
        )
        return r.scalar() or 0

    recipe_ingredients_count = await count_query(RecipeIngredient, RecipeIngredient.recipe_id)
    steps_count = await count_query(RecipeStep, RecipeStep.recipe_id)
    roadmap_nodes_count = await count_query(RoadmapNode, RoadmapNode.recipe_id)

    # step_ingredients and step_items cascade from steps, not recipe directly
    step_ids_result = await db.execute(
        select(RecipeStep.id).where(RecipeStep.recipe_id == recipe_id)
    )
    step_ids = [row[0] for row in step_ids_result.all()]

    step_ingredients_count = 0
    step_items_count = 0
    if step_ids:
        si_result = await db.execute(
            select(func.count()).select_from(StepIngredient).where(StepIngredient.step_id.in_(step_ids))
        )
        step_ingredients_count = si_result.scalar() or 0

        sit_result = await db.execute(
            select(func.count()).select_from(StepItem).where(StepItem.step_id.in_(step_ids))
        )
        step_items_count = sit_result.scalar() or 0

    return RecipeDeletePreview(
        recipe_ingredients=recipe_ingredients_count,
        steps=steps_count,
        step_ingredients=step_ingredients_count,
        step_items=step_items_count,
        roadmap_nodes=roadmap_nodes_count,
    )


async def delete_recipe(db: AsyncSession, recipe_id: UUID) -> bool:
    """Delete a recipe. Returns True on success.

    Will raise IntegrityError (caught in the API layer as HTTP 409) if any
    roadmap_node still references this recipe — the FK is RESTRICT.
    """
    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    if not recipe:
        return False

    await db.delete(recipe)
    await db.commit()
    return True
