from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# 1.异步引擎
ASYNC_DATABASE_URL = "mysql+aiomysql://root:password@localhost:3306/fastapi-learning?charset=utf8mb4"
async_engine = create_async_engine(url=ASYNC_DATABASE_URL, echo=True)


# 2.创建pojo(基类+表对应的模型类)
# 基类就是把表的公共字段抽取出来了
class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), default=func.now(), comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, comment="主键")
    username: Mapped[str] = mapped_column(String(20), comment="用户名")
    password: Mapped[str] = mapped_column(String(25), comment="密码")
    age: Mapped[int] = mapped_column(comment="年龄")

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

# 增的DTO
class UserBase(BaseModel):
    username: str = Field(max_length=20)
    password: str = Field(max_length=25)
    age: int

# 增
@app.post("/user/add")
async def addUser(userbase: UserBase, db: AsyncSession = Depends(get_session)):
    user = User(**userbase.__dict__)
    db.add(user)
    return user

# 改的DTO
class UserUpdateBase(BaseModel):
    username: Optional[str] = Field(None, max_length=20)
    password: Optional[str] = Field(None, max_length=25)
    age: Optional[int] = None

# 改
@app.post("/user/update/{id}")
async def updateUser(id: int, userUpdateBase:UserUpdateBase, db: AsyncSession = Depends(get_session)):
    user = await db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    userUpdateBase_un_empty = userUpdateBase.model_dump(exclude_unset=True)
    for key, value in userUpdateBase_un_empty.items():
        setattr(user, key, value)
    return user

# 删
@app.delete("/user/delete/{id}")
async def deleteUser(id: int, db: AsyncSession = Depends(get_session)):
    user = await db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    await db.delete(user)
    return {"message": "删除用户成功"}

"""
新增时遇到的语法：
    user = User(**userbase.__dict__)的含义：
        userbase.__dict__就是把对象转换为字典
        **就是解包，把字典中的键值对转换为关键字参数
        等价于user = User(username=userbase.username, password=userbase.password, age=userbase.age)
修改功能的关键点和语法：
    1.不需要自己调用update语句，而是修改查找出来的对象的属性就行，涉及到sqlalchemy的底层
    2.这里用了一下model_dump()方法，把对象转换为字典，其中exclude_unset=True表示排除没有“显式设置”值的字段
    这里逻辑有点乱，首先model_dump是BaseModel提供的方法，没有显式设置值的意思就是前端没有传这个字段，如果前端传了username值为null，null就是None所以username被设置为None，这样不会被exclude_unset排除！
    3.为什么这里要单独给修改写一个DTO(UserUpdateBase)，就是想配合model_dump()使用，因为毕竟不是每次更新都是全量更新，所以UserUpdateBase里面的字段都是Optional(可选)的


修改和删除都有相应方法，和查询的select()是一样的，update(User).where(条件)、delete(User).where(条件)
"""