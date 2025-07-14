import json

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.ai.aiService import do_api_2_llm
from src.ai.pojo.promptBo import PromptContent
from src.common.enum.codeEnum import CodeEnum
from src.db.db import get_db
from src.myHttp.bo.httpResponse import HttpResponse
from src.pojo.bo.aiBo import ModelConfig
from src.service.aiCodeService import get_code_value_by_code
from src.service.sessionDetailService import get_history_query_by_user_id

router = APIRouter(prefix="/common", tags=["通用AI接口"])

@router.get("/question_recommend")
async def common_ai(user_id:str,db: Session = Depends(get_db)):
    prompt_text = get_code_value_by_code(session=db,
                                         code_value=CodeEnum.QUESTION_RECOMMEND_PROMPT_CODE.value)
    histories = get_history_query_by_user_id(session=db,user_id=user_id)
    system_prompt = PromptContent.as_system(prompt_text).template_handle({'histories':histories})
    user_prompt = PromptContent.as_user("请帮我推荐5个高频问题，以字符数组的形式")
    response = await do_api_2_llm(ModelConfig(stream=False,messages=list([system_prompt,user_prompt])))
    return HttpResponse.success(json.loads(response))