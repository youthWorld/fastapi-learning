import uuid
from datetime import datetime, timedelta

from models.users import User, UserToken
from schemas.users import UserDTO, UserPasswordDTO, UserUpdateDTO
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from utils import security

from fastapi import HTTPException


async def getUser(db: AsyncSession, username: str):
    """根据用户名查询用户"""
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalars().one_or_none()


async def createUser(db: AsyncSession, userDTO: UserDTO):
    """创建用户"""
    hash_password = security.get_hash_password(userDTO.password)  # 加密密码
    user = User(username=userDTO.username, password=hash_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# token的逻辑并不好，而且也得用jwt，而不是简单的uuid
async def generateToken(db: AsyncSession, user_id: int):
    """生成用户令牌"""
    # 查找用户是否有token，没有则创建token，有则更新过期时间
    stmt = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(stmt)
    userToken = result.scalars().one_or_none()
    expire_at = datetime.now() + timedelta(days=1, hours=1, minutes=1, seconds=1)
    if userToken:  # 有token，更新过期时间
        userToken.expires_at = expire_at
    else:  # 没有token，创建新token
        userToken = UserToken(
            user_id=user_id,
            token=str(uuid.uuid4()),
            expires_at=expire_at,
        )
        db.add(userToken)
        await db.commit()
    await db.refresh(userToken)
    return userToken.token


# 校验用户(用户名和密码)
async def validateUser(db: AsyncSession, userDTO: UserDTO):
    """校验用户(用户名和密码)"""
    # 查询用户
    user = await getUser(db, userDTO.username)
    if not user:
        return None
    # 校验密码
    if not security.verify_password(userDTO.password, user.password):
        return None
    return user


# 根据token查询用户(用户认证)
async def getUserByToken(db: AsyncSession, token: str):
    """根据token查询用户"""
    # 先查询token是否存在，是否过期
    stmt = select(UserToken).where(UserToken.token == token)
    result = await db.execute(stmt)
    userToken = result.scalars().one_or_none()
    if not userToken or userToken.expires_at < datetime.now():
        return None

    # 再根据token查询用户
    stmt = select(User).where(User.id == userToken.user_id)
    result = await db.execute(stmt)
    user = result.scalars().one_or_none()
    return user


# 更新用户信息
async def updateUserInfo(db: AsyncSession, username: str, userDTO: UserUpdateDTO):
    """更新用户信息"""
    stmt = (
        update(User)
        .where(User.username == username)
        .values(userDTO.model_dump(exclude_unset=True))
    )
    result = await db.execute(stmt)
    await db.commit()
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="更新失败")
    # 查询更新后的用户信息
    user = await getUser(db, username)
    return user


# 更新用户密码
async def updateUserPassword(
    db: AsyncSession, user: User, userPasswordDTO: UserPasswordDTO
):
    """更新用户密码"""
    # 校验旧密码
    if not security.verify_password(userPasswordDTO.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码错误"
        )
    # 设置新密码
    user.password = security.get_hash_password(userPasswordDTO.new_password)
    """
    sqlalchemy会自动跟踪从数据库中查找得到的ORM对象，在commit()时自动检测所有被跟踪对象的变化，从而完成自动更新，当然我的理解仅限于此（底层原理是什么？什么时候会破坏这种追踪？我都不知道），所以我也不理解这里为什么要写db.add(user)，老师解释如下：
        这里的add并不是新增，而是更新：由SQLAlchemy真正接管这个 User 对象，确保可以 commit
        可以规避 session 过期或关闭导致的不能提交的问题
    """
    db.add(user)
    await db.commit()
    await db.refresh(user)
