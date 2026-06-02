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


class CategoryNodeCreate(BaseModel):
    recipe_id: UUID | None = None
    title: str
    x: int
    y: int
    prerequisite_indices: list[int] = []


class CategoryCreateWithNodes(CategoryBase):
    nodes: list[CategoryNodeCreate] = []


class CategoryNodeResponse(BaseModel):
    id: UUID
    recipe_id: UUID | None = None
    title: str
    x: int
    y: int
    prerequisite_ids: list[UUID] = []


class CategoryUpdate(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    image_url: str | None = None
    unlock_cost_stars: int | None = None
    category_area: str | None = None
    category_type: str | None = None
    total_nodes: int | None = None


class CategoryUpdateWithNodes(CategoryUpdate):
    nodes: list[CategoryNodeCreate] | None = None


class CategoryResponse(CategoryBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
