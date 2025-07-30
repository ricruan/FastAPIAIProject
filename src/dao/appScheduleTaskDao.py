from typing import Optional, Dict, List, Any, Sequence
from datetime import datetime, timedelta

from sqlmodel import Session, select, delete, update
from sqlalchemy import func, and_, or_, between

from src.exception.aiException import AIException
from src.pojo.po.appScheduleTaskPo import AppScheduleTask, TaskStatus, TaskType, TaskSource

def create_schedule_task(session: Session, task: AppScheduleTask) -> AppScheduleTask:
    """
    创建日程或任务

    Args:
        session: 数据库会话
        task: 日程/任务模型实例

    Returns:
        创建后的日程/任务模型实例
    """
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def batch_create_schedule_tasks(session: Session, tasks: List[AppScheduleTask]) -> List[AppScheduleTask]:
    """
    批量创建日程或任务

    Args:
        session: 数据库会话
        tasks: 日程/任务模型实例列表

    Returns:
        创建后的日程/任务模型实例列表
    """
    session.add_all(tasks)
    session.commit()
    for task in tasks:
        session.refresh(task)
    return tasks

def get_schedule_task_by_id(session: Session, task_id: str) -> Optional[AppScheduleTask]:
    """
    通过ID获取日程或任务

    Args:
        session: 数据库会话
        task_id: 日程/任务ID

    Returns:
        日程/任务模型实例，如果不存在则返回None
    """
    statement = select(AppScheduleTask).where(AppScheduleTask.id == task_id)
    result = session.exec(statement).first()
    return result

def get_schedule_task_by_id_with_check(session: Session, task_id: str) -> AppScheduleTask:
    """
    带校验获取日程或任务，如果没找到直接报错

    Args:
        session: 数据库会话
        task_id: 日程/任务ID

    Returns:
        日程/任务模型实例

    Raises:
        AIException: 如果找不到对应的日程/任务
    """
    task = get_schedule_task_by_id(session, task_id)
    if task is None:
        raise AIException.quick_raise(f"没有找到对应的日程/任务(id:{task_id})")
    return task

def search_schedule_tasks(session: Session, search_params: Dict[str, Any]) -> Sequence[AppScheduleTask]:
    """
    根据提供的参数搜索日程或任务，使用AppScheduleTask中定义的like_search_fields
    来决定查询方式

    Args:
        session: 数据库会话
        search_params: 搜索参数字典，键为AppScheduleTask的字段名，值为搜索条件

    Returns:
        符合条件的AppScheduleTask列表
    """
    statement = select(AppScheduleTask)

    # 获取AppScheduleTask类的所有字段名
    task_fields = [column.name for column in AppScheduleTask.__table__.columns]

    # 动态构建查询条件
    for field, value in search_params.items():
        if field in task_fields and value is not None:
            # 根据字段是否在like_search_fields中决定查询方式
            if field in AppScheduleTask.like_search_fields and isinstance(value, str):
                statement = statement.where(getattr(AppScheduleTask, field).like(f"%{value}%"))
            else:
                # 对于其他字段，使用精确匹配
                statement = statement.where(getattr(AppScheduleTask, field) == value)

    # 执行查询
    results = session.exec(statement).all()
    return results

