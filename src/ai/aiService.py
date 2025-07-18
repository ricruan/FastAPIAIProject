import json
import logging
from string import Template
from fastapi import Depends
from sqlmodel import Session
from src.ai.openAi.deepseek import get_deepseek_completion, handle_ds_response_block
from src.ai.openAi.qwen import get_qwen_completion
from src.ai.pojo.promptBo import PromptContent
from src.common.enum.codeEnum import CodeEnum
from src.db.db import get_db, engine
from src.exception.aiException import AIException
from src.pojo.bo.aiBo import GetJsonModel, NormalLLMRequestModel, ModelConfig
from src.service.aiCodeService import get_code_value_by_code
from src.service.apiInfoService import api_info_2_struct_str
from src.utils.dateUtils import get_now_4_prompt

logger = logging.getLogger(__name__)




async def do_api_2_llm(llm_prams: ModelConfig) -> str:
    """
    根据model入参自动选择调用模型类型
    :param llm_prams: 模型配置参数及messages,messages必传
    :return:
    """
    if llm_prams.messages is None:
        raise AIException.quick_raise("messages is required")


    if "deepseek" in llm_prams.model:
        response = await get_deepseek_completion(**llm_prams.model_dump())

    elif "qwen" in llm_prams.model:
        response = await get_qwen_completion(**llm_prams.model_dump())

    else:
        response = await get_deepseek_completion(**llm_prams.model_dump())

    if llm_prams.stream:
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
            yield f"data: {json.dumps(content)}\n\n"

        # 可选：发送结束事件
        yield "event: end\n"

    except Exception as e:
        logger.error(f"SSE 流错误: {str(e)}")
        yield f"event: error\ndata: {str(e)}\n\n"



async def normal_json_structure_extraction(query: str,model: str,structure: str):
    """
    通用JSON结构提取
    :param query: 用户输入
    :param model: 调用模型
    :param structure: JSON结构信息
    :return: LLM提取到的结果
    """
    with Session(engine) as db:
        prompt_text = get_code_value_by_code(session=db, code_value=CodeEnum.JSON_STRUCTURE_EXTRACTION_PROMPT_CODE.value)
        date_info = get_now_4_prompt()
        prompt_template = Template(prompt_text)
        prompt = prompt_template.substitute(struct=structure,date_info=date_info)
        messages = [PromptContent.as_system(prompt), PromptContent.as_user(query)]
        result = await do_api_2_llm(ModelConfig(model=model, messages=messages, stream=False))
        return result

async def easy_json_structure_extraction(params :GetJsonModel):
    with Session(engine) as db:
        struct = api_info_2_struct_str(session=db, api_code=params.api_code)
        return await normal_json_structure_extraction(params.query, params.model, struct)


async def get_time_range(query: str,model: str):
    """
    根据自然语言提取时间范围
    :param query:上个月张三家的电费是多少
    :param model: 调用模型
    :return: 一个数组，第一个dict是开始时间，第二个dict是结束时间
    """
    params = GetJsonModel(query=query, model=model, api_code=CodeEnum.DATETIME_TO_TIMESTAMP_FUNC_CODE.value)
    return easy_json_structure_extraction(params)