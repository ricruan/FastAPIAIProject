from typing import Optional, Dict, List, Any, Sequence
from datetime import datetime

from sqlmodel import Session, select, delete, update

from src.exception.aiException import AIException
from src.pojo.po.promptPo import Prompt

def create_prompt(session: Session, prompt: Prompt) -> Prompt:
    """
    创建提示词

    Args:
        session: 数据库会话
        prompt: 提示词模型实例

    Returns:
        创建后的提示词模型实例
    """
    session.add(prompt)
    session.commit()
    session.refresh(prompt)
    return prompt

def get_prompt_by_id(session: Session, prompt_id: str) -> Optional[Prompt]:
    """
    通过ID获取提示词

    Args:
        session: 数据库会话
        prompt_id: 提示词ID

    Returns:
        提示词模型实例，如果不存在则返回None
    """
    statement = select(Prompt).where(Prompt.id == prompt_id)
    result = session.exec(statement).first()
    return result

def get_prompt_by_code(session: Session, code: str) -> Optional[Prompt]:
    """
    通过编码获取提示词

    Args:
        session: 数据库会话
        code: 提示词编码

    Returns:
        提示词模型实例，如果不存在则返回None
    """
    statement = select(Prompt).where(Prompt.code == code)
    result = session.exec(statement).first()
    return result

def get_prompt_by_code_with_check(session: Session, code: str) -> Prompt:
    """
    带校验获取提示词，如果没找到直接报错

    Args:
        session: 数据库会话
        code: 提示词编码

    Returns:
        提示词模型实例

    Raises:
        AIException: 如果找不到对应的提示词
    """
    prompt = get_prompt_by_code(session, code)
    if prompt is None:
        raise AIException.quick_raise(f"没有找到对应的提示词(code:{code})")
    return prompt

def search_prompts(session: Session, search_params: Dict[str, Any]) -> Sequence[Prompt]:
    """
    根据提供的参数搜索提示词，使用Prompt中定义的like_search_fields
    来决定查询方式

    Args:
        session: 数据库会话
        search_params: 搜索参数字典，键为Prompt的字段名，值为搜索条件

    Returns:
        符合条件的Prompt列表
    """
    statement = select(Prompt)

    # 获取Prompt类的所有字段名
    prompt_fields = [column.name for column in Prompt.__table__.columns]

    # 动态构建查询条件
    for field, value in search_params.items():
        if field in prompt_fields and value is not None:
            # 根据字段是否在like_search_fields中决定查询方式
            if field in Prompt.like_search_fields and isinstance(value, str):
                statement = statement.where(getattr(Prompt, field).like(f"%{value}%"))
            else:
                # 对于其他字段，使用精确匹配
                statement = statement.where(getattr(Prompt, field) == value)

    # 执行查询
    results = session.exec(statement).all()
    return results

def update_prompt(session: Session, prompt_id: str, update_data: Dict[str, Any]) -> Optional[Prompt]:
    """
    更新提示词

    Args:
        session: 数据库会话
        prompt_id: 提示词ID
        update_data: 要更新的数据字典

    Returns:
        更新后的提示词模型实例，如果不存在则返回None
    """
    # 先获取提示词
    db_prompt = get_prompt_by_id(session, prompt_id)
    if not db_prompt:
        return None

    # 更新字段
    for field, value in update_data.items():
        if hasattr(db_prompt, field):
            setattr(db_prompt, field, value)

    # 更新更新时间
    db_prompt.updated_at = datetime.now()

    session.add(db_prompt)
    session.commit()
    session.refresh(db_prompt)
    return db_prompt

def update_prompt_by_code(session: Session, code: str, update_data: Dict[str, Any]) -> Optional[Prompt]:
    """
    通过编码更新提示词

    Args:
        session: 数据库会话
        code: 提示词编码
        update_data: 要更新的数据字典

    Returns:
        更新后的提示词模型实例，如果不存在则返回None
    """
    # 先获取提示词
    db_prompt = get_prompt_by_code(session, code)
    if not db_prompt:
        return None

    # 更新字段
    for field, value in update_data.items():
        if hasattr(db_prompt, field):
            setattr(db_prompt, field, value)

    # 更新更新时间
    db_prompt.updated_at = datetime.now()

    session.add(db_prompt)
    session.commit()
    session.refresh(db_prompt)
    return db_prompt

def delete_prompt(session: Session, prompt_id: str) -> bool:
    """
    删除提示词

    Args:
        session: 数据库会话
        prompt_id: 提示词ID

    Returns:
        是否成功删除
    """
    db_prompt = get_prompt_by_id(session, prompt_id)
    if not db_prompt:
        return False

    session.delete(db_prompt)
    session.commit()
    return True

