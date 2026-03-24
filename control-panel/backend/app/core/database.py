from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=False, future=True)

if not hasattr(AsyncSession, "exec"):
    async def _compat_exec(self, statement, *args, **kwargs):
        return await self.execute(statement, *args, **kwargs)
    AsyncSession.exec = _compat_exec


class AsyncSessionCompat(AsyncSession):
    async def exec(self, statement, *args, **kwargs):
        return await self.execute(statement, *args, **kwargs)


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSessionCompat,
    expire_on_commit=False,
)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
