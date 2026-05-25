from passlib.context import CryptContext

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 获取加密密码
def get_hash_password(password: str):
    return pwd_context.hash(password)

# 校验密码
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)