from datetime import datetime

from models.histories import History
from models.news import News
from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def add_history(db: AsyncSession, user_id: int, news_id: int):
    """添加浏览历史"""
    # 先检查是否存在该浏览历史
    stmt = select(History).where(
        and_(History.user_id == user_id, History.news_id == news_id)
    )
    result = await db.execute(stmt)
    existing_history = result.scalars().one_or_none()
    if existing_history:  # 如果存在，更新浏览时间
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    # 如果不存在，添加新的浏览历史
    history = History(user_id=user_id, news_id=news_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history


async def get_history_list(db: AsyncSession, user_id: int, offset: int, limit: int):
    """分页查询浏览历史列表"""
    stmt = (
        select(News, History.view_time.label("view_time"))
        .join(History, News.id == History.news_id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.all()


async def get_history_size(db: AsyncSession, user_id: int):
    """获取浏览历史总数"""
    stmt = select(func.count(History.id)).where(History.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar()


async def remove_history(db: AsyncSession, user_id: int, history_id: int):
    """删除浏览历史"""
    stmt = delete(History).where(
        and_(History.user_id == user_id, History.id == history_id)
    )
    await db.execute(stmt)
    await db.commit()


async def clear_history(db: AsyncSession, user_id: int):
    """清空浏览历史"""
    stmt = delete(History).where(History.user_id == user_id)
    await db.execute(stmt)
    await db.commit()
