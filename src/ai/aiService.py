import logging
from string import Template
from fastapi import Depends
from sqlmodel import Session
from src.ai.openAi.deepseek import get_deepseek_completion, handle_ds_response_block
from src.ai.openAi.qwen import get_qwen_completion
from src.ai.pojo.promptBo import PromptContent
from src.common.enum.codeEnum import CodeEnum
from src.db.db import get_db, engine
from src.service.aiCodeService import get_code_value_by_code
from src.service.apiInfoService import api_info_2_struct_str
from src.utils.dateUtils import get_now_4_prompt

logger = logging.getLogger(__name__)

def get_inventory_analysis_prompt(data,prompt_text:str) -> list[dict]:
    prompt_template = Template(prompt_text)
    prompt = prompt_template.substitute(data=data)
    messages = [PromptContent.as_system(prompt).model_dump(), PromptContent.as_user("基于我提供的数据,帮我进行库存分析. 以下是我提供的数据:\n" + str(data)).model_dump()]
    return messages


async def do_api_2_llm(prams: dict, model: str) -> str:
    """
    根据model入参自动选择调用模型类型
    :param prams: 模型配置参数及messages,messages必传
    :param model: 模型类型 目前仅支持 ds qwen
    :return:
    """
    if model == "deepseek":
        response = await get_deepseek_completion(**prams)

    elif model == "qwen":
        response = await get_qwen_completion(**prams)

    else:
        response = await get_deepseek_completion(**prams)

    if "stream" in prams and bool(prams["stream"]) == True:
        result = response
    else:
        result = handle_ds_response_block(response)
    return result


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
            content = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
            yield f"data: {content}\n\n"

        # 可选：发送结束事件
        yield "event: end\n"

    except Exception as e:
        logger.error(f"SSE 流错误: {str(e)}")
        yield f"event: error\ndata: {str(e)}\n\n"


async def inventory_analysis(data,prompt_text:str,model: str,stream: bool = True) -> str:
    """
    库存详情分析，根据库存详情数据进行库存分析
    :param stream: 流式输出？
    :param data: 库存详情数据
    :param prompt_text: 提示词
    :param model: 调用模型
    :return: 分析结果
    """
    messages = get_inventory_analysis_prompt(data,prompt_text)
    result = await do_api_2_llm({"messages": messages,"stream": stream},model)
    return result


async def get_time_range(query: str,model: str):
    """
    根据自然语言提取时间范围
    :param query:上个月张三家的电费是多少
    :param model: 调用模型
    :return: 一个数组，第一个dict是开始时间，第二个dict是结束时间
    """
    with Session(engine) as db:
        prompt_text = get_code_value_by_code(session=db, code_value=CodeEnum.JSON_STRUCTURE_EXTRACTION_PROMPT_CODE.value)
        struct = api_info_2_struct_str(session=db, api_code=CodeEnum.DATETIME_TO_TIMESTAMP_FUNC_CODE.value)
        date_info = get_now_4_prompt()
        prompt_template = Template(prompt_text)
        prompt = prompt_template.substitute(struct=struct,date_info=date_info)
        messages = [PromptContent.as_system(prompt).model_dump(), PromptContent.as_user(query).model_dump()]
        result = await do_api_2_llm({"messages": messages},model)
        return result