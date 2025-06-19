from datetime import datetime
from typing import Optional, ClassVar, List
from sqlmodel import SQLModel, Field, Index, text



class APIInfo(SQLModel, table=True):
    """
    API信息表模型
    """
    __tablename__ = "api_info"
    
    # 定义应该使用like查询的字段列表
    like_search_fields: ClassVar[List[str]] = [
        "api_name", "api_url", "api_desc", "api_param_struct", 
        "api_param_desc", "api_param_template"
    ]
    
    # 定义应该使用精确匹配的字段列表
    exact_search_fields: ClassVar[List[str]] = [
        "id", "api_code", "create_time", "update_time"
    ]


    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="唯一标识",
    )

    type_code: str = Field(
        max_length=64,
        description="API类型编码",
    )

    api_code: str = Field(
        max_length=64,
        index=True,
        description="API唯一编码",
    )

    api_name: str = Field(
        max_length=128,
        description="API名称",
    )

    api_url: str = Field(
        max_length=512,
        description="API请求地址",
    )

    api_desc: str = Field(
        max_length=512,
        description="API请求地址",
    )


    api_param_struct: Optional[str] = Field(
        default=None,
        description="API参数结构",
    )

    api_param_desc: Optional[str] = Field(
        default=None,
        description="API参数描述",
    )

    api_param_template: Optional[str] = Field(
        default=None,
        description="API参数示例",
    )

    create_time: Optional[datetime] = Field(
        default=None,
        description="创建时间",
    )

    update_time: Optional[datetime] = Field(
        default=None,
        description="更新时间",
    )


