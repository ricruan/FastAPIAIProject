from datetime import datetime
from typing import Optional, ClassVar, List

from sqlmodel import SQLModel, Field, Index


class FileUploads(SQLModel, table=True):
    """
    文件上传记录表模型
    """
    __tablename__ = "file_uploads"

    # 定义表级参数，包括表注释
    __table_args__ = {
        "comment": "文件上传记录表",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    # 定义应该使用like查询的字段列表
    like_search_fields: ClassVar[List[str]] = [
        "original_name", "file_type"
    ]

    id: str = Field(
        primary_key=True,
        max_length=32,
        description="文件唯一标识(UUID)",
        sa_column_kwargs={"comment": "文件唯一标识(UUID)"}
    )

    original_name: str = Field(
        max_length=255,
        description="原始文件名",
        sa_column_kwargs={"comment": "原始文件名"}
    )

    stored_name: str = Field(
        max_length=255,
        description="存储后的文件名(含UUID和扩展名)",
        sa_column_kwargs={"comment": "存储后的文件名(含UUID和扩展名)"}
    )

    file_path: str = Field(
        max_length=512,
        description="文件存储路径(相对路径)",
        sa_column_kwargs={"comment": "文件存储路径(相对路径)"}
    )

    file_size: Optional[int] = Field(
        default=None,
        description="文件大小(字节)",
        sa_column_kwargs={"comment": "文件大小(字节)"}
    )

    file_type: Optional[str] = Field(
        default=None,
        max_length=100,
        description="文件MIME类型",
        sa_column_kwargs={"comment": "文件MIME类型"}
    )

    upload_time: datetime = Field(
        default_factory=datetime.now,
        description="上传时间",
        sa_column_kwargs={"comment": "上传时间"}
    )

    upload_ip: Optional[str] = Field(
        default=None,
        max_length=50,
        description="上传者IP地址",
        sa_column_kwargs={"comment": "上传者IP地址"}
    )

    status: str = Field(
        default="1",
        description="状态:1-正常,0-已删除",
        sa_column_kwargs={"comment": "状态:1-正常,0-已删除"}
    )

    # 定义索引
    class Config:
        indexes = [
            Index("idx_stored_name", "stored_name"),
            Index("idx_original_name", "original_name")
        ]
