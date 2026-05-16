from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    title: str
    subtitle: str | None = None
    image_url: str | None = None
    unlock_cost_stars: int | None = 0
    category_area: str | None = None
    category_type: str | None = None
    total_nodes: int | None = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    image_url: str | None = None
    unlock_cost_stars: int | None = None
    category_area: str | None = None
    category_type: str | None = None
    total_nodes: int | None = None


class CategoryResponse(CategoryBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
