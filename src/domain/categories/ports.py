import abc
from uuid import UUID
from domain.categories.models import CategoryDomain

class ICategoryRepository(abc.ABC):
    @abc.abstractmethod
    async def get_categories(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        sort_by: str = "title",
        sort_order: str = "asc",
        category_area: str | None = None,
        category_type: str | None = None,
    ) -> tuple[list[CategoryDomain], int]:
        pass

    @abc.abstractmethod
    async def get_category_by_id(self, category_id: UUID) -> CategoryDomain | None:
        pass

    @abc.abstractmethod
    async def get_delete_preview(self, category_id: UUID) -> dict:
        pass

    @abc.abstractmethod
    async def create_category(self, data: dict) -> CategoryDomain:
        pass

    @abc.abstractmethod
    async def update_category(self, category_id: UUID, data: dict) -> CategoryDomain | None:
        pass

    @abc.abstractmethod
    async def delete_category(self, category_id: UUID) -> bool:
        pass
