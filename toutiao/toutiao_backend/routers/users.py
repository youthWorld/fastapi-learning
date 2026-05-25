from config.db_config import get_async_session
from crud import users
from models.users import User
from schemas.users import (
    UserAuthResponse,
    UserDTO,
    UserInfoResponse,
    UserPasswordDTO,
    UserUpdateDTO,
)
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from utils import auth
from utils.response import success_response

from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/api/user", tags=["用户"])


@router.post("/register")
async def register(userDTO: UserDTO, db: AsyncSession = Depends(get_async_session)):
    # 查询用户->创建用户->创建token->响应
    exist_user = await users.getUser(db, userDTO.username)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
        )
    # 创建用户
    user = await users.createUser(db, userDTO)
    # 创建token
    token = await users.generateToken(db, user.id)
    userAuthResponse = UserAuthResponse(
        token=token,
        user_info=UserInfoResponse.model_validate(user),
    )
    return success_response(message="success", data=userAuthResponse)


@router.post("/login")
async def login(userDTO: UserDTO, db: AsyncSession = Depends(get_async_session)):
    """用户登录"""
    # 校验密码、创建token，响应结果
    # 校验密码
    user = await users.validateUser(db, userDTO)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )
    # 创建token
    token = await users.generateToken(db, user.id)
    userAuthResponse = UserAuthResponse(
        token=token,
        user_info=UserInfoResponse.model_validate(user),
    )
    return success_response(message="success", data=userAuthResponse)


@router.get("/info")
async def info(user: User = Depends(auth.get_current_user)):
    """获取用户信息"""
    return success_response(
        message="success", data=UserInfoResponse.model_validate(user)
    )


@router.put("/update")
async def update(
    userDTO: UserUpdateDTO,
    user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """更新用户信息"""
    # 校验用户和token(auth.get_current_user)->更新用户信息->查询更新后的用户信息->响应新的用户信息
    user = await users.updateUserInfo(db, user.username, userDTO)
    return success_response(
        message="success", data=UserInfoResponse.model_validate(user)
    )


@router.put("/password")
async def updatePassword(
    userPasswordDTO: UserPasswordDTO,
    user: User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """更新用户密码"""
    # 校验用户和token(auth.get_current_user)->更新用户密码->响应结果
    await users.updateUserPassword(db, user, userPasswordDTO)
    return success_response(message="success", data=None)
