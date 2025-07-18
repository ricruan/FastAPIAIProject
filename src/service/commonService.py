import json
from sqlmodel import Session
from src.ai.aiService import do_api_2_llm
from src.ai.pojo.promptBo import PromptContent
from src.common.enum.codeEnum import CodeEnum
from src.pojo.bo.aiBo import ModelConfig
from src.pojo.po.promptPo import PromptCodeEnum
from src.pojo.po.userProfilePo import UserProfile
from src.service.aiCodeService import get_code_value_by_code
from src.service.promptService import get_prompt_by_code_service
from src.service.sessionDetailService import get_history_query_by_user_id
from src.utils.dataUtils import is_valid_json


async def get_question_recommend_by_uid(user_id:str,db: Session) :
    """
    根据user_id获取推荐问题
    :param user_id: 用户ID
    :param db:
    :return: 如果转不了json就是str,你永远不知道LLM会返回什么
    """
    prompt_text = get_code_value_by_code(session=db,
                                         code_value=CodeEnum.QUESTION_RECOMMEND_PROMPT_CODE.value)
    histories = get_history_query_by_user_id(session=db,user_id=user_id)
    system_prompt = PromptContent.as_system(prompt_text).template_handle({'histories':histories})
    user_prompt = PromptContent.as_user("请帮我推荐5个高频问题，以字符数组的形式")
    response = await do_api_2_llm(ModelConfig(stream=False,messages=list([system_prompt,user_prompt])))
    if not response and is_valid_json(response):
        response = json.loads(response)
    return response


async def get_question_recommend_by_profile(profile: UserProfile,db: Session) :
    """
    根据用户画像获取推荐问题
    :param profile: 用户画像
    :param db:
    :return:
    """
    histories = get_history_query_by_user_id(session=db, user_id=profile.user_id)
    prompt_po = get_prompt_by_code_service(session=db, code=PromptCodeEnum.QUESTION_RECOMMEND_PLUS_PROMPT.value)
    prompt = prompt_po.render_prompt(variable={'histories': histories,'user_info':profile.user_info})
    messages = PromptContent.to_messages(prompt=prompt,query=prompt_po.user_prompt)
    response = await do_api_2_llm(ModelConfig(stream=False, messages=messages))
    if not response and is_valid_json(response):
        response = json.loads(response)
    return response