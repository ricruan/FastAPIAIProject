import asyncio
import json
import logging
from asyncio import Event

import aiohttp
from src.exception.aiException import AIException
from src.utils.difyUtils import dify_stream_response_handler, dify_get_conversation_id_from_stream, \
    get_value_from_stream_response_by_key

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
        async with session.post(
                url,
                json=para_json,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=TIMEOUT)
        ) as response:
            result_text = await response.text()
            result_text = json.loads(result_text)
            logger.info(f"\n请求地址:{url}\n响应结果:{result_text}")

            return result_text

async def post_with_query_params(url: str, params: dict, headers: dict) -> dict:
    """
    常规POST请求封装(异步)，参数通过URL Query String传递，便于后期统一拦截
    :param url: API URL
    :param params: API 请求参数(会拼接在URL上)
    :param headers: API 请求头
    :return: 响应JSON数据
    """
    headers = {**HEADERS, **headers}
    logger.info(f"\n请求地址:{url}\n请求参数:{params}\n请求头:{headers}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=TIMEOUT)
            ) as response:
                result_text = await response.text()
                result_text = json.loads(result_text)
                logger.info(f"\n请求地址:{url}\n响应结果:{result_text}")
                return result_text
    except asyncio.TimeoutError:
        logger.error(f"请求超时: {url}")
        raise Exception("API请求超时")
    except Exception as e:
        logger.error(f"请求异常: {url}\n错误: {str(e)}")
        raise

async def form_data_post(url: str, form_data: dict, headers: dict) -> dict:
    """
    Form-Data格式POST请求封装(异步)，参数通过form-data传递，便于后期统一拦截
    :param url: API URL
    :param form_data: API 请求参数(以form-data形式提交)
    :param headers: API 请求头
    :return: 响应JSON数据
    """
    # 不使用默认的Content-Type，因为form-data请求会自动设置正确的Content-Type和boundary
    headers_without_content_type = {k: v for k, v in headers.items() if k.lower() != 'content-type'}
    headers_without_content_type = {**{k: v for k, v in HEADERS.items() if k.lower() != 'content-type'}, **headers_without_content_type}
    
    logger.info(f"\n请求地址:{url}\n请求参数(form-data):{form_data}\n请求头:{headers_without_content_type}")

    try:
        async with aiohttp.ClientSession() as session:
            # 创建FormData对象
            data = aiohttp.FormData()
            for key, value in form_data.items():
                # 如果值是文件对象，需要特殊处理
                if hasattr(value, 'read'):
                    # 对于文件对象，可以指定文件名和内容类型
                    filename = getattr(value, 'name', 'file')
                    content_type = None  # 让aiohttp自动检测
                    data.add_field(key, value, filename=filename, content_type=content_type)
                else:
                    # 对于普通值，直接添加
                    data.add_field(key, str(value))
            
            async with session.post(
                url,
                data=data,
                headers=headers_without_content_type,
                timeout=aiohttp.ClientTimeout(total=TIMEOUT)
            ) as response:
                result_text = await response.text()
                try:
                    result_json = json.loads(result_text)
                    logger.info(f"\n请求地址:{url}\n响应结果:{result_json}")
                    return result_json
                except json.JSONDecodeError:
                    # 如果响应不是JSON格式，返回原始文本
                    logger.info(f"\n请求地址:{url}\n响应结果(非JSON):{result_text}")
                    return {"raw_response": result_text}
    except asyncio.TimeoutError:
        logger.error(f"请求超时: {url}")
        raise Exception("API请求超时")
    except Exception as e:
        logger.error(f"请求异常: {url}\n错误: {str(e)}")
        raise

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
                raise AIException.quick_raise("流式请求Dify接口的返回码异常" + str(response))

            # 逐行读取流式响应数据
            async for line in response.content:
                # 解码字节数据为字符串
                chunk = line.decode('utf-8').strip()
                logger.debug(f"流式请求Dify接口的响应数据:{chunk}")
                if get_value_from_stream_response_by_key(chunk,'event') == 'error':
                    result = 'dify error,'+ get_value_from_stream_response_by_key(chunk,'message') + ","
                result = result + dify_stream_response_handler(chunk)
                if conversation_id is None:
                    conversation_id = dify_get_conversation_id_from_stream(chunk)
                if chunk:  # 忽略空行
                    # 将数据放入队列
                    await message_queue.put(chunk)

            return {"result": result,
            "conversation_id": conversation_id}