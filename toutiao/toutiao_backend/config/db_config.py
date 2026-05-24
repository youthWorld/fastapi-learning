from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

ASYNC_DATABASE_URL = "mysql+aiomysql://root:password@localhost:3306/news_app?charset=utf8mb4"

# 创建数据库引擎
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

# 创建会话工厂
async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# 依赖注入会话
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()