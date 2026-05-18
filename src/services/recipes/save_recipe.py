from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from api.schemas.recipe_draft import RecipeDraft
from infrastructure.database.models.core.ingredient import Ingredient
from infrastructure.database.models.core.item import Item
from infrastructure.database.models.recipe.recipe import Recipe
from infrastructure.database.models.recipe.recipe_ingredient import RecipeIngredient
from infrastructure.database.models.recipe.recipe_step import RecipeStep
from infrastructure.database.models.recipe.step_ingredient import StepIngredient
from infrastructure.database.models.recipe.step_item import StepItem

async def create_recipe_from_draft(db: AsyncSession, draft: RecipeDraft) -> UUID:
    """Persists a parsed RecipeDraft directly into the Postgres database.
    Uses native upsert (ON CONFLICT DO UPDATE) for ingredients and items
    to avoid duplicates while ensuring we return the ID.
    """
    
    # 1. Insert Recipe
    recipe = Recipe(
        title=draft.title,
        title_i18n=draft.title_i18n,
        description=draft.description,
        description_i18n=draft.description_i18n,
        image_url=draft.image_url,
        difficulty_level=draft.difficulty,
        duration_minutes=draft.duration_minutes,
        youtube_url=draft.youtube_url,
        tags=draft.tags,
        category=draft.category,
        area=draft.area,
        source_url=draft.source_url,
    )
    db.add(recipe)
    await db.flush()  # To get recipe.id

    async def upsert_ingredient(name: str, default_unit: str | None, name_i18n: dict) -> UUID:
        stmt = insert(Ingredient).values(
            name=name,
            default_unit=default_unit,
            name_i18n=name_i18n
        ).on_conflict_do_update(
            index_elements=['name'],
            set_={'default_unit': default_unit, 'name_i18n': name_i18n}
        ).returning(Ingredient.id)
        result = await db.execute(stmt)
        return result.scalar_one()

    async def upsert_item(name: str, tag: str, name_i18n: dict) -> UUID:
        stmt = insert(Item).values(
            name=name,
            tag=tag,
            name_i18n=name_i18n
        ).on_conflict_do_update(
            index_elements=['name'],
            set_={'tag': tag, 'name_i18n': name_i18n}
        ).returning(Item.id)
        result = await db.execute(stmt)
        return result.scalar_one()

    # 2. Insert Recipe Ingredients
    for ing_draft in draft.ingredients:
        ing_id = await upsert_ingredient(ing_draft.name, ing_draft.unit, {})
        recipe_ing = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ing_id,
            amount=ing_draft.amount,
            unit=ing_draft.unit,
            sort_order=ing_draft.sort_order
        )
        db.add(recipe_ing)

    # 3. Insert Steps, Step Ingredients, and Step Items
    for step_draft in draft.steps:
        step = RecipeStep(
            recipe_id=recipe.id,
            step_number=step_draft.step_number,
            instruction=step_draft.instruction,
            instruction_i18n=step_draft.instruction_i18n,
            duration_seconds=step_draft.duration_seconds
        )
        db.add(step)
        await db.flush()

        for s_ing_draft in step_draft.ingredients:
            ing_id = await upsert_ingredient(s_ing_draft.name, s_ing_draft.unit, s_ing_draft.name_i18n)
            step_ing = StepIngredient(
                step_id=step.id,
                ingredient_id=ing_id,
                amount=s_ing_draft.amount,
                unit=s_ing_draft.unit,
                actions=[a.value for a in s_ing_draft.actions]
            )
            db.add(step_ing)

        for s_item_draft in step_draft.items:
            item_id = await upsert_item(s_item_draft.name, s_item_draft.tag, s_item_draft.name_i18n)
            step_item = StepItem(
                step_id=step.id,
                item_id=item_id
            )
            db.add(step_item)

    await db.commit()
    return recipe.id
