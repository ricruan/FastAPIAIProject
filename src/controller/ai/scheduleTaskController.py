from typing import List, Optional
from datetime import datetime, timedelta, date
import uuid

from fastapi import APIRouter, Depends, Query, Path
from sqlmodel import Session

from src.dao import appScheduleTaskDao
from src.db.db import get_db
from src.pojo.po.appScheduleTaskPo import AppScheduleTask, TaskType, TaskStatus, TaskSource, ImportanceFlag, UrgencyFlag
from src.myHttp.bo.httpResponse import HttpResponse, HttpResponseModel
from pydantic import BaseModel, Field

# 创建路由
router = APIRouter(prefix="/app/schedule-tasks", tags=["日程任务管理"])

# 请求和响应模型
class ScheduleTaskCreate(BaseModel):
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    content: Optional[str] = None
    is_urgent: Optional[str] = None
    is_important: Optional[str] = None
    attachment: Optional[str] = None

    def to_po_4_stone(self) -> AppScheduleTask:
        """
        将VO转换为PO  4 Stone ai
        """
        return AppScheduleTask(
            id=uuid.uuid4().hex,
            user_id=self.user_id,
            user_name=self.user_name,
            type=TaskType.SCHEDULE.value,
            start_time=self.start_time,
            end_time=self.end_time,
            create_time=datetime.now(),
            content=self.content,
            status=TaskStatus.INCOMPLETE.value,
            source=TaskSource.STONE.value,
            is_urgent=self.is_urgent or UrgencyFlag.NOT_URGENT.value,
            is_important=self.is_important or ImportanceFlag.NOT_IMPORTANT.value,
            attachment=self.attachment or ""
        )

class ScheduleTaskUpdate(BaseModel):
    user_name: Optional[str] = None
    type: Optional[TaskType] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    content: Optional[str] = None
    status: Optional[TaskStatus] = None
    source: Optional[TaskSource] = None
    is_urgent: Optional[UrgencyFlag] = None
    is_important: Optional[ImportanceFlag] = None
    attachment: Optional[str] = None

class BatchScheduleTaskCreate(BaseModel):
    tasks: List[ScheduleTaskCreate]

class ScheduleTaskSearch(BaseModel):
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    type: Optional[TaskType] = None
    status: Optional[TaskStatus] = None
    source: Optional[TaskSource] = None
    is_urgent: Optional[UrgencyFlag] = None
    is_important: Optional[ImportanceFlag] = None
    content: Optional[str] = None
    date: Optional[datetime] = None  # 新增日期字段，可以接收datetime类型

class CompleteParams(BaseModel):
    task_id: str
    is_complete: bool = True


# API接口 - 基本CRUD操作
@router.post("", response_model=HttpResponseModel[AppScheduleTask])
async def create_schedule_task(
    task_create: ScheduleTaskCreate,
    db: Session = Depends(get_db)
):
    """
    创建日程或任务
    
    Args:
        task_create: 日程/任务创建数据
        db: 数据库会话
        
    Returns:
        创建后的日程/任务
    """
    try:
        # 转换为PO并创建
        new_task = task_create.to_po_4_stone()
        created_task = appScheduleTaskDao.create_schedule_task(db, new_task)
        return HttpResponse.success(created_task)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.post("/batch", response_model=HttpResponseModel[List[AppScheduleTask]])
async def batch_create_schedule_tasks(
    batch_data: BatchScheduleTaskCreate,
    db: Session = Depends(get_db)
):
    """
    批量创建日程或任务
    
    Args:
        batch_data: 批量日程/任务创建数据
        db: 数据库会话
        
    Returns:
        创建后的日程/任务列表
    """
    try:
        # 转换为PO并批量创建
        new_tasks = [task.to_po_4_stone() for task in batch_data.tasks]
        created_tasks = appScheduleTaskDao.batch_create_schedule_tasks(db, new_tasks)
        return HttpResponse.success(created_tasks)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.get("/get/{task_id}", response_model=HttpResponseModel[AppScheduleTask])
async def get_schedule_task(
    task_id: str = Path(..., description="日程/任务ID"),
    db: Session = Depends(get_db)
):
    """
    获取日程或任务详情
    
    Args:
        task_id: 日程/任务ID
        db: 数据库会话
        
    Returns:
        日程/任务详情
    """
    task = appScheduleTaskDao.get_schedule_task_by_id(db, task_id)
    if not task:
        return HttpResponse.error(msg=f"日程/任务不存在: {task_id}")
    return HttpResponse.success(task)

