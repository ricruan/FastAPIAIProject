import logging
from datetime import datetime

from sqlmodel import Session
from src.ai.aiService import do_api_2_llm
from src.ai.pojo.promptBo import PromptContent
from src.common.enum.codeEnum import CodeEnum
from src.dao.userProfileDao import get_profile_by_user_id, create_user_profile, update_user_profile
from src.pojo.bo.aiBo import ModelConfig
from src.pojo.po.userProfilePo import UserProfile
from src.service.aiCodeService import get_code_value_by_code, get_code_4_prompt
from src.service.sessionDetailService import get_history_qa_by_user_id, histories_2_simple_qa

logger = logging.getLogger(__name__)

def check_new_user(session: Session,user_id: str, user_source: str):
    """
    检查是否为用户画像中不存在的新用户， if true, save |else None
    :param session:
    :param user_id: 用户ID
    :param user_source:用户来源
    :return:
    """
    profile = get_profile_by_user_id(session=session, user_id= user_id)
    if profile is not None:
        return None

    profile_new = UserProfile.get_profile(user_id=user_id, source=user_source)
    return create_user_profile(session=session, user_profile= profile_new)


async def analysis_language_style(session: Session,profile: UserProfile):
    """
    分析用户画像中的 语言风格, 并更新字段
    :param session:
    :param profile:
    :return:
    """
    # todo 后期加循环，一次处理完所有未处理的对话。目前prompt限制 once limit 50
    user_prompt = "结合AI之前对我总结的语言风格,以及我与AI新的历史问答记录,再次生成一份新的语言风格总结。以下是旧的语言风格总结内容:"
    histories = get_history_qa_by_user_id(session=session, user_id=profile.user_id, last_handle_session_id=profile.last_handle_session_id)
    if not histories :
        logger.info(f"【用户画像分析】【语言风格】:该用户({profile.user_id})暂无新的未分析对话,本次分析过程跳过.")
        return
    profile.last_handle_session_id = histories[0]['id']
    histories = histories_2_simple_qa(histories=histories)
    variable = {'user_info':profile.user_info,'histories':histories}
    prompt = get_code_4_prompt(session=session, code_value=CodeEnum.UP_LANGUAGE_STYLE_ANALYSIS_PROMPT_CODE.value, variable=variable)
    messages = [PromptContent.as_system(prompt),
                PromptContent.as_user(user_prompt + profile.language_style)]
    result =await  do_api_2_llm(ModelConfig(model='deepseek-reasoner',messages=messages,stream=False))
    profile.language_style = result
    update_user_profile(session=session, profile_id=profile.id, update_data={'language_style':result,
                                                                             'last_handle_session_id':profile.last_handle_session_id,
                                                                             'update_time':datetime.now()})
    return