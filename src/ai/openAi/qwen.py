import asyncio
import json
import logging
from openai import OpenAI, AsyncOpenAI
from typing import List, Dict, Any, Optional, Union, Literal
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
load_dotenv()

qwen_openai_client = None

async def get_qwen_completion(
    messages: List[Dict[str, str]],
    stream: bool = False,
    model: str = os.getenv("QWEN_MODEL", "qwen-plus"),
    api_key: str = os.getenv("DASHSCOPE_API_KEY", ""),
    base_url: str = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
    temperature: float = float(os.getenv("QWEN_TEMPERATURE", 1.0)),
    enable_search: bool = False,
    **kwargs
) -> Any:
    """
    调用通义千问API获取聊天完成结果

    Args:
        messages: 消息列表，每个消息是一个包含'role'和'content'的字典
        stream: 是否使用流式响应，默认为False
        model: 使用的模型名称，默认为"qwen-plus"
        api_key: 通义千问API密钥
        base_url: 通义千问API基础URL
        temperature: 温度参数，默认为1.0
        enable_search: 是否启用搜索功能，默认为False
    Returns:
        OpenAI API的响应对象
    """
    global qwen_openai_client
    if qwen_openai_client is None:
        qwen_openai_client = AsyncOpenAI(api_key=api_key, base_url=base_url)


    logger.info(f"通义千问 API 提示词信息:\n {messages}")

    # 准备额外参数
    extra_body = {}
    if enable_search:
        extra_body["enable_search"] = True

    # 调用 API 获取完成结果
    response = await qwen_openai_client.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream,
        temperature=temperature,
        extra_body=extra_body if extra_body else None,
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
        # 非流式示例
        # print("非流式响应示例:")
        # response = await get_qwen_completion(example_messages, stream=False, enable_search=True)
        # print(handle_qwen_response_block(response))

        # 流式示例
        print("\n流式响应示例:")
        stream_response = await get_qwen_completion(example_messages, stream=True, enable_search=True)
        async for chunk in stream_response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()  # 添加换行

    asyncio.run(main())