@router.put("/update/{task_id}", response_model=HttpResponseModel[AppScheduleTask])
async def update_schedule_task(
    task_update: ScheduleTaskUpdate,
    task_id: str = Path(..., description="日程/任务ID"),
    db: Session = Depends(get_db)
):
    """
    更新日程或任务
    
    Args:
        task_id: 日程/任务ID
        task_update: 更新数据
        db: 数据库会话
        
    Returns:
        更新后的日程/任务
    """
    # 转换为字典
    update_data = task_update.model_dump(exclude_unset=True)
    
    # 更新日程/任务
    updated_task = appScheduleTaskDao.update_schedule_task(db, task_id, update_data)
    if not updated_task:
        return HttpResponse.error(msg=f"日程/任务不存在: {task_id}")
    
    return HttpResponse.success(updated_task)

@router.delete("/del/{task_id}", response_model=HttpResponseModel[bool])
async def delete_schedule_task(
    task_id: str = Path(..., description="日程/任务ID"),
    db: Session = Depends(get_db)
):
    """
    删除日程或任务
    
    Args:
        task_id: 日程/任务ID
        db: 数据库会话
        
    Returns:
        是否成功删除
    """
    result = appScheduleTaskDao.delete_schedule_task(db, task_id)
    if not result:
        return HttpResponse.error(msg=f"日程/任务不存在: {task_id}")
    
    return HttpResponse.success(True)

