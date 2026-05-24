
from fastapi import FastAPI


app = FastAPI()

"""
按照代码顺序，中间件的加入顺序是：中间件1、中间件2
这是一种栈模型，先加入到栈的保存在栈厎，所以栈的内容为：中间件2、中间件1、接口
所以最终执行顺序是：中间件2start、中间件1start、接口执行、中间件1end、中间件2end
"""

@app.middleware("http")
async def middleware1(request, call_next):
    print("中间件1 start")
    response = await call_next(request)
    print("中间件1 end")
    return response

@app.middleware("http")
async def middleware2(request, call_next):
    print("中间件2 start")
    response = await call_next(request)
    print("中间件2 end")
    return response


@app.get("/")
async def hello():
    print("请求执行")
    return {"message": "Hello, FastAPI!"}