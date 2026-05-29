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


class RecipeUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    image_url: str | None = None
    difficulty_level: str | None = None
    duration_minutes: int | None = None
    youtube_url: str | None = None
    tags: list[str] | None = None
    category: str | None = None
    area: str | None = None
    source_url: str | None = None


# ── Detailed response schemas for recipe edit page ──


class IngredientRef(BaseModel):
    id: UUID
    name: str
    default_unit: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ItemRef(BaseModel):
    id: UUID
    name: str
    tag: str

    model_config = ConfigDict(from_attributes=True)


class RecipeIngredientResponse(BaseModel):
    id: UUID
    ingredient: IngredientRef
    amount: float | None = None
    unit: str | None = None
    sort_order: int = 0

    model_config = ConfigDict(from_attributes=True)


class StepIngredientResponse(BaseModel):
    id: UUID
    ingredient: IngredientRef
    amount: float | None = None
    unit: str | None = None
    actions: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class StepItemResponse(BaseModel):
    id: UUID
    item: ItemRef

    model_config = ConfigDict(from_attributes=True)


class RecipeStepResponse(BaseModel):
    id: UUID
    step_number: int
    instruction: str
    duration_seconds: int | None = None
    ingredients: list[StepIngredientResponse] = []
    items: list[StepItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RecipeDetailResponse(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    image_url: str | None = None
    difficulty_level: str | None = None
    duration_minutes: int | None = None
    category: str | None = None
    area: str | None = None
    tags: list[str] | None = None
    youtube_url: str | None = None
    source_url: str | None = None
    roadmap_category_titles: list[str] = []
    ingredients: list[RecipeIngredientResponse] = []
    steps: list[RecipeStepResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ── Full update schema (replaces nested data) ──


class RecipeIngredientUpdate(BaseModel):
    ingredient_id: UUID
    amount: float | None = None
    unit: str | None = None
    sort_order: int = 0


class StepIngredientUpdate(BaseModel):
    ingredient_id: UUID
    amount: float | None = None
    unit: str | None = None
    actions: list[str] = []


class StepItemUpdate(BaseModel):
    item_id: UUID


class RecipeStepUpdate(BaseModel):
    step_number: int
    instruction: str
    duration_seconds: int | None = None
    ingredients: list[StepIngredientUpdate] = []
    items: list[StepItemUpdate] = []


class RecipeFullUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    image_url: str | None = None
    difficulty_level: str | None = None
    duration_minutes: int | None = None
    youtube_url: str | None = None
    tags: list[str] | None = None
    category: str | None = None
    area: str | None = None
    source_url: str | None = None
    ingredients: list[RecipeIngredientUpdate] = []
    steps: list[RecipeStepUpdate] = []


# ── List responses for ingredients and items ──


class IngredientListResponse(BaseModel):
    items: list[IngredientRef]


class ItemListResponse(BaseModel):
    items: list[ItemRef]
