import logging
from src.utils.log_config import setup_logging

# 初始化日志配置
setup_logging()

# 获取logger
logger = logging.getLogger(__name__)

# 先初始化日志 再导入其他模块
from fastapi import FastAPI
from .controller.ai import apiInfoController
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
