from config.db_config import get_async_session
from crud import users
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from fastapi import Depends, Header, HTTPException


async def get_current_user(
    db: AsyncSession = Depends(get_async_session),
    authorization: str = Header(alias="Authorization"),
):
    """获取当前用户"""
    token = authorization.removeprefix("Bearer ")
    user = await users.getUserByToken(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    return user
