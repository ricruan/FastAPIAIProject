from datetime import datetime
from typing import Optional, ClassVar, List
from sqlmodel import SQLModel, Field, Index, text
from sqlalchemy import Text


class APIInfo(SQLModel, table=True):
    """
    API信息表模型
    """
    __tablename__ = "api_info"
    
    # 定义表级参数，包括表注释
    __table_args__ = {
        "comment": "API信息表",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }
    
    # 定义应该使用like查询的字段列表
    like_search_fields: ClassVar[List[str]] = [
        "api_name", "api_url", "api_desc", "api_param_struct", 
        "api_param_desc", "api_param_template"
    ]
    



    id: Optional[str] = Field(
        default=None,
        primary_key=True,
        description="唯一标识",
        sa_column_kwargs={"comment": "唯一标识"}
    )

    type_code: Optional[str] = Field(
        max_length=64,
        description="API类型编码",
        sa_column_kwargs={"comment": "API类型编码"}
    )

    api_code: str = Field(
        max_length=64,
        index=True,
        description="API唯一编码",
        sa_column_kwargs={"comment": "API唯一编码"}
    )

    api_name: str = Field(
        max_length=128,
        description="API名称",
        sa_column_kwargs={"comment": "API名称"}
    )

    api_url: Optional[str] = Field(
        max_length=512,
        description="API请求地址",
        sa_column_kwargs={"comment": "API请求地址"}
    )

    api_header: Optional[str] = Field(
        sa_type=Text,
        description="API请求头",
        sa_column_kwargs={"comment": "API请求头"}
    )

    api_desc: Optional[str] = Field(
        sa_type=Text,
        description="API请求地址",
        sa_column_kwargs={"comment": "API描述"}
    )


    api_param_struct: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="API参数结构",
        sa_column_kwargs={"comment": "API参数结构"}
    )

    api_param_desc: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="API参数描述",
        sa_column_kwargs={"comment": "API参数描述"}
    )

    api_param_template: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="API参数示例",
        sa_column_kwargs={"comment": "API参数示例"}
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


