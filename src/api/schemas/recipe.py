from uuid import UUID
from pydantic import BaseModel, ConfigDict


class RecipeResponse(BaseModel):
    id: UUID
    title: str
    image_url: str | None = None
    difficulty_level: str | None = None
    duration_minutes: int | None = None
    category: str | None = None
    area: str | None = None
    tags: list[str] | None = None
    # Populated via joined query, not a column
    roadmap_category_titles: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class RecipeListResponse(BaseModel):
    items: list[RecipeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RecipeDeletePreview(BaseModel):
    recipe_ingredients: int
    steps: int
    step_ingredients: int
    step_items: int
    roadmap_nodes: int
