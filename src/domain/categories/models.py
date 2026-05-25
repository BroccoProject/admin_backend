from dataclasses import dataclass
from uuid import UUID

@dataclass
class CategoryDomain:
    id: UUID
    title: str
    subtitle: str | None = None
    image_url: str | None = None
    unlock_cost_stars: int | None = 0
    category_area: str | None = None
    category_type: str | None = None
    total_nodes: int | None = 0
