from typing import Literal
from pydantic import BaseModel, Field

from infrastructure.database.models.enums import Language, ItemTag, DifficultyLevel, IngredientAction

# ---------------------------------------------------------------------------
# Step 1 – metadata schema
# ---------------------------------------------------------------------------

AllowedCategory = Literal[
    "Beef", "Breakfast", "Chicken", "Dessert", "Goat", "Lamb",
    "Miscellaneous", "Pasta", "Pork", "Seafood", "Side", "Starter",
    "Vegan", "Vegetarian",
]

AllowedTag = Literal[
    "Alcoholic", "Baking", "BBQ", "Beans", "Breakfast", "Brunch",
    "Bun", "Cake", "Calorific", "Caramel", "Casserole", "Celebration",
    "Cheap", "Cheesy", "Chilli", "Chocolate", "Christmas", "Curry",
    "Dairy", "DateNight", "Desert", "DinnerParty", "Easter", "Egg",
    "Eid", "Expensive", "Fish", "Fresh", "Fruity", "Fusion", "Glazed",
    "Greasy", "Halloween", "HangoverFood", "Heavy", "HighFat", "Kebab",
    "Keto", "Light", "LowCalorie", "LowCarbs", "MainMeal", "Meat",
    "Mild", "Nutty", "Onthego", "Paella", "Paleo", "Pancake", "Party",
    "Pasta", "Pie", "Pudding", "Pulse", "Salad", "Sandwich", "Sausages",
    "Savory", "Seafood", "Shellfish", "SideDish", "Snack", "Soup",
    "Sour", "Speciality", "Spicy", "Stew", "Streetfood", "StrongFlavor",
    "Summer", "Sweet", "Tart", "Treat", "UnHealthy", "Vegan",
    "Vegetables", "Vegetarian",
]

class RecipeMetaDraft(BaseModel):
    """Structured metadata extracted in step 1 (no steps/ingredients)."""
    title: str
    description: str = Field(
        description="2-4 sentence summary of the dish, its origin and key flavours."
    )
    difficulty: DifficultyLevel = Field(
        description="One of: Beginner, Intermediate, Master Chef"
    )
    duration_minutes: int = Field(
        description="Total cook + prep time in minutes."
    )
    category: AllowedCategory = Field(
        description="Primary meal category. Must be one of the allowed values."
    )
    area: str | None = Field(
        default=None,
        description="Cuisine origin, e.g. 'Italian', 'Mexican'. Leave null if unknown."
    )
    tags: list[AllowedTag] = Field(
        default_factory=list,
        description="Up to 10 relevant tags chosen strictly from the allowed list."
    )

# ---------------------------------------------------------------------------
# Step 2 – steps / ingredients schemas (unchanged)
# ---------------------------------------------------------------------------

class RecipeIngredientDraft(BaseModel):
    name: str
    amount: float = Field(description="The numeric amount/quantity of the ingredient.")
    unit: str = Field(description="The unit of measurement (e.g. 'g', 'ml', 'pcs'). Use 'pcs' if the item is counted in whole pieces.")
    sort_order: int = 0

class StepIngredientDraft(BaseModel):
    name: str
    amount: float = Field(description="The numeric amount/quantity of the ingredient in this step.")
    unit: str = Field(description="The unit of measurement (e.g. 'g', 'ml', 'pcs'). Use 'pcs' if the item is counted in whole pieces.")
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

class RecipeBodyDraft(BaseModel):
    """Structured output for step 2: only steps and ingredients."""
    ingredients: list[RecipeIngredientDraft] = Field(default_factory=list)
    steps: list[RecipeStepDraft] = Field(default_factory=list)


class RecipeDraft(BaseModel):
    """Final merged recipe draft combining step-1 metadata and step-2 body."""
    # --- metadata (from step 1) ---
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

    # --- body (from step 2) ---
    ingredients: list[RecipeIngredientDraft] = Field(default_factory=list)
    steps: list[RecipeStepDraft] = Field(default_factory=list)

    # --- i18n ---
    title_i18n: dict[Language, str] = Field(default_factory=dict)
    description_i18n: dict[Language, str] = Field(default_factory=dict)

    @classmethod
    def from_steps(cls, meta: "RecipeMetaDraft", body: "RecipeBodyDraft") -> "RecipeDraft":
        """Merge the two-step outputs into a single RecipeDraft."""
        return cls(
            title=meta.title,
            description=meta.description,
            difficulty=meta.difficulty,
            duration_minutes=meta.duration_minutes,
            category=meta.category,
            area=meta.area,
            tags=list(meta.tags),
            ingredients=body.ingredients,
            steps=body.steps,
        )
