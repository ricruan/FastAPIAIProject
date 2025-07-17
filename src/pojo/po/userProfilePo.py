import uuid
from datetime import datetime
from typing import Optional, ClassVar, List

from sqlalchemy import Text
from sqlmodel import SQLModel, Field, Index

class UserProfile(SQLModel, table=True):
    """
    用户画像表模型
    """
    __tablename__ = "user_profile"

    # 定义表级参数，包括表注释
    __table_args__ = {
        "comment": "用户画像表",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    # 定义应该使用like查询的字段列表
    like_search_fields: ClassVar[List[str]] = [
        "user_info", "language_style", "preferred_llm_style",
        "disliked_llm_style", "personality_traits", "user_summary"
    ]

    id: str = Field(
        primary_key=True,
        max_length=255,
        description="唯一标识",
        sa_column_kwargs={"comment": "唯一标识"}
    )

    user_id: str = Field(
        max_length=255,
        unique=True,
        description="用户id",
        sa_column_kwargs={"comment": "用户id"}
    )

    user_info: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="用户详细信息",
        sa_column_kwargs={"comment": "用户详细信息"}
    )

    source: Optional[str] = Field(
        default=None,
        max_length=255,
        description="用户来源，从何处录入到的用户",
        sa_column_kwargs={"comment": "用户来源，从何处录入到的用户"}
    )

    create_time: datetime = Field(
        description="录入时间",
        sa_column_kwargs={"comment": "录入时间"}
    )

    update_time: datetime = Field(
        description="最后更新时间",
        sa_column_kwargs={"comment": "最后更新时间"}
    )

    language_style: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="用户的语言风格",
        sa_column_kwargs={"comment": "用户的语言风格"}
    )

    preferred_llm_style: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="期望llm以何种形式回复",
        sa_column_kwargs={"comment": "期望llm以何种形式回复"}
    )

    disliked_llm_style: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="抵触llm以何种形式回复",
        sa_column_kwargs={"comment": "抵触llm以何种形式回复"}
    )

    personality_traits: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="性格特征，LLM基于历史对话记录总结",
        sa_column_kwargs={"comment": "性格特征，LLM基于历史对话记录总结"}
    )

    behavior_profile: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="行为画像，记录用户各类行为的次数",
        sa_column_kwargs={"comment": "行为画像，记录用户各类行为的次数"}
    )

    interpersonal_profile: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="人际关系画像，记录用户在对话中提到的其他人的次数和态度",
        sa_column_kwargs={"comment": "人际关系画像，记录用户在对话中提到的其他人的次数和态度"}
    )

    key_events: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="重要事件，基于历史对话记录提取重要事件信息",
        sa_column_kwargs={"comment": "重要事件，基于历史对话记录提取重要事件信息"}
    )

    preference_questions: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="偏好问题推荐，根据用户习惯推荐五个用户可能想问的问题",
        sa_column_kwargs={"comment": "偏好问题推荐，根据用户习惯推荐五个用户可能想问的问题"}
    )

    topic_preferences: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="偏好话题标签",
        sa_column_kwargs={"comment": "偏好话题标签"}
    )

    sentiment_trend: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="情感趋势",
        sa_column_kwargs={"comment": "情感趋势"}
    )

    user_summary: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="用户总结，基于前面的字段，总结成一段简短的文本，作为提示词给LLM",
        sa_column_kwargs={"comment": "用户总结，基于前面的字段，总结成一段简短的文本，作为提示词给LLM"}
    )

    last_handle_session_id: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="上一次分析截止的会话详情id",
        sa_column_kwargs={"comment": "上一次分析截止的会话详情id"}
    )

    @classmethod
    def get_profile(cls,user_id: str,source: str):
        return cls(user_id = user_id,
                   source = source,
                   id = uuid.uuid4().hex,
                   create_time = datetime.now(),
                   update_time = datetime.now(),)

    # 定义索引
    class Config:
        indexes = [
            Index("idx_user_id", "user_id")
        ]
