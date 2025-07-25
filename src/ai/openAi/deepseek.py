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

deepseek_openai_client = None

async def get_deepseek_completion(
    params: OpenAiParam,
    **kwargs
) -> Any:
    """
    调用 Deepseek API 获取聊天完成结果
    
    Args:
        params: 参数
    Returns:
        OpenAI API 的响应对象
    """
    global deepseek_openai_client
    if deepseek_openai_client is None:
        deepseek_openai_client = AsyncOpenAI(api_key=nvl(params.api_key,os.getenv("DEEPSEEK_API_KEY")),
                                         base_url=nvl(params.base_url,os.getenv("DEEPSEEK_BASE_URL")))

    if not params.model:
        params.model = os.getenv("DEEPSEEK_MODEL")
    if not params.temperature:
        params.temperature = os.getenv("DEEPSEEK_TEMPERATURE",1.0)


    logger.info(f"Deepseek API 提示词信息:\n {params.messages}")
    # 调用 API 获取完成结果
    response = await deepseek_openai_client.chat.completions.create(
        model=params.model,
        messages=params.messages,
        stream=params.stream,
        temperature=params.temperature,
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


if __name__ == "__main__":
    example_messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "讲一个短故事"},
    ]


    async def main():
        response = await get_deepseek_completion(OpenAiParam(messages=example_messages,stream=True))
        # print(handle_ds_response_block(response))
        async for chunk in response:
            print(chunk.choices[0].delta.content, end="", flush=True)


    asyncio.run(main())