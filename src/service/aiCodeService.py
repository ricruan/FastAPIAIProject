import json
from typing import Optional

from sqlmodel import Session

from src.dao.aiCodeDao import get_code_by_code
from src.exception.aiException import AIException
from src.utils.dataUtils import is_valid_json


def get_code_value_by_code(session: Session, code_value: str) -> Optional[str | dict]:
    """
    根据编码获取编码值，若结果可转json，则自动转化为json
    :param session:
    :param code_value:
    :return:
    """
    code = get_code_by_code(session, code_value)
    if code is None:
        raise AIException.quick_raise(f"编码{code_value}不存在")
    if is_valid_json(code.value):
        return json.loads(code.value)
    else:
        return code.value
