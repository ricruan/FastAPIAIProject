import logging
from datetime import datetime
from sqlmodel import Session
from src.ai.aiService import do_api_2_llm
from src.ai.pojo.promptBo import PromptContent
from src.common.enum.codeEnum import CodeEnum
from src.dao.userProfileDao import get_profile_by_user_id, create_user_profile, update_user_profile, \
    get_all_user_profiles
from src.db.db import engine
from src.pojo.bo.aiBo import ModelConfig
from src.pojo.po.promptPo import PromptCodeEnum
from src.pojo.po.userProfilePo import UserProfile
from src.service.aiCodeService import get_code_4_prompt
from src.service.commonService import get_question_recommend_by_profile
from src.service.promptService import get_prompt_by_code_service
from src.service.sessionDetailService import get_history_qa_by_user_id, histories_2_simple_qa, get_history_normal
import asyncio

from src.utils.dataUtils import nvl

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

async def analysis_all():
    profiles = []
    with Session(engine) as session:
        profiles = get_all_user_profiles(session=session)

    for i in range(0, len(profiles), 4):
        chunk = profiles[i:i + 4]
        # 并发处理当前分块内的所有 profile
        await asyncio.gather(*[analysis_by_user(profile) for profile in chunk])




async def analysis_by_user(profile: UserProfile):
    """
    基于用户开始进行完整的用户画像分析
    :param profile: 用户画像
    :return:
    """
    logger.info(f"【用户画像分析】:对用户{profile.user_id}的分析开始")
    with Session(engine) as session:
        try:
            await analysis_language_style(session=session,profile=profile)
        except Exception as e:
            logger.error(f"【用户画像分析】【语言风格】:用户({profile.user_id})分析发生异常\n{e}")
        try:
            await analysis_preference_questions(session=session,profile=profile)
        except Exception as e:
            logger.error(f"【用户画像分析】【偏好问题】:用户({profile.user_id})分析发生异常\n{e}")
        try:
            await analysis_personality_traits(session=session,profile=profile)
        except Exception as e:
            logger.error(f"【用户画像分析】【性格特征】:用户({profile.user_id})分析发生异常\n{e}")

async def analysis_language_style(session: Session,profile: UserProfile):
    """
    分析用户画像中的 语言风格, 并更新字段
    :param session:
    :param profile:
    :return:
    """
    # todo 后期加循环，一次处理完所有未处理的对话。目前prompt限制  limit 50 once
    user_prompt = "结合AI之前对我总结的语言风格,以及我与AI新的历史问答记录,再次生成一份新的语言风格总结。以下是旧的语言风格总结内容:"
    histories = get_history_qa_by_user_id(session=session, user_id=profile.user_id, last_handle_session_id=profile.last_handle_session_id)
    if not histories :
        logger.info(f"【用户画像分析】【语言风格】:该用户({profile.user_id})暂无新的未分析对话,本次分析过程跳过.")
        return
    histories = histories_2_simple_qa(histories=histories)
    variable = {'user_info':profile.user_info,'histories':histories}
    prompt = get_code_4_prompt(session=session, code_value=CodeEnum.UP_LANGUAGE_STYLE_ANALYSIS_PROMPT_CODE.value, variable=variable)
    messages = [PromptContent.as_system(prompt),
                PromptContent.as_user(user_prompt + nvl(profile.language_style,""))]
    result =await  do_api_2_llm(ModelConfig(model='deepseek-reasoner',messages=messages,stream=False))
    update_user_profile(session=session, profile_id=profile.id, update_data={'language_style':result,
                                                                             # 'last_handle_session_id':profile.last_handle_session_id,
                                                                             'update_time':datetime.now()})
    logger.info(f"【用户画像分析】【语言风格】:用户({profile.user_id})分析完成")


async def analysis_preference_questions(session: Session,profile: UserProfile):
    questions = await get_question_recommend_by_profile(db=session, profile=profile)
    if not questions:
        logger.info(f"【用户画像分析】【偏好问题】:该用户({profile.user_id})暂无新的未分析对话,本次分析过程跳过.")
        return
    update_user_profile(session=session, profile_id=profile.id, update_data={'preference_questions':questions})
    logger.info(f"【用户画像分析】【偏好问题】:用户({profile.user_id})分析完成")


async def analysis_personality_traits(session: Session,profile: UserProfile):
    prompt = get_prompt_by_code_service(session=session, code=PromptCodeEnum.PERSONALITY_TRAITS_PROMPT.value)
    histories = get_history_normal(session=session, user_id=profile.user_id, last_handle_session_id=profile.last_handle_session_id)
    messages = prompt.get_messages(variable={**profile.model_dump(),'histories':histories})
    result = await do_api_2_llm(ModelConfig(model='deepseek-reasoner', messages=messages, stream=False))
    update_user_profile(session=session, profile_id=profile.id,update_data={'personality_traits':result})
    logger.info(f"【用户画像分析】【性格特征】:用户({profile.user_id})分析完成")

