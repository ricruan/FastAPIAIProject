import logging
import sys
import time
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

def setup_logging():
    """
    配置日志系统，按天生成日志文件
    """
    # 创建logs目录（如果不存在）
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 创建日志格式
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

    # 添加按天轮转的文件处理器
    log_file_path = log_dir / "app.log"
    file_handler = TimedRotatingFileHandler(
        filename=log_file_path,
        when='midnight',  # 每天午夜轮转
        interval=1,       # 每1天轮转一次
        backupCount=30,   # 保留30天的日志
        encoding='utf-8',
        atTime=None       # 在午夜时分轮转
    )
    # 设置后缀名格式为 .YYYY-MM-DD
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # 添加专门用于ERROR级别日志的文件处理器
    error_log_file_path = log_dir / "app.error.log"
    error_file_handler = TimedRotatingFileHandler(
        filename=error_log_file_path,
        when='midnight',  # 每天午夜轮转
        interval=1,       # 每1天轮转一次
        backupCount=30,   # 保留30天的日志
        encoding='utf-8',
        atTime=None       # 在午夜时分轮转
    )
    # 设置后缀名格式为 .YYYY-MM-DD
    error_file_handler.suffix = "%Y-%m-%d"
    error_file_handler.setFormatter(log_format)
    # 只处理ERROR及以上级别的日志
    error_file_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_file_handler)
    
    logging.info(f"日志系统初始化完成，常规日志文件将保存在: {log_file_path}")
    logging.info(f"错误日志文件将保存在: {error_log_file_path}")
