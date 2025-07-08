from datetime import datetime
from typing import Optional, ClassVar, List

from sqlalchemy import Text
from sqlmodel import SQLModel, Field, Index

class Code(SQLModel, table=True):
    """
    编码表模型
    """
    __tablename__ = "code"

    # 定义表级参数，包括表注释
    __table_args__ = {
        "comment": "编码表",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    # 定义应该使用like查询的字段列表
    like_search_fields: ClassVar[List[str]] = [
        "code", "value", "desc"
    ]

    id: str = Field(
        primary_key=True,
        max_length=36,
        description="唯一标识，存储UUID",
        sa_column_kwargs={"comment": "唯一标识，存储UUID"}
    )

    code: str = Field(
        max_length=64,
        unique=True,
        description="编码",
        sa_column_kwargs={"comment": "编码"}
    )

    value: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="码值",
        sa_column_kwargs={"comment": "码值"}
    )

    desc: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="描述",
        sa_column_kwargs={"comment": "描述"}
    )

    type: Optional[str] = Field(
        default=None,
        max_length=64,
        index=True,
        description="类型",
        sa_column_kwargs={"comment": "类型"}
    )

    mapper: Optional[str] = Field(
        default=None,
        max_length=64,
        description="映射实体",
        sa_column_kwargs={"comment": "映射实体"}
    )

    parent_code: Optional[str] = Field(
        default=None,
        max_length=64,
        index=True,
        description="上级编码",
        sa_column_kwargs={"comment": "上级编码"}
    )

    create_time: Optional[datetime] = Field(
        default=None,
        description="创建时间",
        sa_column_kwargs={"comment": "创建时间"}
    )

    update_time: Optional[datetime] = Field(
        default=None,
        description="更新时间",
        sa_column_kwargs={"comment": "更新时间"}
    )

    # 定义索引和唯一约束
    class Config:
        arbitrary_types_allowed = True
        indexes = [
            Index("idx_parent_code", "parent_code"),
            Index("idx_type", "type")
        ]
