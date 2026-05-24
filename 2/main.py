from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel

"""
指定响应格式，默认是JSONResponse
"""

app = FastAPI()

@app.get("/", response_class=JSONResponse)
async def read_root():
    return {"message": "Hello, FastAPI!"}

"""
HTMLResponse，返回html页面
"""
@app.get("/html", response_class=HTMLResponse)
async def html_response():
  return "<h1>Hello, FastAPI!</h1>"


"""
FileResponse，返回文件
"""
@app.get("/file", response_class=FileResponse)
async def file_response():
  return FileResponse(path="cat.jpg")


"""
自定义响应对象
"""
class CustomData(BaseModel):
  name: str
  age: int
class CustomResponse(BaseModel):
  code: int
  message: str
  data: CustomData

@app.get("/custom", response_model=CustomResponse)
async def custom_response():
  return CustomResponse(code=200, message="success", data=CustomData(name="FastAPI", age=18))
