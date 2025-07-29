from typing import Optional, Dict, List, Any, Sequence
from datetime import datetime

from sqlmodel import Session, select, delete, update

from src.pojo.po.fileUploadsPo import FileUploads


def create_file_upload(session: Session, file_upload: FileUploads) -> FileUploads:
    """
    创建文件上传记录

    Args:
        session: 数据库会话
        file_upload: 文件上传记录模型实例

    Returns:
        创建后的文件上传记录模型实例
    """
    session.add(file_upload)
    session.commit()
    session.refresh(file_upload)
    return file_upload


def get_file_upload_by_id(session: Session, file_id: str) -> Optional[FileUploads]:
    """
    通过ID获取文件上传记录

    Args:
        session: 数据库会话
        file_id: 文件ID

    Returns:
        文件上传记录模型实例，如果不存在则返回None
    """
    statement = select(FileUploads).where(FileUploads.id == file_id)
    result = session.exec(statement).first()
    return result


def get_file_upload_by_stored_name(session: Session, stored_name: str) -> Optional[FileUploads]:
    """
    通过存储名称获取文件上传记录

    Args:
        session: 数据库会话
        stored_name: 存储后的文件名

    Returns:
        文件上传记录模型实例，如果不存在则返回None
    """
    statement = select(FileUploads).where(FileUploads.stored_name == stored_name)
    result = session.exec(statement).first()
    return result


def search_file_uploads(session: Session, search_params: Dict[str, Any]) -> Sequence[FileUploads]:
    """
    根据提供的参数搜索文件上传记录，使用FileUploads中定义的like_search_fields
    来决定查询方式

    Args:
        session: 数据库会话
        search_params: 搜索参数字典，键为FileUploads的字段名，值为搜索条件

    Returns:
        符合条件的FileUploads列表
    """
    statement = select(FileUploads)

    # 获取FileUploads类的所有字段名
    file_upload_fields = [column.name for column in FileUploads.__table__.columns]

    # 动态构建查询条件
    for field, value in search_params.items():
        if field in file_upload_fields and value is not None:
            # 根据字段是否在like_search_fields中决定查询方式
            if field in FileUploads.like_search_fields and isinstance(value, str):
                statement = statement.where(getattr(FileUploads, field).like(f"%{value}%"))
            else:
                # 对于其他字段，使用精确匹配
                statement = statement.where(getattr(FileUploads, field) == value)

    # 执行查询
    results = session.exec(statement).all()
    return results


def update_file_upload(session: Session, file_id: str, update_data: Dict[str, Any]) -> Optional[FileUploads]:
    """
    更新文件上传记录

    Args:
        session: 数据库会话
        file_id: 文件ID
        update_data: 要更新的数据字典

    Returns:
        更新后的文件上传记录模型实例，如果不存在则返回None
    """
    # 先获取文件上传记录
    db_file = get_file_upload_by_id(session, file_id)
    if not db_file:
        return None

    # 更新字段
    for field, value in update_data.items():
        if hasattr(db_file, field):
            setattr(db_file, field, value)

    session.add(db_file)
    session.commit()
    session.refresh(db_file)
    return db_file


def delete_file_upload(session: Session, file_id: str) -> bool:
    """
    删除文件上传记录

    Args:
        session: 数据库会话
        file_id: 文件ID

    Returns:
        是否成功删除
    """
    db_file = get_file_upload_by_id(session, file_id)
    if not db_file:
        return False

    session.delete(db_file)
    session.commit()
    return True


def get_file_uploads_by_status(session: Session, status: str) -> Sequence[FileUploads]:
    """
    通过状态获取文件上传记录列表

    Args:
        session: 数据库会话
        status: 文件状态 (1-正常, 0-已删除)

    Returns:
        文件上传记录模型实例列表
    """
    statement = select(FileUploads).where(FileUploads.status == status)
    results = session.exec(statement).all()
    return results


def get_file_uploads_by_original_name(session: Session, original_name: str) -> Sequence[FileUploads]:
    """
    通过原始文件名获取文件上传记录列表

    Args:
        session: 数据库会话
        original_name: 原始文件名

    Returns:
        文件上传记录模型实例列表
    """
    statement = select(FileUploads).where(FileUploads.original_name == original_name)
    results = session.exec(statement).all()
    return results


def batch_create_file_uploads(session: Session, file_uploads: List[FileUploads]) -> List[FileUploads]:
    """
    批量创建文件上传记录

    Args:
        session: 数据库会话
        file_uploads: 文件上传记录模型实例列表

    Returns:
        创建后的文件上传记录模型实例列表
    """
    session.add_all(file_uploads)
    session.commit()
    for file_upload in file_uploads:
        session.refresh(file_upload)
    return file_uploads


def get_all_file_uploads(session: Session) -> Sequence[FileUploads]:
    """
    获取所有文件上传记录

    Args:
        session: 数据库会话

    Returns:
        所有文件上传记录模型实例列表
    """
    statement = select(FileUploads)
    results = session.exec(statement).all()
    return results


def count_file_uploads(session: Session) -> int:
    """
    统计文件上传记录数量

    Args:
        session: 数据库会话

    Returns:
        文件上传记录的数量
    """
    statement = select(FileUploads)
    results = session.exec(statement).all()
    return len(results)


def get_recent_file_uploads(session: Session, limit: int = 10) -> Sequence[FileUploads]:
    """
    获取最近上传的文件记录

    Args:
        session: 数据库会话
        limit: 限制返回的记录数量

    Returns:
        文件上传记录模型实例列表
    """
    statement = select(FileUploads).order_by(FileUploads.upload_time.desc()).limit(limit)
    results = session.exec(statement).all()
    return results


def logical_delete_file_upload(session: Session, file_id: str) -> Optional[FileUploads]:
    """
    逻辑删除文件上传记录（将状态设置为0）

    Args:
        session: 数据库会话
        file_id: 文件ID

    Returns:
        更新后的文件上传记录模型实例，如果不存在则返回None
    """
    return update_file_upload(session, file_id, {"status": "0"})


def get_file_uploads_by_file_type(session: Session, file_type: str) -> Sequence[FileUploads]:
    """
    通过文件类型获取文件上传记录列表

    Args:
        session: 数据库会话
        file_type: 文件MIME类型

    Returns:
        文件上传记录模型实例列表
    """
    statement = select(FileUploads).where(FileUploads.file_type.like(f"%{file_type}%"))
    results = session.exec(statement).all()
    return results
