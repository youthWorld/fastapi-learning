from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import Depends, FastAPI
from sqlalchemy import DateTime, String, func, select
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# 1.异步引擎
ASYNC_DATABASE_URL = "mysql+aiomysql://root:password@localhost:3306/fastapi-learning?charset=utf8mb4"
async_engine = create_async_engine(url=ASYNC_DATABASE_URL, echo=True)


# 2.创建pojo(基类+表对应的模型类)
# 基类就是把表的公共字段抽取出来了
class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now, default=func.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, default=func.now, onupdate=func.now, comment="更新时间")

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, comment="主键")
    username: Mapped[str] = mapped_column(String(20), comment="用户名")
    password: Mapped[str] = mapped_column(String(25), comment="密码")

# 生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield # 处理请求
    await async_engine.dispose() # 关闭数据库连接

# 数据库会话
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

# 依赖注入，对于需要用到数据库操作的请求，都要从AsyncSessionLocal中获取一个数据库会话
async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

app = FastAPI(lifespan=lifespan)

# 测试接口：获取用户列表
@app.get("/user/list")
async def getUserList(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    return result.scalars().all()


"""
变化的代码就两个，一是会话工厂、而是依赖注入会话
  会话：main1.py中提到DeclarativeBase模型基类中有个metadata对象，用于创建和删除表属于DDL，而DML和DQL要使用会话执行操作

  依赖注入会话：某个接口需要使用DML/DQL时，通过依赖注入一个数据库会话
  
  get_session方法中yield session表示返回一个会话并阻塞在该处（用return session的话get_session就执行完毕了），当请求完成后，会回到yield的下一行代码执行，即await session.commit()
"""