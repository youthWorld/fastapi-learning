from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Field

app = FastAPI()

# 入门
@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}

# 路径参数：{name}
# 额外参数注解使用Path函数，注意Path的第一个参数即默认值必须传入...，且不能是其他值
@app.get("/hello/{name}")
async def say_hello(name: str = Path(..., description="用户姓名", min_length=2, max_length=15)):
    return {"message": f"你好, {name}!"}

# 查询参数：?skip?limit
# 分页查询，额外参数注解使用Query函数，Query的第一个参数是默认值
@app.get("/news/news_list")
async def get_news_list(skip: int = Query(0, lt=100),
                  limit: int = Query(10)):
    return {"skip": skip, "limit": limit}


# application/json参数：通过对象接收，定义一个类，继承BaseModel类
# 额外参数注解使用Field函数
# 新增图书，图书信息包括书名、作者、出版社、售价
class Book(BaseModel):
    name: str = Field(min_length=1, max_length=30, description="图书名称")
    author: str = Field(min_length=2, max_length=15, description="作者")
    publisher: str = Field(min_length=5, max_length=30, description="出版社")
    price: float = Field(gt=0, description="售价")
@app.post("/book/add")
async def add_book(book: Book):
    return book