from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from src.db.db import get_db
from src.pojo.po.sessionPo import Session as SessionModel, SessionInfo
from src.dao.sessionDao import (
    create_session, 
    get_session_by_id, 
    get_sessions_by_user_id, 
    search_sessions,
    update_session,
    delete_session,
    get_session_with_details,
    get_recent_sessions
)
from src.myHttp.bo.httpResponse import HttpResponse, HttpResponseModel
from pydantic import BaseModel

from src.service.sessionService import when_search_session

router = APIRouter(prefix="/ai/session", tags=["Session"])

# 创建会话的请求模型
class SessionCreate(BaseModel):
    session_title: Optional[str] = None
    session_desc: Optional[str] = None
    user_id: str
    token: Optional[str] = None
    history_semantic: Optional[str] = None
    
    def to_po(self) -> SessionModel:
        """
        将VO转换为PO
        """
        return SessionModel(
            id=str(uuid.uuid4()),
            session_title=self.session_title,
            session_desc=self.session_desc,
            create_time=datetime.now(),
            user_id=self.user_id,
            token=self.token,
            history_semantic=self.history_semantic
        )

# 更新会话的请求模型
class SessionUpdate(BaseModel):
    session_title: Optional[str] = None
    session_desc: Optional[str] = None
    token: Optional[str] = None
    history_semantic: Optional[str] = None



@router.get("/{session_id}", response_model=HttpResponseModel[SessionModel])
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """
    根据会话ID获取会话信息
    
    Args:
        session_id: 会话ID
        db: 数据库会话
        
    Returns:
        会话信息
    """
    session = get_session_by_id(db, session_id)
    if not session:
        return HttpResponse.error(msg=f"Session with id {session_id} not found")
    return HttpResponse.success(session)

@router.get("/user/{user_id}", response_model=HttpResponseModel[List[SessionModel]])
async def get_user_sessions(user_id: str, db: Session = Depends(get_db)):
    """
    获取用户的所有会话
    
    Args:
        user_id: 用户ID
        db: 数据库会话
        
    Returns:
        会话列表
    """
    sessions = get_sessions_by_user_id(db, user_id)
    return HttpResponse.success(sessions)

@router.get("/user/{user_id}/recent", response_model=HttpResponseModel[List[SessionModel]])
async def get_user_recent_sessions(user_id: str, limit: int = 10, db: Session = Depends(get_db)):
    """
    获取用户最近的会话
    
    Args:
        user_id: 用户ID
        limit: 限制返回的会话数量
        db: 数据库会话
        
    Returns:
        会话列表
    """
    sessions = get_recent_sessions(db, user_id, limit)
    return HttpResponse.success(sessions)

@router.get("/{session_id}/details")
async def get_session_details(session_id: str, db: Session = Depends(get_db)):
    """
    获取会话及其详情
    
    Args:
        session_id: 会话ID
        db: 数据库会话
        
    Returns:
        会话及其详情
    """
    result = when_search_session(db, session_id)

    return HttpResponse.success(result)

@router.post("/", response_model=HttpResponseModel[SessionModel])
async def create_session_endpoint(session_data: SessionCreate, db: Session = Depends(get_db)):
    """
    创建会话
    
    Args:
        session_data: 会话数据
        db: 数据库会话
        
    Returns:
        创建的会话
    """
    try:
        # 转换为PO并创建
        session_po = session_data.to_po()
        created_session = create_session(db, session_po)
        return HttpResponse.success(created_session)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.put("/{session_id}", response_model=HttpResponseModel[SessionModel])
async def update_session_endpoint(session_id: str, session_data: SessionUpdate, db: Session = Depends(get_db)):
    """
    更新会话
    
    Args:
        session_id: 会话ID
        session_data: 更新的会话数据
        db: 数据库会话
        
    Returns:
        更新后的会话
    """
    # 转换为字典
    update_data = session_data.model_dump(exclude_unset=True)
    
    # 更新会话
    updated_session = update_session(db, session_id, update_data)
    if not updated_session:
        return HttpResponse.error(msg=f"Session with id {session_id} not found")
    
    return HttpResponse.success(updated_session)

@router.delete("/{session_id}", response_model=HttpResponseModel[bool])
async def delete_session_endpoint(session_id: str, db: Session = Depends(get_db)):
    """
    删除会话
    
    Args:
        session_id: 会话ID
        db: 数据库会话
        
    Returns:
        是否成功删除
    """
    result = delete_session(db, session_id)
    if not result:
        return HttpResponse.error(msg=f"Session with id {session_id} not found")
    
    return HttpResponse.success(True)

@router.post("/search", response_model=HttpResponseModel[List[SessionModel]])
async def search_sessions_endpoint(search_params: Dict[str, Any] | None, db: Session = Depends(get_db)):
    """
    搜索会话

    Args:
        search_params: 搜索参数
        db: 数据库会话

    Returns:
        符合条件的会话列表
    """
    try:
        results = search_sessions(db, search_params)
        return HttpResponse.success(results)
    except Exception as e:
        return HttpResponse.error(msg=str(e))
