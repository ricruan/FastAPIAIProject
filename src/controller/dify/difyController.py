import logging
import json
import random
from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.dao.apiInfoDao import get_info_by_api_code
from src.dao.sessionDao import update_session
from src.dao.sessionDetailDao import create_session_detail
from src.db.db import get_db
from src.exception.aiException import AIException
from src.myHttp.bo.httpResponse import HttpResponse
from src.myHttp.utils.myHttpUtils import normal_post, stream_post_and_enqueue
from src.pojo.po.sessionDetailPo import SessionDetail
from src.pojo.vo.jixiaomeiVo import DifyJxm
from src.service.difyService import dify_result_handler, NO_DATA_RESPONSE
from src.service.sessionService import get_user_last_session
from fastapi.responses import StreamingResponse
import asyncio
from src.utils.dataUtils import is_valid_json

router = APIRouter(prefix="/dify", tags=["DIFY 相关"])


JXM_API_CODE = "jixiaomei" # pmspte 更换成这个


logger = logging.getLogger(__name__)


@router.post("/chatflow-jxm")
async def chatflow_jxm(param: DifyJxm, db: Session = Depends(get_db)):
    api_code = JXM_API_CODE
    api_info =get_info_by_api_code(session=db, api_code=api_code)
    api_url = api_info.api_url
    api_header = api_info.api_header
    jxm_param = param.to_jxm()
    # 处理会话和对话信息
    ai_session = get_user_last_session(session=db, user_id=param.user_id, token=param.token)
    ai_session_detail = SessionDetail.from_dify_jxm(param)
    ai_session_detail.session_id = ai_session.id
    # 默认给dify续上多轮对话
    jxm_param["conversation_id"] = ai_session.dify_conversation_id
    ai_session_detail.api_input = jxm_param
    # 内部临时先用阻塞
    # jxm_param["response_mode"] = "blocking"


    dify_response = {}
    result = ""

    async def session_handle():
        """
         session 的持久化处理
        :return:
        """
        nonlocal dify_response
        nonlocal result
        if param.response_mode == "streaming":
            dify_response = await stream_post_task
            result = dify_response.get("result")
        if ai_session.dify_conversation_id is None:
            result = dify_response.get("result")
            # 获取到Dify的会话ID并持久化到本系统的会话表中
            ai_session.dify_conversation_id = dify_response.get("conversation_id")
            update_session(session=db, session_id=ai_session.id, update_data=ai_session.dict())

        ai_session_detail.when_success(dify_response, result)
        create_session_detail(session=db, session_detail=ai_session_detail)

    try:
        if param.response_mode != "streaming":
            dify_response = await normal_post(api_url, jxm_param, json.loads(api_header))
            result = await dify_result_handler(dify_response)
            await session_handle()
            if not isinstance(result, list):
                result = [result]
            return HttpResponse.success(result)

        # 消息队列
        message_queue = asyncio.Queue()
        stream_post_task = asyncio.create_task(
            stream_post_and_enqueue(message_queue, api_url, jxm_param, json.loads(api_header)))
        return await do_stream_post_dify(message_queue,session_handle)
    except  Exception as e:
        ai_session_detail.when_error("问答流程异常，没有返回数据")
        create_session_detail(session=db, session_detail=ai_session_detail)
        logger.error(e)
        return HttpResponse.success([NO_DATA_RESPONSE])



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

async def do_stream_post_dify(message_queue, finally_handle):
    """
    流式请求Dify,接受一个回调函数，在流输出结束之后执行
    :param message_queue: 消息队列
    :param finally_handle: 回调函数
    :return:
    """
    async def event_stream():
        while True:
            try:
                # 设置超时
                data = await asyncio.wait_for(message_queue.get(), timeout=60.0)
                logger.debug(f"SSE接收到消息: {data}")
                if data.startswith("data: "):
                    json_str = data[6:].strip()  # 去掉前6个字符("data: ")并去除首尾空白
                else:
                    json_str = data.strip()

                if is_valid_json(json_str):
                    json_data = json.loads(json_str)
                    if json_data.get("event") == "message_end":
                        logger.debug("检测到结束指令，关闭SSE流")
                        yield f"data: {json_str}\n\n"
                        break
                # 终止流
                yield f"data: {json_str}\n\n"

            except asyncio.TimeoutError:
                logger.debug("超时，关闭SSE流")
                raise AIException.quick_raise("请求超时")
            except Exception as e:
                logger.error(e)
                break
            finally:
                await finally_handle()
    return StreamingResponse(event_stream(), media_type="text/event-stream")




