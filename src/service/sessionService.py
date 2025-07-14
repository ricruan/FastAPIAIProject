from datetime import datetime

from sqlmodel import Session
from typing import Optional, Dict, Any, List

from src.dao.sessionDao import create_session, get_recent_sessions, get_session_by_id, update_session
from src.dao.sessionDetailDao import get_session_details_by_session_id
from src.exception.aiException import AIException
from src.pojo.po.sessionPo import SessionPo as SessionModel, SessionInfo


def create_session_default(session: Session,user_id: str = None , token: str = None):
    """
    默认的方式创建session
    :param session: db
    :param user_id: 用户ID
    :param token: token
    :return: 回显
    """
    session_model = SessionModel.get_default()
    session_model.user_id = user_id
    session_model.token = token
    call_back = create_session(session,session_model)
    return call_back


def get_user_last_session(session: Session,user_id: str = None , token: str = None):
    """
    获取用户最近一次的会话，如果没有的话创建一个新会话
    :param session: db
    :param user_id: 用户ID
    :param token: token
    :return: 回显
    """
    session_list = get_recent_sessions(session,user_id)
    if session_list:
        return session_list[0]
    else:
        return create_session_default(session,user_id,token)



def when_search_session(session: Session,session_id: str) -> Optional[SessionInfo]:
    """
    当查询session时，顺便 把历史对话查出来，顺便再更新查询的session为当前使用的session
    :param session: db
    :param session_id: 会话ID
    :return:
    """
    session_model = get_session_by_id(session,session_id)
    if not session_model:
        raise AIException.quick_raise(f"未查询到指定会话ID {session_id} 的对应数据")
    history_list = get_session_details_by_session_id(session,session_model.id)
    session_info = session_model.to_session_info(list(history_list))
    session_model.update_time = datetime.now()
    update_session(session,session_model.id,session_model.model_dump())
    return session_info



