import json
import logging
import aiohttp
import asyncio

# 请求头
HEADERS = {
    "Content-Type": "application/json",
}

## todo 放到环境变量里面去
TIMEOUT = 360

logger = logging.getLogger(__name__)


async def normal_post(url: str, data: dict, headers: dict):
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