def delete_prompt_by_code(session: Session, code: str) -> bool:
    """
    通过编码删除提示词

    Args:
        session: 数据库会话
        code: 提示词编码

    Returns:
        是否成功删除
    """
    db_prompt = get_prompt_by_code(session, code)
    if not db_prompt:
        return False

    session.delete(db_prompt)
    session.commit()
    return True

def batch_create_prompts(session: Session, prompts: List[Prompt]) -> List[Prompt]:
    """
    批量创建提示词

    Args:
        session: 数据库会话
        prompts: 提示词模型实例列表

    Returns:
        创建后的提示词模型实例列表
    """
    session.add_all(prompts)
    session.commit()
    for prompt in prompts:
        session.refresh(prompt)
    return prompts

def get_all_prompts(session: Session) -> Sequence[Prompt]:
    """
    获取所有提示词

    Args:
        session: 数据库会话

    Returns:
        所有提示词模型实例列表
    """
    statement = select(Prompt)
    results = session.exec(statement).all()
    return results

def get_prompts_by_category(session: Session, category: str) -> Sequence[Prompt]:
    """
    通过分类获取提示词列表

    Args:
        session: 数据库会话
        category: 提示词分类

    Returns:
        提示词模型实例列表
    """
    statement = select(Prompt).where(Prompt.category == category)
    results = session.exec(statement).all()
    return results

def get_prompts_by_model_type(session: Session, model_type: str) -> Sequence[Prompt]:
    """
    通过模型类型获取提示词列表

    Args:
        session: 数据库会话
        model_type: 模型类型

    Returns:
        提示词模型实例列表
    """
    statement = select(Prompt).where(Prompt.model_type == model_type)
    results = session.exec(statement).all()
    return results

def get_prompts_by_agent_code(session: Session, agent_code: str) -> Sequence[Prompt]:
    """
    通过Agent编码获取提示词列表

    Args:
        session: 数据库会话
        agent_code: Agent编码

    Returns:
        提示词模型实例列表
    """
    statement = select(Prompt).where(Prompt.agent_code == agent_code)
    results = session.exec(statement).all()
    return results

def get_prompts_by_status(session: Session, status: str) -> Sequence[Prompt]:
    """
    通过状态获取提示词列表

    Args:
        session: 数据库会话
        status: 状态

    Returns:
        提示词模型实例列表
    """
    statement = select(Prompt).where(Prompt.status == status)
    results = session.exec(statement).all()
    return results

def increment_usage_count(session: Session, prompt_id: str) -> Optional[Prompt]:
    """
    增加提示词使用次数

    Args:
        session: 数据库会话
        prompt_id: 提示词ID

    Returns:
        更新后的提示词模型实例，如果不存在则返回None
    """
    db_prompt = get_prompt_by_id(session, prompt_id)
    if not db_prompt:
        return None

    db_prompt.usage_count += 1
    db_prompt.last_called_at = datetime.now()
    db_prompt.updated_at = datetime.now()

    session.add(db_prompt)
    session.commit()
    session.refresh(db_prompt)
    return db_prompt

def increment_usage_count_by_code(session: Session, code: str) -> Optional[Prompt]:
    """
    通过编码增加提示词使用次数

    Args:
        session: 数据库会话
        code: 提示词编码

    Returns:
        更新后的提示词模型实例，如果不存在则返回None
    """
    db_prompt = get_prompt_by_code(session, code)
    if not db_prompt:
        return None

    db_prompt.usage_count += 1
    db_prompt.last_called_at = datetime.now()
    db_prompt.updated_at = datetime.now()

    session.add(db_prompt)
    session.commit()
    session.refresh(db_prompt)
    return db_prompt

def count_prompts(session: Session) -> int:
    """
    统计提示词数量

    Args:
        session: 数据库会话

    Returns:
        提示词的数量
    """
    statement = select(Prompt)
    results = session.exec(statement).all()
    return len(results)

def count_prompts_by_category(session: Session, category: str) -> int:
    """
    统计特定分类的提示词数量

    Args:
        session: 数据库会话
        category: 提示词分类

    Returns:
        特定分类的提示词数量
    """
    statement = select(Prompt).where(Prompt.category == category)
    results = session.exec(statement).all()
    return len(results)

def count_prompts_by_status(session: Session, status: str) -> int:
    """
    统计特定状态的提示词数量

    Args:
        session: 数据库会话
        status: 状态

    Returns:
        特定状态的提示词数量
    """
    statement = select(Prompt).where(Prompt.status == status)
    results = session.exec(statement).all()
    return len(results)
