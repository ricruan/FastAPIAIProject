# FILEPATH: C:/Ric/RicProjects/FastAPIProject/src/ai/openAi/doubao.py

import asyncio
import logging
from openai import AsyncOpenAI
from typing import List, Dict, Any
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
load_dotenv()

async def get_doubao_completion(
    messages: List[Dict[str, str]],
    stream: bool = False,
    model: str = os.getenv("DOUBAO_MODEL", "doubao-1-5-thinking-pro-250415"),
    api_key: str = os.getenv("DOUBAO_API_KEY", ""),
    base_url: str = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
    temperature: float = float(os.getenv("DOUBAO_TEMPERATURE", 1.0)),
    **kwargs
) -> Any:
    """
    调用豆包API获取聊天完成结果

    Args:
        messages: 消息列表，每个消息是一个包含'role'和'content'的字典
        stream: 是否使用流式响应，默认为False
        model: 使用的模型名称，默认为"doubao-1-5-thinking-pro-250415"
        api_key: 豆包API密钥
        base_url: 豆包API基础URL
        temperature: 温度参数，默认为1.0
    Returns:
        OpenAI API的响应对象
    """
    # 创建 OpenAI 客户端
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    logger.info(f"豆包 API 提示词信息:\n {messages}")

    # 调用 API 获取完成结果
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream,
        temperature=temperature,
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


async def online_search_doubao(messages: List[Dict[str, str]],
    stream: bool = False,
    model: str = os.getenv("ONLINE_MODEL"),
    api_key: str = os.getenv("DOUBAO_API_KEY", ""),
    base_url: str = os.getenv("ONLINE_DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3/bots"),
    temperature: float = float(os.getenv("DOUBAO_TEMPERATURE", 1.0)),
    **kwargs):
    """
    联网搜索版本
    :param messages: 照旧
    :param stream: 照旧
    :param model: 需要修改
    :param api_key: 照旧
    :param base_url: 需要修改
    :param temperature: 照旧
    :param kwargs: 照旧
    :return:
    """
    return await get_doubao_completion(messages=messages,stream=stream, model=model, api_key=api_key, base_url=base_url, temperature=temperature)

# 示例用法
if __name__ == "__main__":
    example_messages = [
        {"role": "system", "content": "你是人工智能助手"},
        {"role": "user", "content": "LOL2025年MSI冠军是谁"},
    ]

    async def main():
        # # 非流式示例
        # print("非流式响应示例:")
        # response = await get_doubao_completion(example_messages, stream=False)
        # print(handle_doubao_response_block(response))

        # 流式示例
        print("\n流式响应示例:")
        stream_response = await online_search_doubao(example_messages, stream=True)
        async for chunk in stream_response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()  # 添加换行

    asyncio.run(main())