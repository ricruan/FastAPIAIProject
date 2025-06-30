from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict, Any, List, Optional, Sequence
from datetime import datetime
import uuid

from src.db.db import get_db
from src.pojo.po.sessionDetailPo import SessionDetail
from src.dao.sessionDetailDao import (
    create_session_detail,
    batch_create_session_details,
    get_session_detail_by_id,
    get_session_details_by_session_id,
    search_session_details,
    update_session_detail,
    delete_session_detail,
    delete_session_details_by_session_id,
    get_latest_session_detail,
    count_session_details
)
from src.myHttp.bo.httpResponse import HttpResponse, HttpResponseModel
from pydantic import BaseModel

router = APIRouter(prefix="/ai/session-detail", tags=["Session Detail"])

# 创建会话详情的请求模型
class SessionDetailCreate(BaseModel):
    session_id: str
    dialog_carrier: Optional[str] = None
    api_input: Optional[str] = None
    api_output: Optional[str] = None
    user_question: Optional[str] = None
    final_response: Optional[str] = None
    process_log: Optional[str] = None
    model: Optional[str] = None
    agent: Optional[str] = None
    status: Optional[str] = None

    def to_po(self) -> SessionDetail:
        """
        将VO转换为PO
        """
        return SessionDetail(
            id=str(uuid.uuid4()),
            session_id=self.session_id,
            dialog_carrier=self.dialog_carrier,
            api_input=self.api_input,
            api_output=self.api_output,
            user_question=self.user_question,
            final_response=self.final_response,
            process_log=self.process_log,
            model=self.model,
            agent=self.agent,
            status=self.status,
            create_time=datetime.now()
        )

# 批量创建会话详情的请求模型
class BatchSessionDetailCreate(BaseModel):
    details: List[SessionDetailCreate]

# 更新会话详情的请求模型
class SessionDetailUpdate(BaseModel):
    dialog_carrier: Optional[str] = None
    api_input: Optional[str] = None
    api_output: Optional[str] = None
    user_question: Optional[str] = None
    final_response: Optional[str] = None
    process_log: Optional[str] = None
    model: Optional[str] = None
    agent: Optional[str] = None
    status: Optional[str] = None

@router.get("/{detail_id}", response_model=HttpResponseModel[SessionDetail])
async def get_session_detail(detail_id: str, db: Session = Depends(get_db)):
    """
    根据ID获取会话详情

    Args:
        detail_id: 会话详情ID
        db: 数据库会话

    Returns:
        会话详情
    """
    detail = get_session_detail_by_id(db, detail_id)
    if not detail:
        return HttpResponse.error(msg=f"Session detail with id {detail_id} not found")
    return HttpResponse.success(detail)

@router.get("/session/{session_id}", response_model=HttpResponseModel[List[SessionDetail]])
async def get_session_details(session_id: str, db: Session = Depends(get_db)):
    """
    获取会话的所有详情

    Args:
        session_id: 会话ID
        db: 数据库会话

    Returns:
        会话详情列表
    """
    details = get_session_details_by_session_id(db, session_id)
    return HttpResponse.success(details)

@router.get("/session/{session_id}/latest", response_model=HttpResponseModel[SessionDetail])
async def get_latest_detail(session_id: str, db: Session = Depends(get_db)):
    """
    获取会话的最新详情

    Args:
        session_id: 会话ID
        db: 数据库会话

    Returns:
        最新的会话详情
    """
    detail = get_latest_session_detail(db, session_id)
    if not detail:
        return HttpResponse.error(msg=f"No details found for session {session_id}")
    return HttpResponse.success(detail)

@router.get("/session/{session_id}/count", response_model=HttpResponseModel[int])
async def count_details(session_id: str, db: Session = Depends(get_db)):
    """
    统计会话的详情数量

    Args:
        session_id: 会话ID
        db: 数据库会话

    Returns:
        会话详情数量
    """
    count = count_session_details(db, session_id)
    return HttpResponse.success(count)

@router.post("/", response_model=HttpResponseModel[SessionDetail])
async def create_detail(detail_data: SessionDetailCreate, db: Session = Depends(get_db)):
    """
    创建会话详情

    Args:
        detail_data: 会话详情数据
        db: 数据库会话

    Returns:
        创建的会话详情
    """
    try:
        # 转换为PO并创建
        detail_po = detail_data.to_po()
        created_detail = create_session_detail(db, detail_po)
        return HttpResponse.success(created_detail)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.post("/batch", response_model=HttpResponseModel[List[SessionDetail]])
async def batch_create_details(batch_data: BatchSessionDetailCreate, db: Session = Depends(get_db)):
    """
    批量创建会话详情

    Args:
        batch_data: 批量会话详情数据
        db: 数据库会话

    Returns:
        创建的会话详情列表
    """
    try:
        # 转换为PO并批量创建
        detail_pos = [detail.to_po() for detail in batch_data.details]
        created_details = batch_create_session_details(db, detail_pos)
        return HttpResponse.success(created_details)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.put("/{detail_id}", response_model=HttpResponseModel[SessionDetail])
async def update_detail(detail_id: str, detail_data: SessionDetailUpdate, db: Session = Depends(get_db)):
    """
    更新会话详情

    Args:
        detail_id: 会话详情ID
        detail_data: 更新的会话详情数据
        db: 数据库会话

    Returns:
        更新后的会话详情
    """
    # 转换为字典
    update_data = detail_data.dict(exclude_unset=True)

    # 更新会话详情
    updated_detail = update_session_detail(db, detail_id, update_data)
    if not updated_detail:
        return HttpResponse.error(msg=f"Session detail with id {detail_id} not found")

    return HttpResponse.success(updated_detail)

@router.delete("/{detail_id}", response_model=HttpResponseModel[bool])
async def delete_detail(detail_id: str, db: Session = Depends(get_db)):
    """
    删除会话详情

    Args:
        detail_id: 会话详情ID
        db: 数据库会话

    Returns:
        是否成功删除
    """
    result = delete_session_detail(db, detail_id)
    if not result:
        return HttpResponse.error(msg=f"Session detail with id {detail_id} not found")

    return HttpResponse.success(True)

@router.delete("/session/{session_id}", response_model=HttpResponseModel[int])
async def delete_session_details(session_id: str, db: Session = Depends(get_db)):
    """
    删除会话的所有详情

    Args:
        session_id: 会话ID
        db: 数据库会话

    Returns:
        删除的记录数量
    """
    count = delete_session_details_by_session_id(db, session_id)
    return HttpResponse.success(count)

@router.post("/search", response_model=HttpResponseModel[List[SessionDetail]])
async def search_details(search_params: Dict[str, Any] | None, db: Session = Depends(get_db)):
    """
    搜索会话详情

    Args:
        search_params: 搜索参数
        db: 数据库会话

    Returns:
        符合条件的会话详情列表
    """
    try:
        results = search_session_details(db, search_params)
        return HttpResponse.success(results)
    except Exception as e:
        return HttpResponse.error(msg=str(e))
