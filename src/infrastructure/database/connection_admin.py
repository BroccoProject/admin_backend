from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from core.config import settings

engine_admin = create_async_engine(
    settings.DATABASE_URL_ADMIN,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={"statement_cache_size": 0},
)

AsyncAdminSessionLocal = async_sessionmaker(
    bind=engine_admin,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

class AdminBase(DeclarativeBase):
    pass