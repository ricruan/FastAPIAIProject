import asyncio
import logging

from openai import OpenAI, AsyncOpenAI
from typing import List, Dict, Any
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
load_dotenv()


async def get_deepseek_completion(
    messages: List[Dict[str, str]], 
    stream: bool = False,
    model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    api_key: str = os.getenv("DEEPSEEK_API_KEY", ""),
    base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    temperature: float = float(os.getenv("DEEPSEEK_TEMPERATURE", 1.0)),
) -> Any:
    """
    调用 Deepseek API 获取聊天完成结果
    
    Args:
        messages: 消息列表，每个消息是一个包含 'role' 和 'content' 的字典
        stream: 是否使用流式响应，默认为 False
        model: 使用的模型名称，默认为 "deepseek-chat"
        api_key: Deepseek API 密钥
        base_url: Deepseek API 基础 URL
        temperature: 温度参数，默认为 1.0
    Returns:
        OpenAI API 的响应对象
    """
    # 创建 OpenAI 客户端
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    logger.info(f"Deepseek API 提示词信息:\n {messages}")
    # 调用 API 获取完成结果
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream,
        temperature=temperature,
    )
    
    return response

def handle_ds_response_block(response: ChatCompletion) -> str:
    """
    阻塞模式下从ds返回结果中解析答案
    :param response: ds原始返回结果
    :return: 答案
    """
    result = response.choices[0].message.content
    logger.info(f"LLM 最终返回结果:\n {result}")
    return result

# 示例用法
if __name__ == "__main__":
    example_messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "讲一个短故事"},
    ]


    async def main():
        response = await get_deepseek_completion(example_messages, stream=False)
        print(handle_ds_response_block(response))
        # async for chunk in response:
        #     print(chunk.choices[0].delta.content, end="", flush=True)


    asyncio.run(main())