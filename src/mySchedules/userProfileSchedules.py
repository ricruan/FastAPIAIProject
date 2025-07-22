import asyncio
import logging
from aiojobs import Scheduler
from datetime import datetime, time, timedelta
from typing import Optional

from src.service.userProfileService import analysis_all

# 配置日志
logger = logging.getLogger(__name__)

# 可配置参数
class ScheduleConfig:
    # 默认执行时间为每天0点
    EXECUTION_HOUR: int = 0
    EXECUTION_MINUTE: int = 0
    # 最大重试次数
    MAX_RETRIES: int = 3
    # 重试间隔（秒）
    RETRY_INTERVAL: int = 300  # 5分钟
    # 任务超时时间（秒）
    TASK_TIMEOUT: int = 3600  # 1小时

# 全局调度器
scheduler = None

async def execute_task():
    """执行分析任务，包含错误处理和重试逻辑"""
    retries = 0
    while retries <= ScheduleConfig.MAX_RETRIES:
        try:
            logger.info("开始执行用户画像分析任务")
            # 设置超时
            task = asyncio.create_task(analysis_all())
            await asyncio.wait_for(task, timeout=ScheduleConfig.TASK_TIMEOUT)
            logger.info("用户画像分析任务执行完成")
            return
        except asyncio.TimeoutError:
            logger.error(f"用户画像分析任务执行超时（{ScheduleConfig.TASK_TIMEOUT}秒）")
            break  # 超时直接退出，不重试
        except Exception as e:
            retries += 1
            logger.error(f"用户画像分析任务执行失败: {str(e)}, 重试次数: {retries}/{ScheduleConfig.MAX_RETRIES}")
            if retries <= ScheduleConfig.MAX_RETRIES:
                await asyncio.sleep(ScheduleConfig.RETRY_INTERVAL)
            else:
                logger.critical("用户画像分析任务达到最大重试次数，放弃执行")

async def schedule_daily_task():
    """调度每日任务，防止任务重叠执行"""
    global scheduler
    
    # 任务执行标志，防止重叠执行
    is_task_running = False
    
    while True:
        try:
            now = datetime.now()
            # 计算距离下一个指定时间点的时间差
            target_time = datetime.combine(
                now.date() + (timedelta(days=1) if now.time() >= time(ScheduleConfig.EXECUTION_HOUR, ScheduleConfig.EXECUTION_MINUTE) else timedelta(days=0)),
                time(ScheduleConfig.EXECUTION_HOUR, ScheduleConfig.EXECUTION_MINUTE)
            )
            delay_seconds = (target_time - now).total_seconds()

            unit = "分钟" if delay_seconds < 3600 else "小时"
            value = delay_seconds / 60 if unit == "分钟" else delay_seconds / 3600
            logger.info(f"下一次用户画像分析任务将在 {value:.2f} {unit}后执行（目标时间: {target_time}）")
            
            # 先等待到指定时间
            await asyncio.sleep(delay_seconds)
            logger.info("用户画像分析任务准备开始执行")
            
            # 然后执行任务
            # 检查是否有任务正在运行
            if not is_task_running:
                is_task_running = True
                try:
                    # 使用调度器执行任务，如果调度器不可用则直接执行
                    if scheduler is not None:
                        # 使用spawn方法创建任务，传递协程函数而不是调用结果
                        await scheduler.spawn(execute_task())
                    else:
                        # 调度器不可用，直接执行任务
                        logger.warning("调度器不可用，直接执行任务")
                        await execute_task()
                finally:
                    is_task_running = False
            else:
                logger.warning("上一个用户画像分析任务仍在执行中，跳过本次执行")
        except Exception as e:
            logger.error(f"调度器异常: {str(e)}")
            # 出现异常时等待一段时间再继续
            await asyncio.sleep(60)

async def start_scheduler():
    """在 FastAPI 启动时运行定时任务"""
    global scheduler
    try:
        logger.info("启动用户画像分析调度器")
        # 直接实例化Scheduler类
        scheduler = Scheduler(close_timeout=10.0)
        # 创建调度任务但不等待它完成
        asyncio.create_task(schedule_daily_task())
    except Exception as e:
        logger.error(f"启动调度器失败: {str(e)}")

async def stop_scheduler():
    """在 FastAPI 关闭时清理资源"""
    global scheduler
    if scheduler:
        logger.info("关闭用户画像分析调度器")
        await scheduler.close()
        scheduler = None

# 允许手动触发任务的函数
async def trigger_analysis_manually():
    """手动触发用户画像分析任务"""
    logger.info("手动触发用户画像分析任务")
    try:
        await execute_task()
        return {"status": "success", "message": "用户画像分析任务已完成"}
    except Exception as e:
        logger.error(f"手动触发任务失败: {str(e)}")
        return {"status": "error", "message": f"任务执行失败: {str(e)}"}

if __name__ == "__main__":
    # 运行手动触发分析的函数
    import asyncio
    
    async def main():
        print("手动启动用户画像分析...")
        result = await trigger_analysis_manually()
        print(f"分析结果: {result}")
    
    # 使用asyncio.run()运行异步主函数
    asyncio.run(main())