def update_schedule_task(session: Session, task_id: str, update_data: Dict[str, Any]) -> Optional[AppScheduleTask]:
    """
    更新日程或任务

    Args:
        session: 数据库会话
        task_id: 日程/任务ID
        update_data: 要更新的数据字典

    Returns:
        更新后的日程/任务模型实例，如果不存在则返回None
    """
    # 先获取日程/任务
    db_task = get_schedule_task_by_id(session, task_id)
    if not db_task:
        return None

    # 更新字段
    for field, value in update_data.items():
        if hasattr(db_task, field):
            setattr(db_task, field, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

def delete_schedule_task(session: Session, task_id: str) -> bool:
    """
    删除日程或任务

    Args:
        session: 数据库会话
        task_id: 日程/任务ID

    Returns:
        是否成功删除
    """
    db_task = get_schedule_task_by_id(session, task_id)
    if not db_task:
        return False

    session.delete(db_task)
    session.commit()
    return True

def get_schedule_tasks_by_user_id(session: Session, user_id: str) -> Sequence[AppScheduleTask]:
    """
    通过用户ID获取日程或任务列表

    Args:
        session: 数据库会话
        user_id: 用户ID

    Returns:
        日程/任务模型实例列表
    """
    statement = select(AppScheduleTask).where(AppScheduleTask.user_id == user_id)
    results = session.exec(statement).all()
    return results

def get_schedule_tasks_by_status(session: Session, status: TaskStatus) -> Sequence[AppScheduleTask]:
    """
    通过状态获取日程或任务列表

    Args:
        session: 数据库会话
        status: 任务状态

    Returns:
        日程/任务模型实例列表
    """
    statement = select(AppScheduleTask).where(AppScheduleTask.status == status)
    results = session.exec(statement).all()
    return results

def get_schedule_tasks_by_type(session: Session, task_type: TaskType) -> Sequence[AppScheduleTask]:
    """
    通过类型获取日程或任务列表

    Args:
        session: 数据库会话
        task_type: 任务类型

    Returns:
        日程/任务模型实例列表
    """
    statement = select(AppScheduleTask).where(AppScheduleTask.type == task_type)
    results = session.exec(statement).all()
    return results

def get_schedule_tasks_by_date(session: Session, date: datetime) -> Sequence[AppScheduleTask]:
    """
    获取指定日期的日程或任务

    Args:
        session: 数据库会话
        date: 指定日期

    Returns:
        日程/任务模型实例列表
    """
    # 获取指定日期的开始和结束时间
    start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
    end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)

    # 查询条件：开始时间在当天，或结束时间在当天，或跨越当天（开始时间在当天之前且结束时间在当天之后）
    statement = select(AppScheduleTask).where(
        or_(
            and_(AppScheduleTask.start_time >= start_of_day, AppScheduleTask.start_time <= end_of_day),
            and_(AppScheduleTask.end_time >= start_of_day, AppScheduleTask.end_time <= end_of_day),
            and_(AppScheduleTask.start_time <= start_of_day, AppScheduleTask.end_time >= end_of_day)
        )
    )

    results = session.exec(statement).all()
    return results

def get_schedule_tasks_ending_soon(session: Session,user_id: str, hours: int) -> Sequence[AppScheduleTask]:
    """
    获取即将结束的日程或任务（离开始时间只差N个小时）

    Args:
        :param session: 数据库会话
        :param hours:  小时数
        :param user_id:  用户ID

    Returns:
        日程/任务模型实例列表

    """
    # 计算当前时间和N小时后的时间
    now = datetime.now()
    n_hours_later = now + timedelta(hours=hours)

    # 查询条件：结束时间在当前时间和N小时后之间，且状态为未完成
    # TaskStatus.INCOMPLETE 的值为 "0"，表示未完成状态
    statement = select(AppScheduleTask).where(
        and_(
            AppScheduleTask.user_id == user_id,
            AppScheduleTask.end_time >= now,
            AppScheduleTask.start_time <= n_hours_later,
            AppScheduleTask.status == TaskStatus.INCOMPLETE  # "0"
        )
    )

    results = session.exec(statement).all()
    return results

def get_overdue_schedule_tasks(session: Session) -> Sequence[AppScheduleTask]:
    """
    获取已过期但未完成的日程或任务

    Args:
        session: 数据库会话

    Returns:
        日程/任务模型实例列表
    """
    now = datetime.now()

    # 查询条件：结束时间已过，但状态仍为未完成
    # TaskStatus.INCOMPLETE 的值为 "0"，表示未完成状态
    statement = select(AppScheduleTask).where(
        and_(
            AppScheduleTask.end_time < now,
            AppScheduleTask.status == TaskStatus.INCOMPLETE  # "0"
        )
    )

    results = session.exec(statement).all()
    return results

def get_upcoming_schedule_tasks(session: Session, days: int = 7) -> Sequence[AppScheduleTask]:
    """
    获取未来N天内的日程或任务

    Args:
        session: 数据库会话
        days: 天数，默认为7天

    Returns:
        日程/任务模型实例列表
    """
    now = datetime.now()
    future_date = now + timedelta(days=days)

    # 查询条件：开始时间在当前时间和未来N天之间
    statement = select(AppScheduleTask).where(
        and_(
            AppScheduleTask.start_time >= now,
            AppScheduleTask.start_time <= future_date
        )
    )

    results = session.exec(statement).all()
    return results

def mark_schedule_task_as_complete(session: Session, task_id: str, is_complete: bool = True) -> Optional[AppScheduleTask]:
    """
    将日程或任务标记为已完成

    Args:
        session: 数据库会话
        task_id: 日程/任务ID

    Returns:
        更新后的日程/任务模型实例，如果不存在则返回None
        :param task_id:
        :param session:
        :param is_complete:
    """
    db_task = get_schedule_task_by_id(session, task_id)
    if not db_task:
        return None

    # TaskStatus.COMPLETE 的值为 "1"，表示已完成状态
    db_task.status = TaskStatus.COMPLETE if is_complete else TaskStatus.INCOMPLETE
    db_task.complete_time = datetime.now() if is_complete else None

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

