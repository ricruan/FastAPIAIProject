import json
import logging

from src.pojo.vo.difyResponse import DifyResponse
from src.service.erpService import erp_execute_sql
from src.utils.dataUtils import is_valid_json

logger = logging.getLogger(__name__)
# 无数据时回复
no_data = DifyResponse.not_found_data()



async def dify_result_handler(result):
    """
    处理Dify服务返回结果
    :param result: 输入结果，可能是dict或list
    :return: 提取的sql_data或原始列表，不满足条件返回空列表
    """
    logger.info(f"\nDify最终需要处理的返回结果:\n {result}")

    json_data = result
    try:
        if json_data["answer"] is not None:
            answer = json_data["answer"]

            if is_valid_json(answer):
                answer = json.loads(answer)
                # todo  看之后是否需要去掉这块逻辑， 当时是因为执行SQL接口调不通 想着异常之后在这里手动调
                if answer.get("type")=="sql":
                    result = await erp_execute_sql(answer.get("data"))
                    return DifyResponse.to_data(result)

            if isinstance(answer, dict):
                if "data" in answer:
                    return DifyResponse.to_data(answer.get("data"))
                else:
                    return no_data
            elif isinstance(answer, list):
                return answer
            elif isinstance(answer, str):
                return DifyResponse.to_text(answer)
            return no_data
        else:
            return no_data
    except Exception as e:
        logger.error(f"处理Dify返回结果异常:{e}")
        return no_data



