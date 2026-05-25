from uuid import UUID

from domain.categories.ports import ICategoryRepository
from domain.categories.models import CategoryDomain


class CategoryService:
    def __init__(self, repository: ICategoryRepository):
        self.repository = repository

    async def get_categories(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        sort_by: str = "title",
        sort_order: str = "asc",
    ) -> tuple[list[CategoryDomain], int]:
        return await self.repository.get_categories(
            page=page,
            page_size=page_size,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def get_category_by_id(self, category_id: UUID) -> CategoryDomain | None:
        return await self.repository.get_category_by_id(category_id)

    async def get_delete_preview(self, category_id: UUID) -> dict:
        return await self.repository.get_delete_preview(category_id)

    async def create_category(self, data: dict) -> CategoryDomain:
        return await self.repository.create_category(data)

    async def update_category(self, category_id: UUID, data: dict) -> CategoryDomain | None:
        return await self.repository.update_category(category_id, data)

    async def delete_category(self, category_id: UUID) -> bool:
        return await self.repository.delete_category(category_id)