def count_schedule_tasks(session: Session) -> int:
    """
    统计日程或任务数量

    Args:
        session: 数据库会话

    Returns:
        日程/任务的数量
    """
    statement = select(func.count()).select_from(AppScheduleTask)
    result = session.exec(statement).one()
    return result

def count_schedule_tasks_by_status(session: Session, status: TaskStatus) -> int:
    """
    统计特定状态的日程或任务数量

    Args:
        session: 数据库会话
        status: 任务状态

    Returns:
        特定状态的日程/任务数量
    """
    statement = select(func.count()).select_from(AppScheduleTask).where(AppScheduleTask.status == status)
    result = session.exec(statement).one()
    return result

def count_schedule_tasks_by_type(session: Session, task_type: TaskType) -> int:
    """
    统计特定类型的日程或任务数量

    Args:
        session: 数据库会话
        task_type: 任务类型

    Returns:
        特定类型的日程/任务数量
    """
    statement = select(func.count()).select_from(AppScheduleTask).where(AppScheduleTask.type == task_type)
    result = session.exec(statement).one()
    return result

def get_all_schedule_tasks(session: Session) -> Sequence[AppScheduleTask]:
    """
    获取所有日程或任务

    Args:
        session: 数据库会话

    Returns:
        所有日程/任务模型实例列表
    """
    statement = select(AppScheduleTask)
    results = session.exec(statement).all()
    return results

def get_schedule_tasks_by_date_range(session: Session, start_date: datetime, end_date: datetime) -> Sequence[AppScheduleTask]:
    """
    获取指定日期范围内的日程或任务

    Args:
        session: 数据库会话
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        日程/任务模型实例列表
    """
    # 查询条件：开始时间或结束时间在指定日期范围内，或跨越整个日期范围
    statement = select(AppScheduleTask).where(
        or_(
            and_(AppScheduleTask.start_time >= start_date, AppScheduleTask.start_time <= end_date),
            and_(AppScheduleTask.end_time >= start_date, AppScheduleTask.end_time <= end_date),
            and_(AppScheduleTask.start_time <= start_date, AppScheduleTask.end_time >= end_date)
        )
    )
    
    results = session.exec(statement).all()
    return results

def get_important_urgent_tasks(session: Session) -> Sequence[AppScheduleTask]:
    """
    获取重要且紧急的任务

    Args:
        session: 数据库会话

    Returns:
        重要且紧急的任务列表
    """
    from src.pojo.po.appScheduleTaskPo import ImportanceFlag, UrgencyFlag
    
    # 使用字符串形式的数字作为枚举值
    # ImportanceFlag.IMPORTANT 的值为 "1"，表示重要
    # UrgencyFlag.URGENT 的值为 "1"，表示紧急
    # TaskStatus.INCOMPLETE 的值为 "0"，表示未完成
    statement = select(AppScheduleTask).where(
        and_(
            AppScheduleTask.is_important == ImportanceFlag.IMPORTANT,  # "1"
            AppScheduleTask.is_urgent == UrgencyFlag.URGENT,  # "1"
            AppScheduleTask.status == TaskStatus.INCOMPLETE  # "0"
        )
    )
    
    results = session.exec(statement).all()
    return results

def get_tasks_by_importance_urgency(session: Session, is_important: bool, is_urgent: bool) -> Sequence[AppScheduleTask]:
    """
    根据重要性和紧急性获取任务

    Args:
        session: 数据库会话
        is_important: 是否重要
        is_urgent: 是否紧急

    Returns:
        符合条件的任务列表
    """
    from src.pojo.po.appScheduleTaskPo import ImportanceFlag, UrgencyFlag
    
    # 使用字符串形式的数字作为枚举值
    importance_flag = ImportanceFlag.IMPORTANT if is_important else ImportanceFlag.NOT_IMPORTANT  # "1" 或 "0"
    urgency_flag = UrgencyFlag.URGENT if is_urgent else UrgencyFlag.NOT_URGENT  # "1" 或 "0"
    
    statement = select(AppScheduleTask).where(
        and_(
            AppScheduleTask.is_important == importance_flag,
            AppScheduleTask.is_urgent == urgency_flag
        )
    )
    
    results = session.exec(statement).all()
    return results