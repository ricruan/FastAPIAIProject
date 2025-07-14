from typing import Optional, Dict, List, Any, Sequence
from datetime import datetime

from sqlmodel import Session, select, delete, update, desc
from sqlalchemy.orm import joinedload

from src.pojo.po.sessionPo import SessionPo as SessionModel
from src.pojo.po.sessionDetailPo import SessionDetail

def create_session(session: Session, session_model: SessionModel) -> SessionModel:
    """
    创建会话

    Args:
        session: 数据库会话
        session_model: 会话模型实例

    Returns:
        创建后的会话模型实例
    """
    session.add(session_model)
    session.commit()
    session.refresh(session_model)
    return session_model

def get_session_by_id(session: Session, session_id: str) -> Optional[SessionModel]:
    """
    通过ID获取会话

    Args:
        session: 数据库会话
        session_id: 会话ID

    Returns:
        会话模型实例，如果不存在则返回None
    """
    statement = select(SessionModel).where(SessionModel.id == session_id)
    result = session.exec(statement).first()
    return result

def get_sessions_by_user_id(session: Session, user_id: str) -> Sequence[SessionModel]:
    """
    通过用户ID获取会话列表

    Args:
        session: 数据库会话
        user_id: 用户ID

    Returns:
        会话模型实例列表
    """
    statement = select(SessionModel).where(SessionModel.user_id == user_id).order_by(SessionModel.update_time.desc())
    results = session.exec(statement).all()
    return results

def search_sessions(session: Session, search_params: Dict[str, Any]) -> Sequence[SessionModel]:
    """
    根据提供的参数搜索会话，使用SessionModel中定义的like_search_fields
    来决定查询方式

    Args:
        session: 数据库会话
        search_params: 搜索参数字典，键为SessionModel的字段名，值为搜索条件

    Returns:
        符合条件的SessionModel列表
    """
    statement = select(SessionModel)

    # 获取SessionModel类的所有字段名
    session_fields = [column.name for column in SessionModel.__table__.columns]

    # 动态构建查询条件
    for field, value in search_params.items():
        if field in session_fields and value is not None:
            # 根据字段是否在like_search_fields中决定查询方式
            if field in SessionModel.like_search_fields and isinstance(value, str):
                statement = statement.where(getattr(SessionModel, field).like(f"%{value}%"))
            else:
                # 对于其他字段，使用精确匹配
                statement = statement.where(getattr(SessionModel, field) == value)

    # 执行查询
    results = session.exec(statement).all()
    return results

def update_session(session: Session, session_id: str, update_data: Dict[str, Any]) -> Optional[SessionModel]:
    """
    更新会话

    Args:
        session: 数据库会话
        session_id: 会话ID
        update_data: 要更新的数据字典

    Returns:
        更新后的会话模型实例，如果不存在则返回None
    """
    # 先获取会话
    db_session = get_session_by_id(session, session_id)
    if not db_session:
        return None

    # 更新字段
    for field, value in update_data.items():
        if hasattr(db_session, field):
            setattr(db_session, field, value)

    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    return db_session

def delete_session(session: Session, session_id: str) -> bool:
    """
    删除会话

    Args:
        session: 数据库会话
        session_id: 会话ID

    Returns:
        是否成功删除
    """
    db_session = get_session_by_id(session, session_id)
    if not db_session:
        return False

    session.delete(db_session)
    session.commit()
    return True

def get_session_with_details(session: Session, session_id: str) -> Optional[Dict[str, Any]]:
    """
    获取会话及其详情

    Args:
        session: 数据库会话
        session_id: 会话ID

    Returns:
        包含会话和详情的字典，如果不存在则返回None
    """
    # 获取会话
    db_session = get_session_by_id(session, session_id)
    if not db_session:
        return None

    # 获取会话详情
    statement = select(SessionDetail).where(SessionDetail.session_id == session_id)
    details = session.exec(statement).all()

    # 构建结果
    result = {
        "session": db_session,
        "details": details
    }

    return result

def get_recent_sessions(session: Session, user_id: str, limit: int = 10) -> Sequence[SessionModel]:
    """
    获取用户最近的会话

    Args:
        session: 数据库会话
        user_id: 用户ID
        limit: 限制返回的会话数量

    Returns:
        会话模型实例列表
    """
    statement = select(SessionModel).where(SessionModel.user_id == user_id).order_by(desc(SessionModel.create_time)).limit(limit)
    results = session.exec(statement).all()
    return results
