import os
from datetime import datetime

from sqlmodel import Session
from typing import Optional, Dict, Any, List

from src.dao.sessionDao import create_session, get_recent_sessions, get_session_by_id, update_session
from src.dao.sessionDetailDao import get_session_details_by_session_id, create_session_detail, count_session_details
from src.db.db import engine
from src.exception.aiException import AIException
from src.pojo.po.sessionDetailPo import SessionDetail, DialogCarrierEnum
from src.pojo.po.sessionPo import SessionPo as SessionModel, SessionInfo, SessionPo
from src.pojo.vo.difyResponse import DifyResponse


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
    获取用户最近一次的会话，如果没有或者最近一次会话轮数大于50 创建一个新会话
    :param session: db
    :param user_id: 用户ID
    :param token: token
    :return: 回显
    """
    session_list = get_recent_sessions(session,user_id)
    if session_list:
        ai_session = session_list[0]
        cnt = count_session_details(session=session, session_id=ai_session.id)
        if cnt < int(os.getenv("SESSION_MAX_NUM",50)):
            return ai_session

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



def dify_stream_handle(conversation_id: str,
                       result,
                       ai_session: SessionPo = None,
                       ai_session_detail: SessionDetail = None,
                       ):
    """
    处理Dify的流式数据
    :param conversation_id: 会话ID
    :param result: 返回结果
    :param ai_session:  会话记录
    :param ai_session_detail: 会话详情记录
    :return:
    """
    with Session(engine) as session:
        if ai_session:
            if not ai_session.dify_conversation_id:
                update_session(session,session_id=ai_session.id,update_data={'conversation_id':conversation_id})
        if ai_session_detail:
            if isinstance(result, DifyResponse) and 'dify error' in str(result.data):
                ai_session_detail.when_error(result)
            else:
                ai_session_detail.when_success(result, result)
            create_session_detail(session=session, session_detail=ai_session_detail)

async def session_handle(ai_session,ai_session_detail,dify_response: dict,result):
    """
     session 的持久化处理 阻塞模式 4 dify
    :return:
    """
    with Session(engine) as db:
        if ai_session.dify_conversation_id is None:
            # 获取到Dify的会话ID并持久化到本系统的会话表中
            ai_session.dify_conversation_id = dify_response.get("conversation_id")
            update_session(session=db, session_id=ai_session.id, update_data=ai_session.dict())
        if isinstance(result,DifyResponse) and 'dify error' in str(result.data):
            ai_session_detail.when_error(result)
        else :
            ai_session_detail.when_success(dify_response, result)
        # 对话载体类型为 DIFY_ERP
        ai_session_detail.dialog_carrier = DialogCarrierEnum.DIFY_ERP.value
        create_session_detail(session=db, session_detail=ai_session_detail)
        db.commit()


