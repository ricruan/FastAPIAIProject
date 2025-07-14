from typing import Optional, Dict, List, Any, Sequence
from datetime import datetime

from sqlmodel import Session, select, delete, update

from src.exception.aiException import AIException
from src.pojo.po.userProfilePo import UserProfile

def create_user_profile(session: Session, user_profile: UserProfile) -> UserProfile:
    """
    创建用户画像

    Args:
        session: 数据库会话
        user_profile: 用户画像模型实例

    Returns:
        创建后的用户画像模型实例
    """
    session.add(user_profile)
    session.commit()
    session.refresh(user_profile)
    return user_profile

def get_profile_by_id(session: Session, profile_id: str) -> Optional[UserProfile]:
    """
    通过ID获取用户画像

    Args:
        session: 数据库会话
        profile_id: 用户画像ID

    Returns:
        用户画像模型实例，如果不存在则返回None
    """
    statement = select(UserProfile).where(UserProfile.id == profile_id)
    result = session.exec(statement).first()
    return result

def get_profile_by_user_id(session: Session, user_id: str) -> Optional[UserProfile]:
    """
    通过用户ID获取用户画像

    Args:
        session: 数据库会话
        user_id: 用户ID

    Returns:
        用户画像模型实例，如果不存在则返回None
    """
    statement = select(UserProfile).where(UserProfile.user_id == user_id)
    result = session.exec(statement).first()
    return result

def get_profile_by_user_id_with_check(session: Session, user_id: str) -> UserProfile:
    """
    带校验获取用户画像，如果没找到直接报错

    Args:
        session: 数据库会话
        user_id: 用户ID

    Returns:
        用户画像模型实例

    Raises:
        AIException: 如果找不到对应的用户画像
    """
    profile = get_profile_by_user_id(session, user_id)
    if profile is None:
        raise AIException.quick_raise(f"没有找到对应的用户画像(user_id:{user_id})")
    return profile

def search_user_profiles(session: Session, search_params: Dict[str, Any]) -> Sequence[UserProfile]:
    """
    根据提供的参数搜索用户画像，使用UserProfile中定义的like_search_fields
    来决定查询方式

    Args:
        session: 数据库会话
        search_params: 搜索参数字典，键为UserProfile的字段名，值为搜索条件

    Returns:
        符合条件的UserProfile列表
    """
    statement = select(UserProfile)

    # 获取UserProfile类的所有字段名
    profile_fields = [column.name for column in UserProfile.__table__.columns]

    # 动态构建查询条件
    for field, value in search_params.items():
        if field in profile_fields and value is not None:
            # 根据字段是否在like_search_fields中决定查询方式
            if field in UserProfile.like_search_fields and isinstance(value, str):
                statement = statement.where(getattr(UserProfile, field).like(f"%{value}%"))
            else:
                # 对于其他字段，使用精确匹配
                statement = statement.where(getattr(UserProfile, field) == value)

    # 执行查询
    results = session.exec(statement).all()
    return results

def update_user_profile(session: Session, profile_id: str, update_data: Dict[str, Any]) -> Optional[UserProfile]:
    """
    更新用户画像

    Args:
        session: 数据库会话
        profile_id: 用户画像ID
        update_data: 要更新的数据字典

    Returns:
        更新后的用户画像模型实例，如果不存在则返回None
    """
    # 先获取用户画像
    db_profile = get_profile_by_id(session, profile_id)
    if not db_profile:
        return None

    # 更新字段
    for field, value in update_data.items():
        if hasattr(db_profile, field):
            setattr(db_profile, field, value)

    # 更新更新时间
    db_profile.update_time = datetime.now()

    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile

def update_user_profile_by_user_id(session: Session, user_id: str, update_data: Dict[str, Any]) -> Optional[UserProfile]:
    """
    通过用户ID更新用户画像

    Args:
        session: 数据库会话
        user_id: 用户ID
        update_data: 要更新的数据字典

    Returns:
        更新后的用户画像模型实例，如果不存在则返回None
    """
    # 先获取用户画像
    db_profile = get_profile_by_user_id(session, user_id)
    if not db_profile:
        return None

    # 更新字段
    for field, value in update_data.items():
        if hasattr(db_profile, field):
            setattr(db_profile, field, value)

    # 更新更新时间
    db_profile.update_time = datetime.now()

    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile

def delete_user_profile(session: Session, profile_id: str) -> bool:
    """
    删除用户画像

    Args:
        session: 数据库会话
        profile_id: 用户画像ID

    Returns:
        是否成功删除
    """
    db_profile = get_profile_by_id(session, profile_id)
    if not db_profile:
        return False

    session.delete(db_profile)
    session.commit()
    return True

def delete_user_profile_by_user_id(session: Session, user_id: str) -> bool:
    """
    通过用户ID删除用户画像

    Args:
        session: 数据库会话
        user_id: 用户ID

    Returns:
        是否成功删除
    """
    db_profile = get_profile_by_user_id(session, user_id)
    if not db_profile:
        return False

    session.delete(db_profile)
    session.commit()
    return True

def batch_create_user_profiles(session: Session, user_profiles: List[UserProfile]) -> List[UserProfile]:
    """
    批量创建用户画像

    Args:
        session: 数据库会话
        user_profiles: 用户画像模型实例列表

    Returns:
        创建后的用户画像模型实例列表
    """
    session.add_all(user_profiles)
    session.commit()
    for profile in user_profiles:
        session.refresh(profile)
    return user_profiles

def get_all_user_profiles(session: Session) -> Sequence[UserProfile]:
    """
    获取所有用户画像

    Args:
        session: 数据库会话

    Returns:
        所有用户画像模型实例列表
    """
    statement = select(UserProfile)
    results = session.exec(statement).all()
    return results

def get_user_profiles_by_source(session: Session, source: str) -> Sequence[UserProfile]:
    """
    通过来源获取用户画像列表

    Args:
        session: 数据库会话
        source: 用户来源

    Returns:
        用户画像模型实例列表
    """
    statement = select(UserProfile).where(UserProfile.source == source)
    results = session.exec(statement).all()
    return results

def count_user_profiles(session: Session) -> int:
    """
    统计用户画像数量

    Args:
        session: 数据库会话

    Returns:
        用户画像的数量
    """
    statement = select(UserProfile)
    results = session.exec(statement).all()
    return len(results)
