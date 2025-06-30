import datetime
import logging
import json
import requests
from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.dao.apiInfoDao import get_info_by_api_code
from src.dao.sessionDao import update_session
from src.dao.sessionDetailDao import create_session_detail
from src.db.db import get_db
from src.myHttp.bo.httpResponse import HttpResponse
from src.myHttp.utils.myHttpUtils import normal_post
from src.pojo.po.sessionDetailPo import SessionDetail
from src.pojo.vo.jixiaomeiVo import DifyJxm
from src.service.difyService import dify_result_handler, NO_DATA_RESPONSE
from src.service.sessionService import create_session_default, get_user_last_session

router = APIRouter(prefix="/dify", tags=["DIFY 相关"])


# 请求头
headers = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer YOUR_ACCESS_TOKEN"  # 如果需要认证，取消注释并替换 Token
}
JXM_API_CODE = "jixiaomei" # pmspte 更换成这个


logger = logging.getLogger(__name__)


@router.post("/chatflow-jxm")
async def execute_sql_query(param: DifyJxm, db: Session = Depends(get_db)):
    api_code = JXM_API_CODE
    api_info =get_info_by_api_code(session=db, api_code=api_code)
    api_url = api_info.api_url
    api_header = api_info.api_header
    jxm_param = param.to_jxm()
    # 处理会话和对话信息
    ai_session = get_user_last_session(session=db, user_id=param.user_id, token=param.token)
    ai_session_detail = SessionDetail.from_dify_jxm(param)
    ai_session_detail.session_id = ai_session.id
    ai_session_detail.api_input = jxm_param
    # 默认给dify续上多轮对话
    jxm_param["conversation_id"] = ai_session.dify_conversation_id

    try:
        response =await  normal_post(api_url, jxm_param, json.loads(api_header))
        result = await dify_result_handler(response)
    except  Exception as e:
        ai_session_detail.when_error("问答流程异常，没有返回数据")
        create_session_detail(session=db, session_detail=ai_session_detail)
        logger.error(e)
        return HttpResponse.success([NO_DATA_RESPONSE])

    # todo 这里可能存在缺陷，不清楚Dify对话数量达到极限时 是否会自动更换会话ID
    if ai_session.dify_conversation_id is None:
        # 获取到Dify的会话ID并持久化到本系统的会话表中
        ai_session.dify_conversation_id = response.get("conversation_id")
        update_session(session=db,session_id = ai_session.id, update_data=ai_session.dict())

    ai_session_detail.when_success(result)
    create_session_detail(session=db, session_detail=ai_session_detail)

    return HttpResponse.success([result])




