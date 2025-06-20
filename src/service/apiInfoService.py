from typing import List, Dict

from src.pojo.po.apiInfoPo import APIInfo



def api_info_2_struct_str(api_infos: APIInfo) -> Dict:
    """
    以结构化字符串的形式返回API信息，用于API结构获取
    :param api_infos:
    :return: 可以直接嵌入提示词的文本
    """
    return {
        "API结构": api_infos.api_param_struct,
        "字段含义": api_infos.api_param_desc,
        "参考示例": api_infos.api_param_template,
    }


def get_api_info_4_task_classify(api_infos: List[APIInfo]) -> List[Dict]:
    """
    简化API信息，用于LLM的任务分类
    
    Args:
        api_infos: APIInfo对象列表
        
    Returns:
        包含api_code、api_name和api_desc字段的字典列表
    """
    return [
    {
        "api_code": api_info.api_code,
        "api_name": api_info.api_name,
        "api_desc": api_info.api_desc
    }
    for api_info in api_infos ]
