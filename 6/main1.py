from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine

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

# 3.建表函数
async def create_table():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 4.生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_table() # 创建表
    yield # 处理请求
    await async_engine.dispose() # 关闭数据库连接

app = FastAPI(lifespan=lifespan)

"""
这里知识点比较多
1.异步引擎

2.模型类相关
  DeclarativeBase: 模型类基础类，所有的模型类都要继承这个类，提供的metadata对象有创建和删除表的方法
  Mapped
    sqlalchemy类型注解，age:Mapped[int]就是告诉python这是一个int类型的属性，同时告诉数据库这是一个int类型的字段，而age:int只能告诉python这是一个int类型的属性
  mapped_column: 映射列，用于定义模型类的字段

3.事件
  @asynccontextmanager：异步上下文管理器
"""