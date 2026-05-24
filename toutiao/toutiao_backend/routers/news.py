from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from crud import news
from config.db_config import get_async_session

router = APIRouter(prefix="/api/news", tags=["新闻"])

# 获取新闻分类
@router.get("/categories")
async def getCategories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends
                        (get_async_session)):
  categories = await news.getCategories(db, skip, limit)
  return {
    "code": 200,
    "message": "获取新闻分类成功",
    "data": categories
  }

# 获取新闻列表
@router.get("/list")
async def getNewsList(
  category_id: int = Query(..., alias="categoryId"),
  page: int = 1,
  page_size: int = Query(10, alias="pageSize", le=100),
  db: AsyncSession = Depends(get_async_session)
):
  skip = (page -  1) * page_size
  news_list = await news.getNewsList(db, category_id, skip, page_size) # 指定分类的新闻列表
  news_count = await news.getNewsCount(db, category_id) # 指定分类的新闻数量
  has_more = skip + len(news_list) < news_count # 当前分类是否还有更多新闻（滚动条）
  return {
  "code": 200,
  "message": "获取新闻列表成功",
  "data": {
    "list": news_list,
    "total": news_count,
    "hasMore": has_more
  }
}

# 根据新闻id获取新闻详情
@router.get("/detail")
async def getNewsDetail(id: int, db: AsyncSession = Depends(get_async_session)):
  news_detail = await news.getNewsDetail(db, id) # 查询新闻详情
  if not news_detail:
      raise HTTPException(status_code=404, detail="新闻不存在")
  row_count = await news.incrementNewsViews(db, id) # 增加浏览量
  if not row_count:
     raise HTTPException(status_code=500, detail="增加浏览量失败")
  
  data = news_detail.__dict__
  data["relatedNews"] = await news.getRelatedNews(db, id, news_detail.category_id) # 获取相关新闻列表

  return {
  "code": 200,
  "message": "success",
  "data": data
}