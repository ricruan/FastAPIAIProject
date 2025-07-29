import json
import logging
import os
from http import HTTPStatus
from dashscope import Application
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
logger = logging.getLogger(__name__)

API_KEY = os.getenv("DASHSCOPE_API_KEY")

class DashScopeAPIParam(BaseModel):
    app_id: str = Field(None, description="APP ID")
    stream: bool = Field(None, description="流式响应")
    messages: list = Field(None, description="消息")
    prompt: str = Field(None, description="用户提示词,同时使用时追加一条到消息后面", example="你好")
    api_key: str = Field(API_KEY, description="API KEY")
    incremental_output: bool = Field(None, description="是否追加模式")

def get_dashscope_completion(
        params: DashScopeAPIParam,
        **kwargs
):
    """
    调用百炼里面创建的智能体
    :param params:
    :param kwargs:
    :return:
    """
    responses = Application.call(**params.model_dump())  # 增量输出
    return responses


def result_handle(response,stream):
    if stream:
        return response
    else:
        if response.status_code != HTTPStatus.OK:
            when_http_not_ok(response)
        else:
            return response.output.text

async def sse_event_generator(response):
    """
    通用的 SSE 事件生成器，接受一个异步生成器并生成 SSE 格式的数据。

    :param response: x
    """
    try:
        # 可选：发送开始事件
        yield "event: start\n"

        # 从传入的异步生成器中逐块读取数据
        async for chunk in response:
            content = chunk.output.text if chunk.output.text else ""
            yield f"data: {json.dumps(content)}\n\n"

        # 可选：发送结束事件
        yield "event: end\n"

    except Exception as e:
        logger.error(f"SSE 流错误: {str(e)}")
        yield f"event: error\ndata: {str(e)}\n\n"

def when_http_not_ok(response):
    logger.error(f'request_id={response.request_id}')
    logger.error(f'code={response.status_code}')
    logger.error(f'message={response.message}')
    logger.error(f'请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code')

if __name__ == '__main__':
    example_messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "讲一个短故事"},
    ]

    response1 = get_dashscope_completion(DashScopeAPIParam(
                                                           app_id=os.getenv("ADDRESS_APP_ID"),
                                                           # messages=example_messages,
                                                           prompt = "深圳市南山区南山区粤海街道滨海社区海天二路19号盈峰中心")
                                         )
    s = result_handle(response1,stream=False)
    print("\n")
    print(s)
