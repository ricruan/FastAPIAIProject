from typing import Optional, Dict, List, Any, Sequence

from sqlmodel import Session, select, delete, update

from src.pojo.po.sessionDetailPo import SessionDetail

def create_session_detail(session: Session, session_detail: SessionDetail) -> SessionDetail:
    """
    创建会话详情

    Args:
        session: 数据库会话
        session_detail: 会话详情模型实例

    Returns:
        创建后的会话详情模型实例
    """
    session_detail.handle_dict()
    session.add(session_detail)
    session.commit()
    session.refresh(session_detail)
    return session_detail

def batch_create_session_details(session: Session, session_details: List[SessionDetail]) -> List[SessionDetail]:
    """
    批量创建会话详情

    Args:
        session: 数据库会话
        session_details: 会话详情模型实例列表

    Returns:
        创建后的会话详情模型实例列表
    """
    session.add_all(session_details)
    session.commit()
    for detail in session_details:
        session.refresh(detail)
    return session_details

def get_session_detail_by_id(session: Session, detail_id: str) -> Optional[SessionDetail]:
    """
    通过ID获取会话详情

    Args:
        session: 数据库会话
        detail_id: 会话详情ID

    Returns:
        会话详情模型实例，如果不存在则返回None
    """
    statement = select(SessionDetail).where(SessionDetail.id == detail_id)
    result = session.exec(statement).first()
    return result

def get_session_details_by_session_id(session: Session, session_id: str) -> Sequence[SessionDetail]:
    """
    通过会话ID获取会话详情列表

    Args:
        session: 数据库会话
        session_id: 会话ID

    Returns:
        会话详情模型实例列表
    """
    statement = select(SessionDetail).where(SessionDetail.session_id == session_id).order_by(SessionDetail.create_time.asc())
    results = session.exec(statement).all()
    return results

def search_session_details(session: Session, search_params: Dict[str, Any],limit: int | None = None) -> Sequence[SessionDetail]:
    """
    根据提供的参数搜索会话详情，使用SessionDetail中定义的like_search_fields
    来决定查询方式

    Args:
        session: 数据库会话
        search_params: 搜索参数字典，键为SessionDetail的字段名，值为搜索条件
        limit: 搜索结果数量限制
    Returns:
        符合条件的SessionDetail列表
    """
    statement = select(SessionDetail)

    # 获取SessionDetail类的所有字段名
    session_detail_fields = [column.name for column in SessionDetail.__table__.columns]

    # 动态构建查询条件
    for field, value in search_params.items():
        if field in session_detail_fields and value is not None:
            # 根据字段是否在like_search_fields中决定查询方式
            if field in SessionDetail.like_search_fields and isinstance(value, str):
                statement = statement.where(getattr(SessionDetail, field).like(f"%{value}%"))
            else:
                # 对于其他字段，使用精确匹配
                statement = statement.where(getattr(SessionDetail, field) == value)

    # 执行查询
    results = session.exec(statement.order_by(SessionDetail.create_time.desc()).limit(limit)).all()
    return results

def update_session_detail(session: Session, detail_id: str, update_data: Dict[str, Any]) -> Optional[SessionDetail]:
    """
    更新会话详情

    Args:
        session: 数据库会话
        detail_id: 会话详情ID
        update_data: 要更新的数据字典

    Returns:
        更新后的会话详情模型实例，如果不存在则返回None
    """
    # 先获取会话详情
    db_detail = get_session_detail_by_id(session, detail_id)
    if not db_detail:
        return None

    # 更新字段
    for field, value in update_data.items():
        if hasattr(db_detail, field):
            setattr(db_detail, field, value)

    session.add(db_detail)
    session.commit()
    session.refresh(db_detail)
    return db_detail

def delete_session_detail(session: Session, detail_id: str) -> bool:
    """
    删除会话详情

    Args:
        session: 数据库会话
        detail_id: 会话详情ID

    Returns:
        是否成功删除
    """
    db_detail = get_session_detail_by_id(session, detail_id)
    if not db_detail:
        return False

    session.delete(db_detail)
    session.commit()
    return True

def delete_session_details_by_session_id(session: Session, session_id: str) -> int:
    """
    通过会话ID删除所有相关的会话详情

    Args:
        session: 数据库会话
        session_id: 会话ID

    Returns:
        删除的记录数量
    """
    statement = delete(SessionDetail).where(SessionDetail.session_id == session_id)
    result = session.exec(statement)
    session.commit()
    return result.rowcount

def get_latest_session_detail(session: Session, session_id: str) -> Optional[SessionDetail]:
    """
    获取会话的最新详情

    Args:
        session: 数据库会话
        session_id: 会话ID

    Returns:
        最新的会话详情模型实例，如果不存在则返回None
    """
    statement = select(SessionDetail).where(SessionDetail.session_id == session_id).order_by(SessionDetail.create_time.desc()).limit(1)
    result = session.exec(statement).first()
    return result

def count_session_details(session: Session, session_id: str) -> int:
    """
    统计会话的详情数量

    Args:
        session: 数据库会话
        session_id: 会话ID

    Returns:
        会话详情的数量
    """
    statement = select(SessionDetail).where(SessionDetail.session_id == session_id)
    results = session.exec(statement).all()
    return len(results)
