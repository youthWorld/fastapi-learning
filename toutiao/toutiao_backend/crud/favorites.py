from models.favorites import Favorite
from models.news import News
from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def check_is_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int,
):
    """检查用户是否收藏了新闻"""
    stmt = select(Favorite).where(
        and_(Favorite.user_id == user_id, Favorite.news_id == news_id)
    )
    result = await db.execute(stmt)
    return result.first() is not None


async def add_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int,
):
    """添加收藏记录"""
    favorite = Favorite(
        user_id=user_id,
        news_id=news_id,
    )
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite


async def remove_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int,
):
    """删除收藏记录"""
    stmt = delete(Favorite).where(
        and_(Favorite.user_id == user_id, Favorite.news_id == news_id)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def get_favorite_list(
    db: AsyncSession,
    user_id: int,
    offset: int,
    page_size: int,
):
    """分页查询收藏列表，联表查询新闻信息"""
    stmt = (
        select(News, Favorite.created_at.label("favorite_time"))
        .join(News, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    return result.all()


async def get_favorite_count(
    db: AsyncSession,
    user_id: int,
):
    """查询用户收藏总数"""
    stmt = select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar()


async def clear_favorite(
    db: AsyncSession,
    user_id: int,
):
    """清空用户收藏列表"""
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount
