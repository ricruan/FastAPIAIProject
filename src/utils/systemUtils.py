import os
import importlib
import logging
import inspect
from typing import List, Optional
from fastapi import FastAPI, APIRouter,Request
from starlette.middleware.base import BaseHTTPMiddleware

# 获取logger
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 记录请求路径
        path = request.url.path

        # 只记录特定路径的请求体
        if path in os.getenv("WATCHING_API_URL"):
            # 读取原始请求体
            body = await request.body()
            # 记录原始请求体
            logger.info(f"Raw request body for {path}: {body.decode()}")
            # 重新设置请求体，因为body()操作是消耗性的
            request._body = body

        # 继续处理请求
        response = await call_next(request)
        return response


def register_routers(app: FastAPI, controller_dir: str = "controller", blacklist: Optional[List[str]] = None) -> None:
    """
    自动注册路由函数

    递归扫描src/controller文件夹下的所有Python文件，如果文件中包含router对象，则将其注册到FastAPI应用中。
    支持黑名单机制，黑名单中的文件不会被注册。

    Args:
        app: FastAPI应用实例
        controller_dir: controller文件夹的相对路径，默认为"controller"
        blacklist: 黑名单列表，包含不需要注册的文件名（不含扩展名），默认为None
    """
    if blacklist is None:
        blacklist = []

    # 获取controller文件夹的绝对路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    controller_path = os.path.join(base_dir, controller_dir)

    logger.info(f"开始扫描路由文件，路径: {controller_path}")
    logger.info(f"黑名单文件: {blacklist}")

    # 记录成功注册的路由数量
    registered_count = 0
    skipped_count = 0
    failed_count = 0

    # 递归扫描controller文件夹
    for root, _, files in os.walk(controller_path):
        for file in files:
            # 只处理Python文件
            if not file.endswith('.py'):
                continue

            # 获取文件名（不含扩展名）
            filename = os.path.splitext(file)[0]

            # 检查是否在黑名单中
            if filename in blacklist:
                logger.info(f"跳过黑名单文件: {filename}")
                skipped_count += 1
                continue

            # 获取相对于base_dir的模块路径
            rel_path = os.path.relpath(root, base_dir)
            module_path = '.'.join(['src'] + rel_path.split(os.sep))

            if filename != '__init__':  # 跳过__init__.py文件
                module_name = f"{module_path}.{filename}"

                try:
                    # 动态导入模块
                    module = importlib.import_module(module_name)

                    # 查找模块中的router对象
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)

                        # 检查是否是APIRouter实例
                        if isinstance(attr, APIRouter):
                            # 注册路由
                            app.include_router(attr)
                            logger.info(f"成功注册路由: {module_name}.{attr_name}")
                            registered_count += 1

                except Exception as e:
                    logger.error(f"注册路由失败: {module_name}, 错误: {str(e)}")
                    failed_count += 1

    logger.info(f"路由注册完成: 成功 {registered_count} 个, 跳过 {skipped_count} 个, 失败 {failed_count} 个")
