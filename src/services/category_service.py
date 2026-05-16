import math
from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.roadmap.category import Category
from database.models.roadmap.roadmap_node import RoadmapNode
from database.models.roadmap.user_unlocked_category import UserUnlockedCategory
from database.models.roadmap.user_completed_node import UserCompletedNode
from schemas.category import CategoryCreate, CategoryUpdate


async def get_categories(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    sort_by: str = "title",
    sort_order: str = "asc",
) -> tuple[list[Category], int]:
    """Fetch paginated categories with optional search and sorting."""
    query = select(Category)
    count_query = select(func.count()).select_from(Category)

    if search:
        search_filter = Category.title.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    # Sorting
    allowed_sort_fields = {"title", "category_area", "category_type", "total_nodes", "unlock_cost_stars"}
    if sort_by in allowed_sort_fields:
        column = getattr(Category, sort_by)
        query = query.order_by(column.desc() if sort_order == "desc" else column.asc())
    else:
        query = query.order_by(Category.title.asc())

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    categories = list(result.scalars().all())

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    return categories, total


async def get_category_by_id(db: AsyncSession, category_id: UUID) -> Category | None:
    """Fetch a single category by its ID."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def get_delete_preview(db: AsyncSession, category_id: UUID) -> dict:
    """Return impact stats for a category before deletion (cascade effects)."""
    # Number of distinct users who have unlocked this category
    unlocked_users_result = await db.execute(
        select(func.count())
        .select_from(UserUnlockedCategory)
        .where(UserUnlockedCategory.category_id == category_id)
    )
    unlocked_users_count = unlocked_users_result.scalar() or 0

    # Number of roadmap nodes belonging to this category
    nodes_result = await db.execute(
        select(func.count())
        .select_from(RoadmapNode)
        .where(RoadmapNode.category_id == category_id)
    )
    nodes_count = nodes_result.scalar() or 0

    # Number of user_completed_nodes rows for nodes in this category
    completed_rows_result = await db.execute(
        select(func.count())
        .select_from(UserCompletedNode)
        .join(RoadmapNode, UserCompletedNode.node_id == RoadmapNode.id)
        .where(RoadmapNode.category_id == category_id)
    )
    completed_nodes_count = completed_rows_result.scalar() or 0

    return {
        "unlocked_by_users": unlocked_users_count,
        "roadmap_nodes": nodes_count,
        "completed_node_records": completed_nodes_count,
    }


async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
    """Create a new category."""
    category = Category(**data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(
    db: AsyncSession, category_id: UUID, data: CategoryUpdate
) -> Category | None:
    """Update an existing category (partial update)."""
    category = await get_category_by_id(db, category_id)
    if not category:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: UUID) -> bool:
    """Delete a category. Returns True on success, raises on constraint errors."""
    category = await get_category_by_id(db, category_id)
    if not category:
        return False

    await db.delete(category)
    await db.commit()
    return True
