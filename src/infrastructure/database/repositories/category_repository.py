import math
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from infrastructure.database.models.roadmap.category import Category
from infrastructure.database.models.roadmap.roadmap_node import RoadmapNode
from infrastructure.database.models.roadmap.user_unlocked_category import UserUnlockedCategory
from infrastructure.database.models.roadmap.user_completed_node import UserCompletedNode

from domain.categories.ports import ICategoryRepository
from domain.categories.models import CategoryDomain
from domain.exceptions import ResourceInUseError


class SQLCategoryRepository(ICategoryRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_domain(self, category: Category) -> CategoryDomain:
        return CategoryDomain(
            id=category.id,
            title=category.title,
            subtitle=category.subtitle,
            image_url=category.image_url,
            unlock_cost_stars=category.unlock_cost_stars,
            category_area=category.category_area,
            category_type=category.category_type,
            total_nodes=category.total_nodes,
        )

    async def get_categories(
        self,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        sort_by: str = "title",
        sort_order: str = "asc",
    ) -> tuple[list[CategoryDomain], int]:
        query = select(Category)
        count_query = select(func.count()).select_from(Category)

        if search:
            search_filter = Category.title.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        allowed_sort_fields = {"title", "category_area", "category_type", "total_nodes", "unlock_cost_stars"}
        if sort_by in allowed_sort_fields:
            column = getattr(Category, sort_by)
            query = query.order_by(column.desc() if sort_order == "desc" else column.asc())
        else:
            query = query.order_by(Category.title.asc())

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        categories = list(result.scalars().all())

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        return [self._to_domain(c) for c in categories], total

    async def get_category_by_id(self, category_id: UUID) -> CategoryDomain | None:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        if not category:
            return None
        return self._to_domain(category)

    async def get_delete_preview(self, category_id: UUID) -> dict:
        unlocked_users_result = await self.db.execute(
            select(func.count())
            .select_from(UserUnlockedCategory)
            .where(UserUnlockedCategory.category_id == category_id)
        )
        unlocked_users_count = unlocked_users_result.scalar() or 0

        nodes_result = await self.db.execute(
            select(func.count())
            .select_from(RoadmapNode)
            .where(RoadmapNode.category_id == category_id)
        )
        nodes_count = nodes_result.scalar() or 0

        completed_rows_result = await self.db.execute(
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

    async def create_category(self, data: dict) -> CategoryDomain:
        category = Category(**data)
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return self._to_domain(category)

    async def update_category(self, category_id: UUID, data: dict) -> CategoryDomain | None:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        if not category:
            return None

        for field, value in data.items():
            setattr(category, field, value)

        await self.db.commit()
        await self.db.refresh(category)
        return self._to_domain(category)

    async def delete_category(self, category_id: UUID) -> bool:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        if not category:
            return False

        try:
            await self.db.delete(category)
            await self.db.commit()
            return True
        except IntegrityError as e:
            await self.db.rollback()
            error_msg = str(e.orig) if hasattr(e, "orig") and e.orig else str(e)
            raise ResourceInUseError("Database constraint violation", detail=error_msg)

