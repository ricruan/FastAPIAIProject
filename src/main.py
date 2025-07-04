import logging
import uuid

from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from src.utils.log_config import setup_logging
from .exception.aiException import AIException
from .myHttp.bo.httpResponse import HttpResponse
from fastapi import FastAPI, Request, status, HTTPException

# 初始化日志配置
setup_logging()

# 获取logger
logger = logging.getLogger(__name__)

# 先初始化日志 再导入其他模块
from fastapi import FastAPI
from .controller.ai import apiInfoController, sessionController, sessionDetailController
from .controller.erp import erpController
from .controller.dify import difyController
from .db.db import create_tables
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.staticfiles import StaticFiles


# 初始化数据库表
create_tables()

app = FastAPI(docs_url=None, redoc_url=None)  # 禁用默认的 docs 和 redoc

app.include_router(apiInfoController.router)
app.include_router(erpController.router)
app.include_router(difyController.router)
app.include_router(sessionController.router)
app.include_router(sessionDetailController.router)



# 挂载本地静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 自定义 Swagger UI 路由, FastAPI swagger 默认从CDN读下面那两个资源,但是有的网络环境下读不到
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="API Docs",
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",  # 本地 JS
        swagger_css_url="/static/swagger-ui/swagger-ui.css",      # 本地 CSS
        swagger_favicon_url="/static/swagger-ui/favicon-32x32.png",  # 本地图标
    )

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.exception_handler(AIException)
async def api_error_handler(request: Request, exc: AIException):
    """处理自定义AI异常"""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    logger.error(f"APIError - RequestID: {request_id}, Error: {exc}")

    return JSONResponse(status_code=200,content=HttpResponse.error(msg=exc.message, code=exc.code,data = exc.detail).model_dump())


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理FastAPI HTTP异常"""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    logger.error(f"HTTPException - RequestID: {request_id}, Error: {exc}")

    return JSONResponse(status_code=200,content=HttpResponse.error(msg=exc.detail, code=exc.status_code).model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求参数验证错误"""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    logger.error(f"ValidationError - RequestID: {request_id}, Error: {exc.errors()}")

    return JSONResponse(status_code=200,
                        content=HttpResponse.error(msg="参数校验失败" ,
                                                   code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                                   data = exc.errors()).model_dump()
                        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    logger.error(f"UnhandledException - RequestID: {request_id}, Error: {str(exc)}", exc_info=True)

    return JSONResponse(status_code=200,
                        content=HttpResponse.error(msg="服务器内部错误" + str(exc) ,
                                                   code=status.HTTP_500_INTERNAL_SERVER_ERROR).model_dump()
                        )

