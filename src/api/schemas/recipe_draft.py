from pydantic import BaseModel, Field
from infrastructure.database.models.enums import Language, ItemTag, DifficultyLevel, IngredientAction

class RecipeIngredientDraft(BaseModel):
    name: str
    amount: float
    unit: str
    sort_order: int = 0

class StepIngredientDraft(BaseModel):
    name: str
    amount: float
    unit: str
    actions: list[IngredientAction] = Field(default_factory=list)
    name_i18n: dict[Language, str] = Field(default_factory=dict)

class StepItemDraft(BaseModel):
    name: str
    tag: ItemTag
    name_i18n: dict[Language, str] = Field(default_factory=dict)

class RecipeStepDraft(BaseModel):
    step_number: int
    instruction: str
    instruction_i18n: dict[Language, str] = Field(default_factory=dict)
    duration_seconds: int | None = None
    ingredients: list[StepIngredientDraft] = Field(default_factory=list)
    items: list[StepItemDraft] = Field(default_factory=list)

class RecipeDraft(BaseModel):
    title: str
    description: str
    difficulty: DifficultyLevel
    duration_minutes: int
    category: str
    area: str | None = None
    tags: list[str] = Field(default_factory=list)
    source_url: str | None = None
    image_url: str | None = None
    youtube_url: str | None = None

    ingredients: list[RecipeIngredientDraft] = Field(default_factory=list)
    steps: list[RecipeStepDraft] = Field(default_factory=list)
    
    title_i18n: dict[Language, str] = Field(default_factory=dict)
    description_i18n: dict[Language, str] = Field(default_factory=dict)
