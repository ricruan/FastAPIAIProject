import json
from string import Template
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


def get_code_4_prompt(session: Session, code_value: str, variable=None) -> str:
    """
    直接根据code获取prompt
    :param session:
    :param code_value: 码值
    :param variable: dict template变量替换字典
    :return: 用真实值替换掉变量占位符的prompt文本
    """
    if variable is None:
        variable = {}
    prompt_text = get_code_value_by_code(session=session, code_value=code_value)
    prompt_template = Template(prompt_text)
    prompt = prompt_template.substitute(**variable)
    return prompt