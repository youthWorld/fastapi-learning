from pydantic import BaseModel, ConfigDict, Field


class UserDTO(BaseModel):
    """
    用户注册DTO
    """

    username: str
    password: str
    # TODO，校验


class UserInfoBase(BaseModel):
    """
    用户信息基础模型
    """

    nickname: str | None = Field(None, nullable=True, max_length=50, description="昵称")
    avatar: str | None = Field(
        None, nullable=True, max_length=255, description="头像URL"
    )
    gender: str | None = Field(None, nullable=True, max_length=10, description="性别")
    bio: str | None = Field(None, nullable=True, max_length=500, description="个人简介")


class UserInfoResponse(UserInfoBase):
    """
    用户信息响应模型
    """
    id: int
    username: str

    # 配置
    model_config = ConfigDict(from_attributes=True)

class UserAuthResponse(BaseModel):
    """
    用户认证响应模型
    """
    token: str
    user_info: UserInfoResponse = Field(alias="userInfo")

    model_config = ConfigDict(
        from_attributes=True, # 允许从ORM对象中赋值
        populate_by_name=True # alias字段名兼容
    )

class UserUpdateDTO(BaseModel):
    """
    用户更新DTO
    """
    nickname: str | None = Field(None, nullable=True, max_length=50, description="昵称")
    avatar: str | None = Field(
        None, nullable=True, max_length=255, description="头像URL"
    )
    gender: str | None = Field(None, nullable=True, max_length=10, description="性别")
    bio: str | None = Field(None, nullable=True, max_length=500, description="个人简介")
    phone: str | None = Field(None, nullable=True, max_length=20, description="手机号")

class UserPasswordDTO(BaseModel):
    """
    用户密码更新DTO
    """
    old_password: str = Field(alias="oldPassword", description="旧密码")
    new_password: str = Field(alias="newPassword", description="新密码")
