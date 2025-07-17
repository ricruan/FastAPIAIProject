from itertools import takewhile

from src.dao.sessionDetailDao import search_session_details, search_session_details_by_user_id
from sqlmodel import Session

def get_history_query_by_user_id(session: Session,user_id:str):
    """
    根据用户ID获取用户历史问题
    :param session:
    :param user_id: 用户ID
    :return:
    """
    histories = search_session_details_by_user_id(session=session,search_params={'status':'200'},user_id=user_id,limit=200)
    if not histories or len(histories) < 10:
        histories = search_session_details(session=session,search_params={'status':'200'}, limit=200)
    return [history.user_question for history in histories]


def get_history_qa_by_user_id(session: Session,user_id:str,last_handle_session_id:str = None):
    """
    获取用户历史问答对(final_response未处理版本)
    :param last_handle_session_id: 上次处理到哪条会话了，只保留这条时间之后的
    :param session:
    :param user_id:
    :return:
    """
    histories = search_session_details_by_user_id(session=session,search_params={'status':'200'},user_id=user_id,limit=50)
    if last_handle_session_id is not None :
        # 取 last_handle_session_id 之前的会话
        histories = list(takewhile(lambda x: x.id != last_handle_session_id, histories))
    return [{'user_question':history.user_question,'answer':history.final_response[:100] + "...",'id':history.id} for history in histories]


def histories_2_simple_qa(histories:list):
    return [{'user_question': history['user_question'], 'answer': history['answer']} for history in histories]
