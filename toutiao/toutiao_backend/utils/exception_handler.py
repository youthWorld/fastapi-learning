from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fastapi import FastAPI, HTTPException

def register_exception_handlers(app: FastAPI):
    """
    注册异常处理函数
    """
    from utils.exception import (
        general_exception_handler,
        http_exception_handler,
        integrity_error_handler,
        sqlalchemy_error_handler,
    )

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
