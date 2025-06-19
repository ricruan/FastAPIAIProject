import logging
from src.utils.log_config import setup_logging

# 初始化日志配置
setup_logging()

# 获取logger
logger = logging.getLogger(__name__)

# 导入其他模块
from fastapi import FastAPI
from .controller import apiInfoController
from .db.db import create_tables


# 初始化数据库表
create_tables()

app = FastAPI()
app.include_router(apiInfoController.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
