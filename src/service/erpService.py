import copy
import logging
from string import Template
from src.ai.aiService import do_api_2_llm
from src.ai.pojo.promptBo import PromptContent
from src.common.enum.codeEnum import CodeEnum
from src.dao.apiInfoDao import get_info_by_api_code
from src.exception.aiException import AIException
from src.myHttp.utils.myHttpUtils import normal_post, post_with_query_params, form_data_post
from sqlmodel import Session

from src.pojo.bo.aiBo import NormalLLMRequestModel, ModelConfig
from src.service.aiCodeService import get_code_value_by_code
from src.utils.dataUtils import translate_dict_keys_4_list, translate_dict_keys_4_dict

logger = logging.getLogger(__name__)

async def erp_execute_sql(sql, session: Session):
    """
    执行SQL
    :param sql:
    :param session:
    :return:
    """
    api_info = get_info_by_api_code(session,CodeEnum.ERP_EXEC_SQL_API_CODE.value)
    if isinstance(sql,str):
        sql = {"sql": sql}
    else:
        sql = sql.model_dump()
    response = await normal_post(api_info.api_url, data=sql, headers={})
    return response['data']

async def erp_generate_popi(data: dict, session: Session):
    """
    生成POPI
    :param data:
    :param session:
    :return:
    """
    api_info = get_info_by_api_code(session,CodeEnum.ERP_GEN_POPI_API_CODE.value)
    response = await post_with_query_params(api_info.api_url, params=data, headers=data)
    erp_response_check(response)
    return response['data']

async def erp_generate_pi(data: dict, session: Session):
    """
    生成PI
    :param data:
    :param session:
    :return:
    """
    api_info = get_info_by_api_code(session,CodeEnum.ERP_GEN_PI_API_CODE.value)
    response = await form_data_post(api_info.api_url, form_data=data, headers=data)
    erp_response_check(response)
    return response['data']


async def erp_order_search(data: dict, session: Session):
    """
    订单查询
    :param data:
    :param session:
    :return:
    """
    response = await erp_order_search_without_check(data, session)
    erp_response_check(response)
    return get_data_from_erp_page_response(response)

async def erp_order_search_without_check(data: dict, session: Session):
    """
    订单查询 不带校验
    :param data:
    :param session:
    :return:
    """
    api_info = get_info_by_api_code(session,CodeEnum.ERP_ORDER_SEARCH_API_CODE.value)
    response = await form_data_post(api_info.api_url, form_data=data, headers={"token": data['token']})
    return response

async def erp_user_sale_info(data: dict, session: Session):
    """
    销售情况查询
    :param data:
    :param session:
    :return:
    """
    api_info = get_info_by_api_code(session,CodeEnum.ERP_USER_SALE_INFO_API_CODE.value)
    response = await form_data_post(api_info.api_url, form_data=data, headers={"token": data['token']})
    erp_response_check(response)
    if isinstance(response['data'],list):
        return response['data']
    return list(response['data'].values())

async def erp_inventory_detail_search(data: dict, session: Session):
    """
    库存详情查询
    :param data:
    :param session:
    :return:
    """
    api_info = get_info_by_api_code(session,CodeEnum.ERP_INVENTORY_DETAIL_SEARCH_API_CODE.value)
    response = await form_data_post(api_info.api_url, form_data=data, headers={"token": data['token']})
    erp_response_check(response)
    return response['data']

async def erp_inventory_detail_search_by_cn(data: dict, session: Session):
    """
    库存详情查询，翻译为中文字段
    :param data:
    :param session:
    :return:
    """
    response = await erp_inventory_detail_search(data, session)
    r1 = copy.deepcopy(response['stockDetails'])
    del response['stockDetails']
    result1 = translate_dict_keys_4_dict(response, get_code_value_by_code(session,
                                                                          CodeEnum.ERP_INVENTORY_DETAIL_SEARCH_API_CODE.value + "_1"))
    result2 = translate_dict_keys_4_list(r1, get_code_value_by_code(session,
                                                                    CodeEnum.ERP_INVENTORY_DETAIL_SEARCH_API_CODE.value + "_2"))
    result1['库存明细'] = result2
    return result1



def get_data_from_erp_page_response(response):
    """
    从erp的分页查询结果中只取数据
    :param response:  erp分页查询结果
    :return:  纯净数据
    """
    return response['data']['list']

def erp_response_check(response):
    """
    erp接口返回结果检查, code 为 0 1 时是正常的
    :param response: erp接口返回结果
    :return: 无
    """
    if response['code'] not in [1,0] :
        raise AIException.quick_raise(f"ERP接口异常:{response['msg']}")

def get_inventory_analysis_prompt(data,prompt_text:str) -> list[dict]:
    prompt_template = Template(prompt_text)
    prompt = prompt_template.substitute(data=data)
    messages = [PromptContent.as_system(prompt),
                PromptContent.as_user("基于我提供的数据,帮我进行库存分析. 以下是我提供的数据:\n" + str(data))]
    return messages

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

    result = await do_api_2_llm(ModelConfig(model=model, messages=messages, stream=stream))
    return result

async def erp_seller_sale_info_analysis(llm_params: NormalLLMRequestModel,sale_data: str, session: Session):
    """
    销售人员销售情况分析
    :param llm_params: LLM的擦拭农户
    :param sale_data:销售数据
    :param session:
    :return:
    """
    prompt_text = get_code_value_by_code(session=session, code_value=CodeEnum.ERP_SELLER_WORK_ANALYSIS_PROMPT_CODE.value)
    llm_params.messages = [PromptContent.as_system(prompt_text),
                                            PromptContent.as_user(llm_params.query),
                                            PromptContent.as_assistant(sale_data)]
    return await do_api_2_llm(llm_params)
