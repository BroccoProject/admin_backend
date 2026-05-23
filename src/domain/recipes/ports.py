import abc
from uuid import UUID
from typing import Any
from domain.recipes.models import RecipeDomain, RecipeDeletePreviewDomain

class IRecipeRepository(abc.ABC):
    @abc.abstractmethod
    async def get_recipes(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        sort_by: str = "title",
        sort_order: str = "asc",
    ) -> tuple[list[RecipeDomain], int]:
        pass

    @abc.abstractmethod
    async def get_recipe_by_id(self, recipe_id: UUID) -> RecipeDomain | None:
        pass

    @abc.abstractmethod
    async def get_delete_preview(self, recipe_id: UUID) -> RecipeDeletePreviewDomain:
        pass

    @abc.abstractmethod
    async def delete_recipe(self, recipe_id: UUID) -> bool:
        pass

    @abc.abstractmethod
    async def update_recipe(self, recipe_id: UUID, update_data: dict) -> RecipeDomain | None:
        pass

    @abc.abstractmethod
    async def create_recipe_from_draft(self, draft: Any) -> UUID:
        """
        draft is of type api.schemas.recipe_draft.RecipeDraft, but we avoid importing it here
        to keep the domain strictly decoupled from api schemas. In a purist approach, we'd map
        it to a domain draft object first. For simplicity without breaking logic, we use Any.
        """
        pass
