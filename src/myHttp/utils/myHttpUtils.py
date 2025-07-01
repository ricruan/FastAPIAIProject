import json
import logging
from asyncio import Event

import aiohttp
from src.exception.aiError import AIError
from src.utils.difyUtils import dify_stream_response_handler, dify_get_conversation_id_from_stream

# 请求头
HEADERS = {
    "Content-Type": "application/json",
}

STREAM_HEADERS = {
    "Content-Type": "text/event-stream",
}

## todo 放到环境变量里面去
TIMEOUT = 360

logger = logging.getLogger(__name__)


async def normal_post(url: str, data: dict, headers: dict)  -> dict:
    """
     常规Post请求封装(异步),可以便与后期统一拦截
    :param url: API URL
    :param data: API 请求参数
    :param headers: API 请求头
    :return:
    """
    headers = {**HEADERS, **headers}
    para_json = {**data}
    logger.info(f"\n请求地址:{url}\n请求参数:{para_json}\n请求头:{headers}")

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=para_json, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as response:
            result_text = await response.text()
            result_text = json.loads(result_text)
            logger.info(f"\n请求地址:{url}\n响应结果:{result_text}")

            return result_text

async def stream_post_and_enqueue(message_queue, api_url: str, api_param: dict, api_header: dict) -> dict:
    """
    发送流式 POST 请求，并将接收到的数据写入 message_queue
    :param message_queue:  消息队列
    :param api_url:  api路径
    :param api_param:  请求参数
    :param api_header:  请求头
    :return:
    """
    async with aiohttp.ClientSession() as session:
        headers = {**HEADERS, **api_header}
        result = ""
        conversation_id = None
        # 发送流式 POST 请求
        async with session.post(
            api_url,
            json=api_param,
            headers=headers
        ) as response:
            # 检查响应状态码
            if response.status != 200:
                raise AIError.quick_raise("流式请求Dify接口的返回码异常" + str(response))

            # 逐行读取流式响应数据
            async for line in response.content:
                # 解码字节数据为字符串
                chunk = line.decode('utf-8').strip()
                logger.debug(f"流式请求Dify接口的响应数据:{chunk}")
                result = result + dify_stream_response_handler(chunk)
                if conversation_id is None:
                    conversation_id = dify_get_conversation_id_from_stream(chunk)
                if chunk:  # 忽略空行
                    # 将数据放入队列
                    await message_queue.put(chunk)

            return {"result": result,
            "conversation_id": conversation_id}