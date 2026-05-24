from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News

# 获取新闻分类
async def getCategories(db: AsyncSession, skip: int = 0, limit: int = 100):
  stmt = select(Category).offset(skip).limit(limit)
  result = await db.execute(stmt)
  return result.scalars().all()

# 获取指定分类的新闻列表
async def getNewsList(db: AsyncSession, category_id: int, skip: int = 0, page_size: int = 10):
  stmt = select(News).where(News.category_id == category_id).offset(skip).limit(page_size)
  result = await db.execute(stmt)
  return result.scalars().all()

# 获取指定分类的新闻数量
async def getNewsCount(db: AsyncSession, category_id: int):
  stmt = select(func.count(News.id)).where(News.category_id == category_id)
  result = await db.execute(stmt)
  return result.scalar()

# 根据新闻id获取新闻详情
async def getNewsDetail(db: AsyncSession, id: int):
  stmt = select(News).where(News.id == id)
  result = await db.execute(stmt)
  return result.scalar_one_or_none()

# 新闻浏览量views +1
async def incrementNewsViews(db: AsyncSession, id: int):
  stmt = update(News).where(News.id == id).values(views=News.views + 1)
  result = await db.execute(stmt)
  await db.commit()
  return result.rowcount

# 获取新闻的关联新闻列表
async def getRelatedNews(db: AsyncSession, news_id: int, category_id: int, page_size: int = 5):
  stmt = select(News).where(
      and_(News.id != news_id, News.category_id == category_id)
    ).order_by(
      News.views.desc(),
      News.publish_time.desc(),
    ).limit(page_size)
  result = await db.execute(stmt)
  # 返回指定字段
  return [
    {
      "id": item.id,
      "title": item.title,
      "description": item.description,
      "image": item.image,
      "author": item.author,
      "category_id": item.category_id,
      "views": item.views,
      "publish_time": item.publish_time,
    }
    for item in result.scalars().all()
  ]