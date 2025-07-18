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
from src.service.commonService import get_question_recommend_by_uid
from src.service.sessionDetailService import get_history_query_by_user_id

router = APIRouter(prefix="/common", tags=["通用AI接口"])

@router.get("/question_recommend")
async def common_ai(user_id:str,db: Session = Depends(get_db)):
    response = await get_question_recommend_by_uid(user_id=user_id,db=db)
    return HttpResponse.success(json.loads(response))