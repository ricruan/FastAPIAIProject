from typing import Optional
from sqlmodel import Session

from src.dao.promptDao import get_prompt_by_code, increment_usage_count_by_code
from src.pojo.po.promptPo import Prompt
from src.exception.aiException import AIException

def get_prompt_by_code_service(session: Session, code: str) -> Prompt:
    """
    根据提示词编码查询提示词，并增加使用次数

    Args:
        session: 数据库会话
        code: 提示词编码

    Returns:
        提示词模型实例

    Raises:
        AIException: 如果找不到对应的提示词
    """
    # 查询提示词
    prompt = get_prompt_by_code(session, code)
    if prompt is None:
        raise AIException.quick_raise(f"没有找到对应的提示词(code:{code})")

    # 增加使用次数
    updated_prompt = increment_usage_count_by_code(session, code)
    if updated_prompt is None:
        # 这种情况理论上不会发生，因为我们已经确认提示词存在
        # 但为了健壮性，我们仍然处理这种情况
        raise AIException.quick_raise(f"更新提示词使用次数失败(code:{code})")

    return updated_prompt
