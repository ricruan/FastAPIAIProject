import json
import logging
from requests import Session
import asyncio
from starlette.responses import StreamingResponse
from src.dao.apiInfoDao import get_info_by_api_code
from src.dao.sessionDetailDao import create_session_detail
from src.myHttp.bo.httpResponse import HttpResponse
from src.myHttp.utils.myHttpUtils import normal_post, dify_stream_post
from src.pojo.po.sessionDetailPo import SessionDetail, DialogCarrierEnum
from src.pojo.vo.difyResponse import DifyResponse
from src.service.sessionService import get_user_last_session, session_handle
from src.service.userProfileService import check_new_user
from src.utils.dataUtils import is_valid_json, jstr_to_dict
from datetime import datetime

logger = logging.getLogger(__name__)
# 无数据时回复
NO_DATA_RESPONSE = DifyResponse.not_found_data()


async def normal_dify_flow(api_code: str,user_id: str,dify_param: dict,db: Session):
    """
     通用处理Dify对话流\n
     前置工作：\n
     - 去API表维护Dify对话流的API信息以及Header信息

     函数内容：\n
     - 持久化会话和对话
     - 兼容阻塞模式和非阻塞模式
    :param api_code:
    :param user_id:
    :param dify_param:
    :param db:
    :return:
    """
    api_info = get_info_by_api_code(session=db, api_code=api_code)
    api_url = api_info.api_url
    api_header = api_info.api_header

    # 处理会话和对话信息
    ai_session = get_user_last_session(session=db, user_id=user_id)
    ai_session_detail = SessionDetail(user_id=user_id, session_id=ai_session.id)
    ai_session_detail.api_input = dify_param
    ai_session_detail.user_question = dify_param['query']
    ai_session_detail.response_mode = dify_param['response_mode']
    # if Dify calling,Session's dialog_carrier is  API表对应api的code
    ai_session_detail.dialog_carrier = api_info.api_code
    ai_session_detail.create_time = datetime.now()
    dify_param['conversation_id'] = ai_session.dify_conversation_id
    # user_info = ""
    # profile = get_profile_by_user_id(session=db, user_id=user_id)
    # if profile:
    #     user_info = profile.user_info
    # # 给一下当前日期
    # dify_param['query'] = f"{dify_param['query']} (额外可参考信息:{get_now_4_prompt()},我的个人信息:{user_info})"

    try:
        if dify_param['response_mode'] != "streaming":
            dify_response = await normal_post(api_url, dify_param, json.loads(api_header))
            result = dify_result_handler(dify_response).model_dump()
            asyncio.create_task(session_handle(ai_session,ai_session_detail,dify_response,result))
            if not isinstance(result,list):
                result = [result]
            return HttpResponse.success(result)

        # todo: 之后可以把用户缓存到内存中 读取判断， 减少一次DB访问
        check_new_user(user_id=user_id, session=db, user_source=DialogCarrierEnum.DIFY_ERP.value)
        return StreamingResponse(
        dify_stream_post(url=api_url, data=dify_param, headers=json.loads(api_header),ai_session=ai_session, ai_session_detail=ai_session_detail),
        media_type="text/event-stream"
    )
    except  Exception as e:
        ai_session_detail.when_error("问答流程异常或没有返回数据" + str(e))
        create_session_detail(session=db, session_detail=ai_session_detail)
        logger.error(e)
        return HttpResponse.success([NO_DATA_RESPONSE])



def dify_result_handler(result) -> DifyResponse|list:
    """
    处理Dify服务返回结果
    :param result: 输入结果，可能是dict或list
    :return: 提取的sql_data或原始列表，不满足条件返回空列表
    """
    logger.info(f"\nDify最终需要处理的返回结果:\n {result}")

    json_data = result
    if json_data["answer"] is not None:
        answer = json_data["answer"]
        return answer_handler(answer)
    else:
        return NO_DATA_RESPONSE

def answer_handler(answer) -> DifyResponse|list:
    """
    处理返回结果的回复内容
    :param answer:
    :return:
    """
    logger.info(f"\nanswer最终需要处理的返回结果:\n {answer}")
    if is_valid_json(answer):
        answer = jstr_to_dict(answer)
    if isinstance(answer, dict):
        if "data" in answer:
            return DifyResponse.to_data(answer.get("data"))
        else:
            return NO_DATA_RESPONSE
    elif isinstance(answer, list):
        return answer
    elif isinstance(answer, str):
        result = answer.replace('"',"“").replace("'","“")
        return DifyResponse.to_text(result)
    return NO_DATA_RESPONSE

