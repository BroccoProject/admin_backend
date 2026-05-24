from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.connection import AsyncSessionLocal
from infrastructure.database.connection_admin import AsyncAdminSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_admin_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncAdminSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
