from typing import Optional, Dict, List, Any

from sqlalchemy import Sequence
from sqlmodel import Session, select

from src.pojo.po.apiInfoPo import APIInfo

def create_api_info(session: Session, api_info: APIInfo):
    session.add(api_info)
    session.commit()
    session.refresh(api_info)
    return api_info

def get_info_by_api_code(session: Session, api_code: str)  -> Optional[APIInfo]:
    statement = select(APIInfo).where(APIInfo.api_code == api_code)
    api = session.exec(statement).first()
    return api

def get_info_by_type_code(session: Session, type_code: str)  -> Optional[Sequence[APIInfo]]:
    statement = select(APIInfo).where(APIInfo.type_code == type_code)
    api = session.exec(statement).all()
    return api

def search_api_info(session: Session, search_params: Dict[str, Any]) -> Sequence[APIInfo]:
    """
    根据提供的参数搜索API信息，使用APIInfo模型中定义的like_search_fields和exact_search_fields
    来决定查询方式
    
    Args:
        session: 数据库会话
        search_params: 搜索参数字典，键为APIInfo的字段名，值为搜索条件
        
    Returns:
        符合条件的APIInfo列表
    """
    statement = select(APIInfo)
    
    # 获取APIInfo类的所有字段名
    api_info_fields = [column.name for column in APIInfo.__table__.columns]
    
    # 动态构建查询条件
    for field, value in search_params.items():
        if field in api_info_fields and value is not None:
            # 根据字段是否在like_search_fields中决定查询方式
            if field in APIInfo.like_search_fields and isinstance(value, str):
                statement = statement.where(getattr(APIInfo, field).like(f"%{value}%"))
            else:
                # 对于exact_search_fields或其他字段，使用精确匹配
                statement = statement.where(getattr(APIInfo, field) == value)
    
    # 执行查询
    results = session.exec(statement).all()
    return results
