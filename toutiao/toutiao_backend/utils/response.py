from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_response(message: str = "success", data=None):
    """
    成功响应模型
    """
    content = {
        "code": 200,
        "message": message,
        "data": data,
    }
    # jsonable_encoder把任何的对象/集合都序列化为正确的json格式
    return JSONResponse(content=jsonable_encoder(content))
