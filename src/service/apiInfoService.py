from typing import List, Dict

from sqlmodel import Session

from src.dao.apiInfoDao import get_info_by_api_code, get_info_by_type_code
from src.pojo.po.apiInfoPo import APIInfo



def api_info_2_struct_str(session: Session, api_code: str) -> Dict:
    """
    以结构化字符串的形式返回API信息，用于API结构获取
    :param session:
    :param api_code:
    :return:
    """
    api_infos = get_info_by_api_code(session, api_code)
    return {
        "API结构": api_infos.api_param_struct,
        "字段含义": api_infos.api_param_desc,
        "参考示例": api_infos.api_param_template,
    }


def get_api_info_4_task_classify(session: Session, type_code: str) -> List[Dict]:
    """
    简化API信息，用于LLM的任务分类
    :param session:
    :param type_code:
    :return:
    """
    api_infos = get_info_by_type_code(session, type_code)
    return [
    {
        "api_code": api_info.api_code,
        "api_name": api_info.api_name,
        "api_desc": api_info.api_desc
    }
    for api_info in api_infos ]
