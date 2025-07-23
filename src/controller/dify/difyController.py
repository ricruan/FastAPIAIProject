import logging
import json
import random
from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.common.enum.codeEnum import CodeEnum
from src.dao.apiInfoDao import get_info_by_api_code
from src.dao.sessionDao import update_session
from src.dao.sessionDetailDao import create_session_detail
from src.dao.userProfileDao import get_profile_by_user_id
from src.db.db import get_db, engine
from src.exception.aiException import AIException
from src.myHttp.bo.httpResponse import HttpResponse
from src.myHttp.utils.myHttpUtils import normal_post, dify_stream_post
from src.pojo.po.sessionDetailPo import SessionDetail, DialogCarrierEnum
from src.pojo.vo.difyResponse import DifyResponse
from src.pojo.vo.difyParamVo import DifyJxm, DifyYpj
from src.service.difyService import dify_result_handler, NO_DATA_RESPONSE, normal_dify_flow
from src.service.sessionService import get_user_last_session
from fastapi.responses import StreamingResponse
import asyncio

from src.service.userProfileService import check_new_user
from src.utils.dataUtils import is_valid_json
from src.utils.dateUtils import get_now_4_prompt

router = APIRouter(prefix="/dify", tags=["DIFY 相关"])



logger = logging.getLogger(__name__)


@router.post("/chatflow-jxm")
async def chatflow_jxm(param: DifyJxm, db: Session = Depends(get_db)):
    api_code = CodeEnum.JXM_API_CODE.value
    jxm_param = param.to_jxm()
    return await normal_dify_flow(api_code=api_code,user_id=param.user_id,dify_param=jxm_param,db=db)

@router.post("/chatflow-ypj")
async def chatflow_ypj(param: DifyYpj,  db: Session = Depends(get_db)):
    api_code = CodeEnum.YPJ_API_CODE.value
    ypj_param = param.model_dump()
    return await normal_dify_flow(api_code=api_code,user_id=param.user,dify_param=ypj_param,db=db)

@router.get("/info/{user}")
async def get_info(user: str, db: Session = Depends(get_db)):
    user_info = "未查询到"
    profile = get_profile_by_user_id(session=db, user_id=user)
    if profile:
        user_info = profile.user_info
    return f"{get_now_4_prompt()} 用户的信息: {user_info}"

async def event_stream_fake(text: str):
    """
     假流式输出,拿到完整的文本，再分段传输，但是会丢失原本的difySEE返回体数据结构\n
     每次随机返回3-4个字符
    :param text: 最终返回文本
    :return:
    """
    index = 0
    text_length = len(text)

    while index < text_length:
        chunk_size = random.randint(3, 4)
        if index + chunk_size > text_length:
            chunk_size = text_length - index
        chunk = text[index: index + chunk_size]
        index += chunk_size
        await asyncio.sleep(0.2)
        yield f"data: {chunk}\n\n"

async def do_stream_post_dify(message_queue):
    """
    流式请求Dify,接受一个回调函数，在流输出结束之后执行
    :param message_queue: 消息队列
    :return:
    """
    async def event_stream():
        while True:
            try:
                # 设置超时
                data = await asyncio.wait_for(message_queue.get(), timeout=60.0)
                logger.debug(f"SSE接收到消息: {data}")
                data = data.decode('utf-8', errors='ignore')
                if data.startswith("data: "):
                    json_str = data[6:].strip()  # 去掉前6个字符("data: ")并去除首尾空白
                else:
                    json_str = data.strip()

                if is_valid_json(json_str):
                    json_data = json.loads(json_str)
                    if "error" == json_data.get("event"):
                        yield f"event: dify error "+json_data.get("message")
                        break
                    # 丢掉普通节点的信息，只传msg
                    if "message" not in json_data.get("event"):
                        continue
                    logger.debug(f"SSE接收到message: {data}")
                    if json_data.get("event") == "message_end":
                        logger.debug("检测到结束指令，关闭SSE流")
                        # yield f"data: {json_str}\n\n"
                        break
                    yield f"data: {json_data.get("answer")}\n\n"

            except asyncio.TimeoutError:
                logger.debug("超时，关闭SSE流")
                raise AIException.quick_raise("请求超时")
            except Exception as e:
                logger.error(e)
                break
    return StreamingResponse(event_stream(), media_type="text/event-stream")