@router.post("/search", response_model=HttpResponseModel[List[AppScheduleTask]])
async def search_schedule_tasks(
    search_params: ScheduleTaskSearch,
    db: Session = Depends(get_db)
):
    """
    搜索日程或任务
    
    Args:
        search_params: 搜索参数
        db: 数据库会话
        
    Returns:
        符合条件的日程/任务列表
    """
    try:
        # 将搜索参数转换为字典，排除未设置的字段
        search_dict = {k: v for k, v in search_params.model_dump().items() if v is not None and k != 'date'}
        
        # 检查是否有日期参数
        if search_params.date:
            # 将datetime转换为date
            query_date = search_params.date.date() if isinstance(search_params.date, datetime) else search_params.date
            
            # 计算当天的开始和结束时间
            start_of_day = datetime.combine(query_date, datetime.min.time())
            end_of_day = datetime.combine(query_date, datetime.max.time())
            
            # 如果有用户ID，则查询特定用户在特定日期的任务
            if search_params.user_id:
                # 先获取用户当天的所有任务
                tasks = appScheduleTaskDao.get_schedule_tasks_by_date_range(db, start_of_day, end_of_day)
                
                # 然后筛选出特定用户的任务
                tasks = [task for task in tasks if task.user_id == search_params.user_id]
                
                # 应用其他搜索条件
                for field, value in search_dict.items():
                    if field != 'user_id':  # 已经筛选过用户ID了
                        if field in AppScheduleTask.like_search_fields and isinstance(value, str):
                            tasks = [task for task in tasks if value.lower() in getattr(task, field, '').lower()]
                        else:
                            tasks = [task for task in tasks if getattr(task, field, None) == value]
                
                return HttpResponse.success(tasks)
            else:
                # 如果没有用户ID，则直接查询当天的所有任务，然后应用其他搜索条件
                tasks = appScheduleTaskDao.get_schedule_tasks_by_date_range(db, start_of_day, end_of_day)
                
                # 应用其他搜索条件
                for field, value in search_dict.items():
                    if field in AppScheduleTask.like_search_fields and isinstance(value, str):
                        tasks = [task for task in tasks if value.lower() in getattr(task, field, '').lower()]
                    else:
                        tasks = [task for task in tasks if getattr(task, field, None) == value]
                
                return HttpResponse.success(tasks)
        else:
            # 如果没有日期参数，则使用原有的搜索逻辑
            tasks = appScheduleTaskDao.search_schedule_tasks(db, search_dict)
            return HttpResponse.success(list(tasks))
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.get("/user/{user_id}", response_model=HttpResponseModel[List[AppScheduleTask]])
async def get_user_schedule_tasks(
    user_id: str = Path(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    获取用户的所有日程或任务
    
    Args:
        user_id: 用户ID
        db: 数据库会话
        
    Returns:
        用户的日程/任务列表
    """
    tasks = appScheduleTaskDao.get_schedule_tasks_by_user_id(db, user_id)
    return HttpResponse.success(list(tasks))

@router.get("/ending-soon/{hours}", response_model=HttpResponseModel[List[AppScheduleTask]])
async def get_ending_soon_tasks(
    hours: int = Path(..., description="小时数", ge=1, le=24),
    db: Session = Depends(get_db)
):
    """
    获取即将结束的日程或任务（离结束时间只差N个小时）
    
    Args:
        hours: 小时数
        db: 数据库会话
        
    Returns:
        即将结束的日程/任务列表
    """
    tasks = appScheduleTaskDao.get_schedule_tasks_ending_soon(db, hours)
    return HttpResponse.success(list(tasks), msg=f"获取成功，共{len(tasks)}条即将在{hours}小时内结束的任务")

@router.get("/today/ending-soon/{hours}", response_model=HttpResponseModel[List[AppScheduleTask]])
async def get_today_ending_soon_tasks(
    hours: int = Path(..., description="小时数", ge=1, le=24),
    db: Session = Depends(get_db)
):
    """
    获取今天截止结束时间近N小时的数据
    
    Args:
        hours: 小时数
        db: 数据库会话
        
    Returns:
        今天即将结束的日程/任务列表
    """
    # 获取今天的日期范围
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # 获取今天的所有任务
    today_tasks = appScheduleTaskDao.get_schedule_tasks_by_date_range(db, today_start, today_end)
    
    # 筛选出结束时间在N小时内的任务
    now = datetime.now()
    n_hours_later = now + timedelta(hours=hours)
    
    ending_soon_tasks = [
        task for task in today_tasks 
        if task.end_time and now <= task.end_time <= n_hours_later and task.status == TaskStatus.INCOMPLETE
    ]
    
    return HttpResponse.success(
        ending_soon_tasks,
        msg=f"获取成功，共{len(ending_soon_tasks)}条今天将在{hours}小时内即将结束的任务"
    )

@router.post("/complete", response_model=HttpResponseModel[AppScheduleTask])
async def mark_task_as_complete(
    params: CompleteParams,
    db: Session = Depends(get_db)
):
    """
    将日程或任务标记为已完成
    
    Args:
        :param params:
        :param db: 数据库会话
    Returns:
        更新后的日程/任务
    """
    completed_task = appScheduleTaskDao.mark_schedule_task_as_complete(db,params.task_id ,params.is_complete)
    if not completed_task:
        return HttpResponse.error(msg=f"日程/任务不存在: {params.task_id}")
    
    return HttpResponse.success(completed_task, msg="标记完成成功")

@router.get("/overdue", response_model=HttpResponseModel)
async def get_overdue_tasks(
    db: Session = Depends(get_db)
):
    """
    获取已过期但未完成的日程或任务
    
    Args:
        db: 数据库会话
        
    Returns:
        已过期但未完成的日程/任务列表
    """
    tasks = appScheduleTaskDao.get_overdue_schedule_tasks(db)
    return HttpResponse.success(list(tasks), msg=f"获取成功，共{len(tasks)}条已过期但未完成的任务")

@router.get("/upcoming/{days}", response_model=HttpResponseModel[List[AppScheduleTask]])
async def get_upcoming_tasks(
    days: int = Path(..., description="天数", ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    获取未来N天内的日程或任务
    
    Args:
        days: 天数
        db: 数据库会话
        
    Returns:
        未来N天内的日程/任务列表
    """
    tasks = appScheduleTaskDao.get_upcoming_schedule_tasks(db, days)
    return HttpResponse.success(list(tasks), msg=f"获取成功，共{len(tasks)}条未来{days}天内的任务")

@router.get("/important-urgent", response_model=HttpResponseModel[List[AppScheduleTask]])
async def get_important_urgent_tasks(
    db: Session = Depends(get_db)
):
    """
    获取重要且紧急的任务
    
    Args:
        db: 数据库会话
        
    Returns:
        重要且紧急的任务列表
    """
    tasks = appScheduleTaskDao.get_important_urgent_tasks(db)
    return HttpResponse.success(list(tasks), msg=f"获取成功，共{len(tasks)}条重要且紧急的任务")

@router.get("/by-importance-urgency", response_model=HttpResponseModel[List[AppScheduleTask]])
async def get_tasks_by_importance_urgency(
    is_important: bool = Query(None, description="是否重要"),
    is_urgent: bool = Query(None, description="是否紧急"),
    db: Session = Depends(get_db)
):
    """
    根据重要性和紧急性获取任务
    
    Args:
        is_important: 是否重要
        is_urgent: 是否紧急
        db: 数据库会话
        
    Returns:
        符合条件的任务列表
    """
    # 如果两个参数都未提供，返回所有任务
    if is_important is None and is_urgent is None:
        tasks = appScheduleTaskDao.get_all_schedule_tasks(db)
        return HttpResponse.success(list(tasks), msg="获取所有任务成功")
    
    # 如果只提供了一个参数，设置另一个为False
    if is_important is None:
        is_important = False
    if is_urgent is None:
        is_urgent = False
    
    # 调用DAO层根据重要性和紧急性获取任务
    tasks = appScheduleTaskDao.get_tasks_by_importance_urgency(db, is_important, is_urgent)
    
    importance_str = "重要" if is_important else "不重要"
    urgency_str = "紧急" if is_urgent else "不紧急"
    
    return HttpResponse.success(
        list(tasks),
        msg=f"获取成功，共{len(tasks)}条{importance_str}且{urgency_str}的任务"
    )