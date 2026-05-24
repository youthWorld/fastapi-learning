from fastapi import FastAPI, Query, Depends

app = FastAPI()

# 公共参数
def common_params(
    skip: int = Query(0, description="跳过数量"),
    limit: int = Query(10, description="每页数量")
):
  # 这里可以做更复杂的参数校验、权限验证等逻辑
  return {"skip": skip, "limit": limit}

@app.get("/news_list")
async def get_news_list(common_params: dict = Depends(common_params)):
  return common_params


@app.get("/book_list")
async def get_book_list(common_params: dict = Depends(common_params)):
  return common_params
