from fastapi import FastAPI
from routers import news, users
from fastapi.middleware.cors import CORSMiddleware
from utils.exception_handler import register_exception_handlers

app = FastAPI()
# 添加路由
app.include_router(news.router)
app.include_router(users.router)

# 添加CORS中间件
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)

# 注册全局异常处理器
register_exception_handlers(app)

@app.get("/")
async def hello():
  return {"message": "Hello World"}