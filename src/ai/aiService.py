from string import Template

from fastapi import Depends

from src.ai.openAi.deepseek import get_deepseek_completion, handle_ds_response_block
from src.ai.pojo.promptBo import PromptContent
from src.common.enum.codeEnum import CodeEnum
from src.db.db import get_db
from src.service.aiCodeService import get_code_value_by_code





def get_inventory_analysis_prompt(data,prompt_text:str) -> list[dict]:
    prompt_template = Template(prompt_text)
    prompt = prompt_template.substitute(data=data)
    messages = [PromptContent.as_system(prompt).model_dump(), PromptContent.as_user("基于我提供的数据,帮我进行库存分析. 以下是我提供的数据:\n" + str(data)).model_dump()]
    return messages


async def inventory_analysis(data,prompt_text:str) -> str:
    messages = get_inventory_analysis_prompt(data,prompt_text)
    response = await get_deepseek_completion(messages)
    result = handle_ds_response_block(response)
    return result

