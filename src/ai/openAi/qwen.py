import asyncio
import json
import logging
from openai import OpenAI, AsyncOpenAI
from typing import List, Dict, Any, Optional, Union, Literal
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv
import os
from src.ai.pojo.openAiBo import QwenOpenAiParm
from src.utils.dataUtils import nvl

logger = logging.getLogger(__name__)
load_dotenv()

qwen_openai_client = None

async def get_qwen_completion(
    params: QwenOpenAiParm,
    **kwargs
) -> Any:
    """
    调用通义千问API获取聊天完成结果

    Args:
        :param params:
    Returns:
        OpenAI API的响应对象

    """
    global qwen_openai_client
    if qwen_openai_client is None:
        qwen_openai_client = AsyncOpenAI(api_key=nvl(params.api_key,os.getenv("DASHSCOPE_API_KEY")),
                                         base_url=nvl(params.base_url,os.getenv("QWEN_BASE_URL")))

    if not params.model:
        params.model = os.getenv("DEFAULT_QWEN_MODEL")

    logger.info(f"通义千问 API 提示词信息:\n {params.messages}")

    # 准备额外参数
    extra_body = {}
    if params.enable_search:
        extra_body["enable_search"] = True

    # 调用 API 获取完成结果
    response = await qwen_openai_client.chat.completions.create(
        model=params.model,
        messages=params.messages,
        stream=params.stream,
        temperature=params.temperature,
        extra_body=extra_body,
    )

    return response


def handle_qwen_response_block(response: ChatCompletion) -> str:
    """
    阻塞模式下从通义千问返回结果中解析答案

    Args:
        response: 通义千问原始返回结果
    Returns:
        解析后的答案文本
    """
    result = response.choices[0].message.content
    logger.info(f"通义千问 API 最终返回结果:\n {result}")
    return result


# 示例用法
if __name__ == "__main__":
    example_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "中国队在巴黎奥运会获得了多少枚金牌"},
    ]

    async def main():
        params = QwenOpenAiParm(messages=example_messages, stream=False, enable_search=True)
        # 非流式示例
        print("非流式响应示例:")
        response = await get_qwen_completion(params=params)
        print(handle_qwen_response_block(response))

        # 流式示例
        # print("\n流式响应示例:")
        # params = QwenOpenQiParm(messages=example_messages, stream=True, enable_search=True)
        # stream_response = await get_qwen_completion(params=params)
        # async for chunk in stream_response:
        #     if chunk.choices[0].delta.content:
        #         print(chunk.choices[0].delta.content, end="", flush=True)
        print()  # 添加换行

    asyncio.run(main())
