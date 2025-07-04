import logging
from src.dao.apiInfoDao import get_info_by_api_code
from src.myHttp.utils.myHttpUtils import normal_post, post_with_query_params, form_data_post
from sqlmodel import Session


logger = logging.getLogger(__name__)
ERP_EXEC_SQL_API_CODE = "erp_exec_sql"
ERP_GEN_POPI_API_CODE = "erp_generate_popi"
ERP_ORDER_SEARCH_API_CODE = "erp_order_search"

async def erp_execute_sql(sql, session: Session):
    api_info = get_info_by_api_code(session,ERP_EXEC_SQL_API_CODE)


    if isinstance(sql,str):
        sql = {"sql": sql}
    else:
        sql = sql.model_dump()
    response = await normal_post(api_info.api_url, data=sql, headers={})
    return response['data']

async def erp_generate_popi(data: dict, session: Session):
    api_info = get_info_by_api_code(session,ERP_GEN_POPI_API_CODE)
    response = await post_with_query_params(api_info.api_url, params=data, headers=data)
    return response['data']


async def erp_order_search(data: dict, session: Session):
    api_info = get_info_by_api_code(session,ERP_ORDER_SEARCH_API_CODE)
    response = await form_data_post(api_info.api_url, form_data=data, headers={"token": data['token']})
    return get_data_from_erp_page_response(response)



def get_data_from_erp_page_response(response):
    """
    从erp的分页查询结果中只取数据
    :param response:  erp分页查询结果
    :return:  纯净数据
    """
    return response['data']['list']
