import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, SQLModel
import logging

# 获取logger
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# MySQL 连接URL格式: mysql+pymysql://用户名:密码@主机:端口/数据库名?参数
DATABASE_URL = "mysql+pymysql://" + os.getenv("DATABASE_URL", "root:root@localhost:3306/stone_ai_db?charset=utf8mb4")

# 初始化数据库引擎
def init_db():
    """初始化数据库引擎"""
    global engine
    
    logger.info("数据库连接URL: %s", DATABASE_URL)
    
    try:
        # 创建引擎（echo=True可显示SQL日志）
        engine = create_engine(
            DATABASE_URL,
            echo=True,
            pool_pre_ping=True,  # 启用连接健康检查
            pool_recycle=3600  # 可选：每1小时回收连接（避免 MySQL 主动关闭）
        )
        logger.info("数据库引擎创建成功")
        return engine
    except Exception as e:
        logger.error("数据库引擎创建失败: %s", str(e))
        raise

# 创建引擎实例
engine = init_db()

def create_tables():
    """创建所有数据库表"""
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        logger.error("数据库表创建失败: %s", str(e))
        raise


def get_db():
    with Session(engine) as session:
        yield session