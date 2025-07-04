import json
import logging
from src.pojo.vo.difyResponse import DifyResponse
from src.utils.dataUtils import is_valid_json

logger = logging.getLogger(__name__)
# 无数据时回复
NO_DATA_RESPONSE = DifyResponse.not_found_data()



async def dify_result_handler(result) -> DifyResponse|list:
    """
    处理Dify服务返回结果
    :param result: 输入结果，可能是dict或list
    :return: 提取的sql_data或原始列表，不满足条件返回空列表
    """
    logger.info(f"\nDify最终需要处理的返回结果:\n {result}")

    json_data = result
    if json_data["answer"] is not None:
        answer = json_data["answer"]
        if is_valid_json(answer):
           answer = json.loads(answer)
        if isinstance(answer, dict):
            if "data" in answer:
                return DifyResponse.to_data(answer.get("data"))
            else:
                return NO_DATA_RESPONSE
        elif isinstance(answer, list):
            return answer
        elif isinstance(answer, str):
            return DifyResponse.to_text(answer)
        return NO_DATA_RESPONSE
    else:
        return NO_DATA_RESPONSE


