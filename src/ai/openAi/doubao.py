# FILEPATH: C:/Ric/RicProjects/FastAPIProject/src/ai/openAi/doubao.py
import asyncio
import logging
from openai import AsyncOpenAI
from typing import List, Dict, Any
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv
import os
from src.ai.pojo.openAiBo import OpenAiParam
from src.utils.dataUtils import nvl

logger = logging.getLogger(__name__)
load_dotenv()

doubao_openai_client = None
doubao_online_openai_client = None

async def get_doubao_completion(
    params: OpenAiParam,
    **kwargs
) -> Any:
    """
    调用豆包API获取聊天完成结果

    Args:
        :param params:
    Returns:
        OpenAI API的响应对象
    """
    global doubao_openai_client
    if doubao_openai_client is None:
        doubao_openai_client = AsyncOpenAI(api_key=nvl(params.api_key,os.getenv("DOUBAO_API_KEY")),
                                         base_url=nvl(params.base_url,os.getenv("DOUBAO_BASE_URL")))

    if not params.model:
        params.model = os.getenv("DEFAULT_DOUBAO_MODEL")
    if not params.temperature:
        params.temperature = os.getenv("DOUBAO_TEMPERATURE",1.0)
    logger.info(f"豆包 API 提示词信息:\n {params.messages}")

    # 调用 API 获取完成结果
    response = await doubao_openai_client.chat.completions.create(
        model=params.model,
        messages=params.messages,
        stream=params.stream,
        temperature=float(params.temperature),
    )

    return response

def handle_doubao_response_block(response: ChatCompletion) -> str:
    """
    阻塞模式下从豆包返回结果中解析答案

    Args:
        response: 豆包原始返回结果
    Returns:
        解析后的答案文本
    """
    result = response.choices[0].message.content
    logger.info(f"豆包 API 最终返回结果:\n {result}")
    return result


async def online_search_doubao(
    params: OpenAiParam,
    **kwargs):
    """
    联网搜索版本
    :param params:
    :param kwargs: 照旧
    :return:
    """
    global doubao_online_openai_client
    if doubao_online_openai_client is None:
        doubao_online_openai_client = AsyncOpenAI(api_key=nvl(params.api_key, os.getenv("DOUBAO_API_KEY")),
                                           base_url=nvl(params.base_url, os.getenv("ONLINE_DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3/bots")))
    logger.info(f"豆包 API 提示词信息:\n {params.messages}")

    if not params.model:
        params.model = os.getenv("ONLINE_MODEL")
    if not params.temperature:
        params.temperature = os.getenv("DOUBAO_TEMPERATURE",1.0)

    # 调用 API 获取完成结果
    response = await doubao_online_openai_client.chat.completions.create(
        model=params.model,
        messages=params.messages,
        stream=params.stream,
        temperature=float(params.temperature),
    )

    return response

# 示例用法
if __name__ == "__main__":
    example_messages = [
        {"role": "system", "content": "你是人工智能助手"},
        {"role": "user", "content": "中国准备新修的水电站在哪里"},
    ]

    example_messages2 = [
        {"role": "system", "content": "你是人工智能助手"},
        {"role": "user", "content": "三国演义的作者是谁"},
    ]

    async def main():
        # # 非流式示例
        print("非流式响应示例:")
        # params = OpenAiParam(messages=example_messages, stream=False)
        # response = await online_search_doubao(params=params)
        # print(handle_doubao_response_block(response))

        # 流式示例
        # print("\n流式响应示例:")
        params = OpenAiParam(messages=example_messages2, stream=True)
        stream_response = await get_doubao_completion(params)
        async for chunk in stream_response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()  # 添加换行

    asyncio.run(main())