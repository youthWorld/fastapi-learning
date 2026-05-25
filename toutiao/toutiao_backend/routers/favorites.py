from config.db_config import get_async_session
from crud import favorites
from models.users import User
from schemas.favorites import (
    AddFavoriteDTO,
    FavoriteNewsItemResponse,
    FavoriteNewsListResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from utils.auth import get_current_user
from utils.response import success_response

from fastapi import APIRouter, Depends, HTTPException, Query

router = APIRouter(prefix="/api/favorite", tags=["新闻收藏"])


@router.get("/check")
async def check_is_favorite(
    news_id: int = Query(alias="newsId", description="新闻ID"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """检查用户是否收藏了新闻"""
    # 鉴权(get_current_user) -> 检查是否存在收藏记录
    is_favorite = await favorites.check_is_favorite(db, user.id, news_id)
    return success_response(data={"isFavorite": is_favorite})


@router.post("/add")
async def add_favorite(
    add_favorite_dto: AddFavoriteDTO,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """添加收藏记录"""
    # 鉴权(get_current_user) -> 检查是否存在收藏记录
    favorite = await favorites.add_favorite(db, user.id, add_favorite_dto.news_id)
    return success_response(data=favorite)


@router.delete("/remove")
async def remove_favorite(
    news_id: int = Query(alias="newsId", description="新闻ID"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """删除收藏记录"""
    # 鉴权(get_current_user) -> 检查是否存在收藏记录
    result = await favorites.remove_favorite(db, user.id, news_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="收藏记录不存在"
        )
    return success_response(data=None)


@router.get("/list")
async def get_favorite_list(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, alias="pageSize", le=100, description="每页数量"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """获取用户收藏列表"""
    # 鉴权(get_current_user) -> 分页查询收藏列表、查询收藏总数
    offset = (page - 1) * page_size
    result = await favorites.get_favorite_list(db, user.id, offset, page_size)
    total = await favorites.get_favorite_count(db, user.id)
    favorite_list = [
        FavoriteNewsItemResponse.model_validate(
            {**news.__dict__, "favorite_time": favorite_time}
        )
        for news, favorite_time in result
    ]
    data = FavoriteNewsListResponse(
        list=favorite_list, total=total, has_more=(offset + len(result) < total)
    )
    return success_response(data=data)


@router.delete("/clear")
async def clear_favorite(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """清空用户收藏列表"""
    # 鉴权(get_current_user) -> 清空用户收藏列表
    rowcount = await favorites.clear_favorite(db, user.id)
    return success_response(message=f"成功删除{rowcount}条收藏记录", data=None)
