import math
from typing import Any
from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from infrastructure.database.models.recipe.recipe import Recipe
from infrastructure.database.models.recipe.recipe_ingredient import RecipeIngredient
from infrastructure.database.models.recipe.recipe_step import RecipeStep
from infrastructure.database.models.recipe.step_ingredient import StepIngredient
from infrastructure.database.models.recipe.step_item import StepItem
from infrastructure.database.models.roadmap.roadmap_node import RoadmapNode
from infrastructure.database.models.roadmap.category import Category
from infrastructure.database.models.core.ingredient import Ingredient
from infrastructure.database.models.core.item import Item

from domain.recipes.ports import IRecipeRepository
from domain.recipes.models import RecipeDomain, RecipeDeletePreviewDomain
from domain.exceptions import ResourceInUseError


class SQLRecipeRepository(IRecipeRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_domain(self, recipe: Recipe, category_titles: list[str] = None) -> RecipeDomain:
        return RecipeDomain(
            id=recipe.id,
            title=recipe.title,
            description=recipe.description,
            image_url=recipe.image_url,
            difficulty_level=recipe.difficulty_level,
            duration_minutes=recipe.duration_minutes,
            youtube_url=recipe.youtube_url,
            tags=recipe.tags,
            category=recipe.category,
            area=recipe.area,
            source_url=recipe.source_url,
            roadmap_category_titles=category_titles or [],
        )

    async def get_recipes(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        sort_by: str = "title",
        sort_order: str = "asc",
        category: str | None = None,
        difficulty: str | None = None,
        tag: str | None = None,
    ) -> tuple[list[RecipeDomain], int]:
        query = select(Recipe)
        count_query = select(func.count()).select_from(Recipe)

        if search:
            search_filter = Recipe.title.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        if category:
            query = query.where(Recipe.category == category)
            count_query = count_query.where(Recipe.category == category)

        if difficulty:
            query = query.where(Recipe.difficulty_level == difficulty)
            count_query = count_query.where(Recipe.difficulty_level == difficulty)

        if tag:
            query = query.where(Recipe.tags.any(tag))
            count_query = count_query.where(Recipe.tags.any(tag))

        allowed_sort_fields = {"title", "difficulty_level", "duration_minutes", "category", "area"}
        if sort_by in allowed_sort_fields:
            column = getattr(Recipe, sort_by)
            query = query.order_by(column.desc() if sort_order == "desc" else column.asc())
        else:
            query = query.order_by(Recipe.title.asc())

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        recipes = list(result.scalars().all())

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        recipe_ids = [r.id for r in recipes]
        category_map: dict[UUID, list[str]] = {r.id: [] for r in recipes}

        if recipe_ids:
            cat_query = (
                select(RoadmapNode.recipe_id, Category.title)
                .join(Category, RoadmapNode.category_id == Category.id)
                .where(RoadmapNode.recipe_id.in_(recipe_ids))
            )
            cat_result = await self.db.execute(cat_query)
            for row in cat_result.all():
                recipe_id, cat_title = row
                if recipe_id in category_map:
                    if cat_title not in category_map[recipe_id]:
                        category_map[recipe_id].append(cat_title)

        return [self._to_domain(r, category_map.get(r.id, [])) for r in recipes], total

    async def get_recipe_by_id(self, recipe_id: UUID) -> RecipeDomain | None:
        result = await self.db.execute(select(Recipe).where(Recipe.id == recipe_id))
        recipe = result.scalar_one_or_none()
        if not recipe:
            return None

        cat_query = (
            select(Category.title)
            .join(RoadmapNode, RoadmapNode.category_id == Category.id)
            .where(RoadmapNode.recipe_id == recipe_id)
            .distinct()
        )
        cat_result = await self.db.execute(cat_query)
        category_titles = [row[0] for row in cat_result.all()]

        return self._to_domain(recipe, category_titles)

    async def get_recipe_detail(self, recipe_id: UUID) -> dict | None:
        """Load recipe with all nested relationships eager-loaded."""
        query = (
            select(Recipe)
            .where(Recipe.id == recipe_id)
            .options(
                selectinload(Recipe.ingredients).selectinload(RecipeIngredient.ingredient),
                selectinload(Recipe.steps)
                    .selectinload(RecipeStep.ingredients)
                    .selectinload(StepIngredient.ingredient),
                selectinload(Recipe.steps)
                    .selectinload(RecipeStep.items)
                    .selectinload(StepItem.item),
            )
        )
        result = await self.db.execute(query)
        recipe = result.scalar_one_or_none()
        if not recipe:
            return None

        # Get roadmap category titles
        cat_query = (
            select(Category.title)
            .join(RoadmapNode, RoadmapNode.category_id == Category.id)
            .where(RoadmapNode.recipe_id == recipe_id)
            .distinct()
        )
        cat_result = await self.db.execute(cat_query)
        category_titles = [row[0] for row in cat_result.all()]

        # Sort steps by step_number, ingredients by sort_order
        sorted_steps = sorted(recipe.steps, key=lambda s: s.step_number)

        return {
            "id": recipe.id,
            "title": recipe.title,
            "description": recipe.description,
            "image_url": recipe.image_url,
            "difficulty_level": recipe.difficulty_level,
            "duration_minutes": recipe.duration_minutes,
            "category": recipe.category,
            "area": recipe.area,
            "tags": recipe.tags,
            "youtube_url": recipe.youtube_url,
            "source_url": recipe.source_url,
            "roadmap_category_titles": category_titles,
            "ingredients": [
                {
                    "id": ri.id,
                    "ingredient": {
                        "id": ri.ingredient.id,
                        "name": ri.ingredient.name,
                        "default_unit": ri.ingredient.default_unit,
                    },
                    "amount": float(ri.amount) if ri.amount is not None else None,
                    "unit": ri.unit,
                    "sort_order": ri.sort_order,
                }
                for ri in sorted(recipe.ingredients, key=lambda i: i.sort_order)
            ],
            "steps": [
                {
                    "id": step.id,
                    "step_number": step.step_number,
                    "instruction": step.instruction,
                    "duration_seconds": step.duration_seconds,
                    "ingredients": [
                        {
                            "id": si.id,
                            "ingredient": {
                                "id": si.ingredient.id,
                                "name": si.ingredient.name,
                                "default_unit": si.ingredient.default_unit,
                            },
                            "amount": float(si.amount) if si.amount is not None else None,
                            "unit": si.unit,
                            "actions": [a.value if hasattr(a, 'value') else str(a) for a in (si.actions or [])],
                        }
                        for si in step.ingredients
                    ],
                    "items": [
                        {
                            "id": sit.id,
                            "item": {
                                "id": sit.item.id,
                                "name": sit.item.name,
                                "tag": sit.item.tag.value if hasattr(sit.item.tag, 'value') else str(sit.item.tag),
                            },
                        }
                        for sit in step.items
                    ],
                }
                for step in sorted_steps
            ],
        }

    async def get_delete_preview(self, recipe_id: UUID) -> RecipeDeletePreviewDomain:
        async def count_query(model, fk_col):
            r = await self.db.execute(
                select(func.count()).select_from(model).where(fk_col == recipe_id)
            )
            return r.scalar() or 0

        recipe_ingredients_count = await count_query(RecipeIngredient, RecipeIngredient.recipe_id)
        steps_count = await count_query(RecipeStep, RecipeStep.recipe_id)
        roadmap_nodes_count = await count_query(RoadmapNode, RoadmapNode.recipe_id)

        step_ids_result = await self.db.execute(
            select(RecipeStep.id).where(RecipeStep.recipe_id == recipe_id)
        )
        step_ids = [row[0] for row in step_ids_result.all()]

        step_ingredients_count = 0
        step_items_count = 0
        if step_ids:
            si_result = await self.db.execute(
                select(func.count()).select_from(StepIngredient).where(StepIngredient.step_id.in_(step_ids))
            )
            step_ingredients_count = si_result.scalar() or 0

            sit_result = await self.db.execute(
                select(func.count()).select_from(StepItem).where(StepItem.step_id.in_(step_ids))
            )
            step_items_count = sit_result.scalar() or 0

        return RecipeDeletePreviewDomain(
            recipe_ingredients=recipe_ingredients_count,
            steps=steps_count,
            step_ingredients=step_ingredients_count,
            step_items=step_items_count,
            roadmap_nodes=roadmap_nodes_count,
        )

    async def delete_recipe(self, recipe_id: UUID) -> bool:
        result = await self.db.execute(select(Recipe).where(Recipe.id == recipe_id))
        recipe = result.scalar_one_or_none()
        if not recipe:
            return False

        try:
            await self.db.delete(recipe)
            await self.db.commit()
            return True
        except IntegrityError as e:
            await self.db.rollback()
            error_msg = str(e.orig) if hasattr(e, "orig") and e.orig else str(e)
            raise ResourceInUseError("Database constraint violation", detail=error_msg)


    async def update_recipe(self, recipe_id: UUID, update_data: dict) -> RecipeDomain | None:
        result = await self.db.execute(select(Recipe).where(Recipe.id == recipe_id))
        recipe = result.scalar_one_or_none()
        if not recipe:
            return None

        for key, value in update_data.items():
            setattr(recipe, key, value)

        await self.db.commit()
        await self.db.refresh(recipe)

        return await self.get_recipe_by_id(recipe_id)

    async def update_recipe_full(self, recipe_id: UUID, update_data: Any) -> dict | None:
        """Full replacement: update top-level fields, then delete-and-recreate all nested data."""
        result = await self.db.execute(select(Recipe).where(Recipe.id == recipe_id))
        recipe = result.scalar_one_or_none()
        if not recipe:
            return None

        # Update top-level fields
        top_fields = [
            "title", "description", "image_url", "difficulty_level",
            "duration_minutes", "youtube_url", "tags", "category", "area", "source_url"
        ]
        for field in top_fields:
            value = getattr(update_data, field, None)
            if value is not None:
                setattr(recipe, field, value)

        # Delete existing nested data: step_items and step_ingredients first (via steps), then steps and recipe_ingredients
        step_ids_result = await self.db.execute(
            select(RecipeStep.id).where(RecipeStep.recipe_id == recipe_id)
        )
        step_ids = [row[0] for row in step_ids_result.all()]

        if step_ids:
            await self.db.execute(
                delete(StepItem).where(StepItem.step_id.in_(step_ids))
            )
            await self.db.execute(
                delete(StepIngredient).where(StepIngredient.step_id.in_(step_ids))
            )

        await self.db.execute(
            delete(RecipeStep).where(RecipeStep.recipe_id == recipe_id)
        )
        await self.db.execute(
            delete(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id)
        )

        # Re-create recipe ingredients
        for ing_data in update_data.ingredients:
            recipe_ing = RecipeIngredient(
                recipe_id=recipe_id,
                ingredient_id=ing_data.ingredient_id,
                amount=ing_data.amount,
                unit=ing_data.unit,
                sort_order=ing_data.sort_order,
            )
            self.db.add(recipe_ing)

        # Re-create steps with nested ingredients and items
        for step_data in update_data.steps:
            step = RecipeStep(
                recipe_id=recipe_id,
                step_number=step_data.step_number,
                instruction=step_data.instruction,
                instruction_i18n={},
                duration_seconds=step_data.duration_seconds,
            )
            self.db.add(step)
            await self.db.flush()

            for s_ing_data in step_data.ingredients:
                step_ing = StepIngredient(
                    step_id=step.id,
                    ingredient_id=s_ing_data.ingredient_id,
                    amount=s_ing_data.amount,
                    unit=s_ing_data.unit,
                    actions=s_ing_data.actions if s_ing_data.actions else [],
                )
                self.db.add(step_ing)

            for s_item_data in step_data.items:
                step_item = StepItem(
                    step_id=step.id,
                    item_id=s_item_data.item_id,
                )
                self.db.add(step_item)

        await self.db.commit()

        return await self.get_recipe_detail(recipe_id)

    async def get_all_ingredients(self) -> list[Any]:
        result = await self.db.execute(select(Ingredient).order_by(Ingredient.name.asc()))
        return list(result.scalars().all())

    async def get_all_items(self) -> list[Any]:
        result = await self.db.execute(select(Item).order_by(Item.name.asc()))
        return list(result.scalars().all())

    async def create_recipe_from_draft(self, draft: Any) -> UUID:
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
        self.db.add(recipe)
        await self.db.flush()

        async def upsert_ingredient(name: str, default_unit: str | None, name_i18n: dict) -> UUID:
            stmt = insert(Ingredient).values(
                name=name,
                default_unit=default_unit,
                name_i18n=name_i18n
            ).on_conflict_do_update(
                index_elements=['name'],
                set_={'default_unit': default_unit, 'name_i18n': name_i18n}
            ).returning(Ingredient.id)
            result = await self.db.execute(stmt)
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
            result = await self.db.execute(stmt)
            return result.scalar_one()

        for ing_draft in draft.ingredients:
            ing_id = await upsert_ingredient(ing_draft.name, ing_draft.unit, {})
            recipe_ing = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ing_id,
                amount=ing_draft.amount,
                unit=ing_draft.unit,
                sort_order=ing_draft.sort_order
            )
            self.db.add(recipe_ing)

        for step_draft in draft.steps:
            step = RecipeStep(
                recipe_id=recipe.id,
                step_number=step_draft.step_number,
                instruction=step_draft.instruction,
                instruction_i18n=step_draft.instruction_i18n,
                duration_seconds=step_draft.duration_seconds
            )
            self.db.add(step)
            await self.db.flush()

            for s_ing_draft in step_draft.ingredients:
                ing_id = await upsert_ingredient(s_ing_draft.name, s_ing_draft.unit, s_ing_draft.name_i18n)
                step_ing = StepIngredient(
                    step_id=step.id,
                    ingredient_id=ing_id,
                    amount=s_ing_draft.amount,
                    unit=s_ing_draft.unit,
                    actions=[a.value for a in s_ing_draft.actions]
                )
                self.db.add(step_ing)

            for s_item_draft in step_draft.items:
                item_id = await upsert_item(s_item_draft.name, s_item_draft.tag, s_item_draft.name_i18n)
                step_item = StepItem(
                    step_id=step.id,
                    item_id=item_id
                )
                self.db.add(step_item)

        await self.db.commit()
        return recipe.id
