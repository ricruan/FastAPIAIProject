from typing import Optional, Dict, List, Any, Sequence
from datetime import date

from sqlmodel import Session, select, update,delete

from src.pojo.po.aiCodePo import Code

def create_code(session: Session, code: Code) -> Code:
    """
    创建编码记录

    Args:
        session: 数据库会话
        code: 编码模型实例

    Returns:
        创建后的编码模型实例
    """
    session.add(code)
    session.commit()
    session.refresh(code)
    return code

def batch_create_codes(session: Session, codes: List[Code]) -> List[Code]:
    """
    批量创建编码记录

    Args:
        session: 数据库会话
        codes: 编码模型实例列表

    Returns:
        创建后的编码模型实例列表
    """
    session.add_all(codes)
    session.commit()
    for code in codes:
        session.refresh(code)
    return codes

def get_code_by_id(session: Session, code_id: str) -> Optional[Code]:
    """
    通过ID获取编码记录

    Args:
        session: 数据库会话
        code_id: 编码ID

    Returns:
        编码模型实例，如果不存在则返回None
    """
    statement = select(Code).where(Code.id == code_id)
    result = session.exec(statement).first()
    return result

def get_code_by_code(session: Session, code_value: str) -> Optional[Code]:
    """
    通过编码值获取编码记录

    Args:
        session: 数据库会话
        code_value: 编码值

    Returns:
        编码模型实例，如果不存在则返回None
    """
    statement = select(Code).where(Code.code == code_value)
    result = session.exec(statement).first()
    return result

def get_codes_by_type(session: Session, type_value: str) -> Sequence[Code]:
    """
    通过类型获取编码记录列表

    Args:
        session: 数据库会话
        type_value: 类型值

    Returns:
        编码模型实例列表
    """
    statement = select(Code).where(Code.type == type_value)
    results = session.exec(statement).all()
    return results

def get_codes_by_parent_code(session: Session, parent_code: str) -> Sequence[Code]:
    """
    通过上级编码获取编码记录列表

    Args:
        session: 数据库会话
        parent_code: 上级编码

    Returns:
        编码模型实例列表
    """
    statement = select(Code).where(Code.parent_code == parent_code)
    results = session.exec(statement).all()
    return results

def search_codes(session: Session, search_params: Dict[str, Any]) -> Sequence[Code]:
    """
    根据提供的参数搜索编码记录，使用Code中定义的like_search_fields
    来决定查询方式

    Args:
        session: 数据库会话
        search_params: 搜索参数字典，键为Code的字段名，值为搜索条件

    Returns:
        符合条件的Code列表
    """
    statement = select(Code)

    # 获取Code类的所有字段名
    code_fields = [column.name for column in Code.__table__.columns]

    # 动态构建查询条件
    for field, value in search_params.items():
        if field in code_fields and value is not None:
            # 根据字段是否在like_search_fields中决定查询方式
            if field in Code.like_search_fields and isinstance(value, str):
                statement = statement.where(getattr(Code, field).like(f"%{value}%"))
            else:
                # 对于其他字段，使用精确匹配
                statement = statement.where(getattr(Code, field) == value)

    # 执行查询
    results = session.exec(statement).all()
    return results

def update_code(session: Session, code_id: str, update_data: Dict[str, Any]) -> Optional[Code]:
    """
    更新编码记录

    Args:
        session: 数据库会话
        code_id: 编码ID
        update_data: 要更新的数据字典

    Returns:
        更新后的编码模型实例，如果不存在则返回None
    """
    # 先获取编码记录
    db_code = get_code_by_id(session, code_id)
    if not db_code:
        return None

    # 更新字段
    for field, value in update_data.items():
        if hasattr(db_code, field):
            setattr(db_code, field, value)

    # 更新更新时间
    db_code.update_time = date.today()

    session.add(db_code)
    session.commit()
    session.refresh(db_code)
    return db_code

def delete_code(session: Session, code_id: str) -> bool:
    """
    删除编码记录

    Args:
        session: 数据库会话
        code_id: 编码ID

    Returns:
        是否成功删除
    """
    db_code = get_code_by_id(session, code_id)
    if not db_code:
        return False

    session.delete(db_code)
    session.commit()
    return True

def delete_codes_by_type(session: Session, type_value: str) -> int:
    """
    通过类型删除所有相关的编码记录

    Args:
        session: 数据库会话
        type_value: 类型值

    Returns:
        删除的记录数量
    """
    statement = delete(Code).where(Code.type == type_value)
    result = session.exec(statement)
    session.commit()
    return result.rowcount

def delete_codes_by_parent_code(session: Session, parent_code: str) -> int:
    """
    通过上级编码删除所有相关的编码记录

    Args:
        session: 数据库会话
        parent_code: 上级编码

    Returns:
        删除的记录数量
    """
    statement = delete(Code).where(Code.parent_code == parent_code)
    result = session.exec(statement)
    session.commit()
    return result.rowcount

def count_codes_by_type(session: Session, type_value: str) -> int:
    """
    统计指定类型的编码记录数量

    Args:
        session: 数据库会话
        type_value: 类型值

    Returns:
        编码记录的数量
    """
    statement = select(Code).where(Code.type == type_value)
    results = session.exec(statement).all()
    return len(results)

def get_all_codes(session: Session) -> Sequence[Code]:
    """
    获取所有编码记录

    Args:
        session: 数据库会话

    Returns:
        所有编码模型实例列表
    """
    statement = select(Code)
    results = session.exec(statement).all()
    return results

def get_codes_by_mapper(session: Session, mapper: str) -> Sequence[Code]:
    """
    通过映射实体获取编码记录列表

    Args:
        session: 数据库会话
        mapper: 映射实体名称

    Returns:
        编码模型实例列表
    """
    statement = select(Code).where(Code.mapper == mapper)
    results = session.exec(statement).all()
    return results
