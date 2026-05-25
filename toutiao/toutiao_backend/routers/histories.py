from config.db_config import get_async_session
from crud import histories
from models.users import User
from schemas.histories import (
    AddHistoryDTO,
    HistoryListResponse,
    HistoryNewsItemResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from utils.auth import get_current_user
from utils.response import success_response

from fastapi import APIRouter, Depends, Path

router = APIRouter(prefix="/api/history", tags=["浏览历史"])


@router.post("/add")
async def add_history(
    add_history_dto: AddHistoryDTO,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """添加浏览历史"""
    history = await histories.add_history(db, user.id, add_history_dto.news_id)
    return success_response(data=history)


@router.get("/list")
async def get_history_list(
    page: int = 1,
    page_size: int = 10,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """获取浏览历史列表"""
    # 获取浏览历史
    offset = (page - 1) * page_size
    result = await histories.get_history_list(db, user.id, offset, page_size)
    # 获取浏览历史总数
    total = await histories.get_history_size(db, user.id)
    history_list = [
        HistoryNewsItemResponse.model_validate(
            {
                **news.__dict__,
                "view_time": view_time,
            }
        )
        for news, view_time in result
    ]
    data = HistoryListResponse(
        list=history_list,
        total=total,
        has_more=offset + len(result) < total,
    )
    return success_response(data=data)


@router.delete("/delete/{history_id}")
async def remove_history(
    history_id: int = Path(..., description="浏览历史ID"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """删除浏览历史"""
    await histories.remove_history(db, user.id, history_id)
    return success_response()

@router.delete("/clear")
async def clear_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """清空浏览历史"""
    await histories.clear_history(db, user.id)
    return success_response()
