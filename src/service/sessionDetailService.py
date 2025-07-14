from src.dao.sessionDetailDao import search_session_details
from sqlmodel import Session

def get_history_query_by_user_id(session: Session,user_id:str):
    """
    根据用户ID获取用户历史问题
    :param session:
    :param user_id: 用户ID
    :return:
    """
    histories = search_session_details(session=session,search_params={'user_id':user_id,'status':'200'},limit=200)
    if histories is None:
        histories = search_session_details(session=session,search_params={'status':'200'}, limit=200)
    return [history.user_question for history in histories]

