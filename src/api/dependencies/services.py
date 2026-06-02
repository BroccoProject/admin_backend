from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies.db import get_db
from infrastructure.database.repositories.category_repository import SQLCategoryRepository
from infrastructure.database.repositories.recipe_repository import SQLRecipeRepository
from services.categories.category_service import CategoryService
from services.recipes.recipe_service import RecipeService

def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    repository = SQLCategoryRepository(db)
    return CategoryService(repository)

def get_recipe_service(db: AsyncSession = Depends(get_db)) -> RecipeService:
    repository = SQLRecipeRepository(db)
    return RecipeService(repository)
