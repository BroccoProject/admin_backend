from typing import Any
from uuid import UUID

from domain.recipes.ports import IRecipeRepository
from domain.recipes.models import RecipeDomain, RecipeDeletePreviewDomain


class RecipeService:
    def __init__(self, repository: IRecipeRepository):
        self.repository = repository

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
        return await self.repository.get_recipes(
            page=page,
            page_size=page_size,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            category=category,
            difficulty=difficulty,
            tag=tag,
        )

    async def get_recipe_by_id(self, recipe_id: UUID) -> RecipeDomain | None:
        return await self.repository.get_recipe_by_id(recipe_id)

    async def get_recipe_detail(self, recipe_id: UUID) -> dict | None:
        return await self.repository.get_recipe_detail(recipe_id)

    async def get_delete_preview(self, recipe_id: UUID) -> RecipeDeletePreviewDomain:
        return await self.repository.get_delete_preview(recipe_id)

    async def delete_recipe(self, recipe_id: UUID) -> bool:
        return await self.repository.delete_recipe(recipe_id)

    async def update_recipe(self, recipe_id: UUID, update_data: dict) -> RecipeDomain | None:
        return await self.repository.update_recipe(recipe_id, update_data)

    async def update_recipe_full(self, recipe_id: UUID, update_data: Any) -> dict | None:
        return await self.repository.update_recipe_full(recipe_id, update_data)

    async def create_recipe_from_draft(self, draft: Any) -> UUID:
        return await self.repository.create_recipe_from_draft(draft)

    async def get_all_ingredients(self) -> list[Any]:
        return await self.repository.get_all_ingredients()

    async def get_all_items(self) -> list[Any]:
        return await self.repository.get_all_items()
