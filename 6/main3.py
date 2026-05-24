from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import Depends, FastAPI, Query
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
    age: Mapped[int] = mapped_column(comment="年龄")
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

# 获取指定ID用户
@app.get("/user/findUser")
async def getUserById(id: int, session: AsyncSession = Depends(get_session)):
    # result = session.get(User, 1)
    result = await session.execute(select(User).where(User.id == id))
    return result.scalars().one_or_none()

# 获取年龄在min-max之间的用户
@app.get("/user/listUserByAge")
async def listUserByAge(min: int, max: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.age.between(min, max)))
    return result.scalars().all()

# 获取用户年龄>age，且用户名包含username的用户
@app.get("/user/listUserByAgeAndUsername")
async def listUserByAgeAndUsername(age: int, username: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where((User.age > age) & (User.username.like(f"%{username}%"))))
    return result.scalars().all()


# 获取id为在ids列表中的用户
"""
    知识点：参数为集合类型参数时，前端默认使用application/json格式，除非通过类型注解显示指定为查询参数或路径参数，在docs文档中的写法是逐个添加参数，在路径上要这样传递:/user/listUserByIds?ids=1&ids=2，而不是/user/listUserByIds?ids=1,2,3
"""
@app.get("/user/listUserByIds")
async def listUserByIds(ids: list[int] = Query(), session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.id.in_(ids)))
    return result.scalars().all()

# 测试聚合查询
@app.get("/user/aggregation")
async def aggregation(session: AsyncSession = Depends(get_session)):
    # result = await session.execute(select(func.count(User.id)))
    # result = await session.execute(select(func.sum(User.age)))
    # result = await session.execute(select(func.avg(User.age)))
    # result = await session.execute(select(func.min(User.age)))
    result = await session.execute(select(func.max(User.age)))
    return result.scalar() # scalar()返回单个值

# 分页查询
@app.get("/user/pageSelect")
async def pageSelect(page: int = Query(1, ge=1), pageSize: int = Query(5, ge=5), session: AsyncSession = Depends(get_session)):
    offset = (page - 1) * pageSize
    result = await session.execute(select(User).offset(offset).limit(pageSize))
    return result.scalars().all()

"""
DQL进阶
    - 执行SQL
        - execute(select(User).where(条件))返回一个ORM对象result
            - 通过scalars()方法获取相应结果集，如result.scalars().all()、result.scalars().one_or_none()、result.scalars().first()
            - 通过scalar()直接返回单个值，聚合查询中用到
        - get(User, 1)表示返回id为1的对象
    
    - 精确查询：where(条件)
        - 可以有多个条件，用&|!连接，&表示与、|表示或、!表示非，注意条件要用括号，不然会有优先级问题导致报错，比如&的优先级比>高。
        - 或者用函数：and_(条件1，条件2)、or_(条件1，条件2)、not_(条件)

    - 范围查询
        - where(字段.between(最小值, 最大值))
        - where(字段.in_(字段值列表))

    - 模糊查询：where(字段.like())，%匹配任意个字符，_匹配单个字符

    - 聚合查询
        - count(字段)
        - sum(字段)
        - avg(字段)
        - max(字段)
        - min(字段)

    - 分页查询
        - select().offset(x).limit(pageSize)
        - x = (page - 1) * pageSize
"""