import json
from datetime import datetime
from string import Template
from typing import Optional, ClassVar, List
from enum import Enum

from sqlalchemy import Text
from sqlmodel import SQLModel, Field, Index

from src.ai.pojo.promptBo import PromptContent
from src.exception.aiException import AIException
from src.utils.dataUtils import is_valid_json


class PromptCodeEnum(str, Enum):
    """
    提示词编码枚举
    
    每个枚举值包含两个属性：
    - value: 提示词编码
    - desc: 提示词描述
    """
    
    # 示例枚举值
    QUESTION_RECOMMEND_PLUS_PROMPT = "question_recommend_plus_prompt", "用户画像问题推荐提示词"
    PERSONALITY_TRAITS_PROMPT = "personality_traits_prompt", "用户画像性格分析提示词"
    ERROR_HANDLING = "error_handling", "错误处理"
    
    # 可以根据需要添加更多枚举值
    
    def __new__(cls, value, desc):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.desc = desc
        return obj
    
    @classmethod
    def get_desc(cls, value):
        """
        根据编码获取描述
        
        Args:
            value: 提示词编码
            
        Returns:
            提示词描述，如果找不到则返回None
        """
        for item in cls:
            if item.value == value:
                return item.desc
        return None
    
    @classmethod
    def get_all_codes(cls):
        """
        获取所有提示词编码
        
        Returns:
            所有提示词编码的列表
        """
        return [item.value for item in cls]

class Prompt(SQLModel, table=True):
    """
    提示词表模型
    """
    __tablename__ = "prompts"

    # 定义表级参数，包括表注释
    __table_args__ = {
        "comment": "提示词表",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    # 定义应该使用like查询的字段列表
    like_search_fields: ClassVar[List[str]] = [
        "name", "content", "description", "category"
    ]

    id: str = Field(
        primary_key=True,
        max_length=36,
        description="唯一标识",
        sa_column_kwargs={"comment": "唯一标识"}
    )

    code: str = Field(
        max_length=50,
        unique=True,
        description="提示词编码",
        sa_column_kwargs={"comment": "提示词编码"}
    )

    name: str = Field(
        max_length=100,
        description="提示词名称",
        sa_column_kwargs={"comment": "提示词名称"}
    )

    content: str = Field(
        sa_type=Text,
        description="提示词内容",
        sa_column_kwargs={"comment": "提示词内容"}
    )

    description: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="提示词简介",
        sa_column_kwargs={"comment": "提示词简介"}
    )

    placeholder_template: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="占位符json模板",
        sa_column_kwargs={"comment": "占位符json模板"}
    )

    user_prompt: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="用户提示词",
        sa_column_kwargs={"comment": "用户提示词"}
    )

    created_at: datetime = Field(
        default_factory=datetime.now,
        description="创建时间",
        sa_column_kwargs={"comment": "创建时间"}
    )

    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="更新时间",
        sa_column_kwargs={"comment": "更新时间"}
    )

    model_type: Optional[str] = Field(
        default=None,
        max_length=50,
        description="适配模型类型",
        sa_column_kwargs={"comment": "适配模型类型"}
    )

    agent_code: Optional[str] = Field(
        default=None,
        max_length=50,
        description="适配Agent编码",
        sa_column_kwargs={"comment": "适配Agent编码"}
    )

    usage_count: int = Field(
        default=0,
        description="使用次数",
        sa_column_kwargs={"comment": "使用次数"}
    )

    last_called_at: Optional[datetime] = Field(
        default=None,
        description="上次调用时间",
        sa_column_kwargs={"comment": "上次调用时间"}
    )

    status: str = Field(
        default="1",
        max_length=20,
        description="状态（0=禁用, 1=启用, 2=待审核）",
        sa_column_kwargs={"comment": "状态（0=禁用, 1=启用, 2=待审核）"}
    )

    creator_id: Optional[str] = Field(
        default=None,
        max_length=36,
        description="创建人ID",
        sa_column_kwargs={"comment": "创建人ID"}
    )

    modifier_id: Optional[str] = Field(
        default=None,
        max_length=36,
        description="最后修改人ID",
        sa_column_kwargs={"comment": "最后修改人ID"}
    )

    category: Optional[str] = Field(
        default=None,
        max_length=50,
        description="提示词分类",
        sa_column_kwargs={"comment": "提示词分类"}
    )

    # 定义索引
    class Config:
        indexes = [
            Index("idx_model_type", "model_type"),
            Index("idx_agent_code", "agent_code"),
            Index("idx_category", "category"),
            Index("idx_status", "status")
        ]

    def render_prompt(self,variable :dict) -> str:
        """
        使用占位符模板和传入的字典渲染提示词中的变量
        :param variable: 传入的变量字典
        :return: 渲染后的提示词
        """
        template = Template(self.content)
        if not is_valid_json(self.placeholder_template):
            raise AIException.quick_raise(f"提示词{self.name} {self.code} 的变量模板json转化失败,请维护对应数据")
        return template.substitute({**json.loads(self.placeholder_template),**variable})

    def get_messages(self,variable :dict):
        if not self.user_prompt:
            raise AIException.quick_raise(f"{self.code} {self.name}提示词缺失默认用户类型的提示词")
        prompt_str = self.render_prompt(variable)
        return PromptContent.to_messages(prompt=prompt_str, query=self.user_prompt)

