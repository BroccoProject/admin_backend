from dataclasses import dataclass, field
from uuid import UUID

@dataclass
class RecipeDomain:
    id: UUID
    title: str
    description: str | None = None
    image_url: str | None = None
    difficulty_level: str | None = None
    duration_minutes: int | None = None
    youtube_url: str | None = None
    tags: list[str] | None = None
    category: str | None = None
    area: str | None = None
    source_url: str | None = None
    roadmap_category_titles: list[str] = field(default_factory=list)

@dataclass
class RecipeDeletePreviewDomain:
    recipe_ingredients: int
    steps: int
    step_ingredients: int
    step_items: int
    roadmap_nodes: int

