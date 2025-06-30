import json
import uuid
from datetime import datetime
from typing import Optional, ClassVar, List

from sqlmodel import SQLModel, Field, Index, text, ForeignKey

from src.pojo.vo.difyResponse import DifyResponse
from src.pojo.vo.jixiaomeiVo import DifyJxm


class SessionDetail(SQLModel, table=True):
    """
    会话详情表模型
    """
    __tablename__ = "session_detail"

    # 定义表级参数，包括表注释
    __table_args__ = {
        "comment": "会话详情表",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    # 定义应该使用like查询的字段列表
    like_search_fields: ClassVar[List[str]] = [
        "dialog_carrier", "api_input", "api_output",
        "user_question", "final_response", "process_log"
    ]

    id: str = Field(
        primary_key=True,
        max_length=64,
        description="唯一标识",
        sa_column_kwargs={"comment": "唯一标识"}
    )

    session_id: str = Field(
        max_length=64,
        foreign_key="session.id",
        description="会话主题id",
        sa_column_kwargs={"comment": "会话主题id"}
    )

    dialog_carrier: Optional[str] = Field(
        default=None,
        max_length=255,
        description="对话载体",
        sa_column_kwargs={"comment": "对话载体"}
    )

    api_input: Optional[str] = Field(
        default=None,
        description="接口原始入参",
        sa_column_kwargs={"comment": "接口原始入参"}
    )

    api_output: Optional[str] = Field(
        default=None,
        description="接口原始出参",
        sa_column_kwargs={"comment": "接口原始出参"}
    )

    user_question: Optional[str] = Field(
        default=None,
        description="对话用户问题",
        sa_column_kwargs={"comment": "对话用户问题"}
    )

    final_response: Optional[str] = Field(
        default=None,
        description="对话最终返回",
        sa_column_kwargs={"comment": "对话最终返回"}
    )

    process_log: Optional[str] = Field(
        default=None,
        description="会话流程日志",
        sa_column_kwargs={"comment": "会话流程日志"}
    )

    model: Optional[str] = Field(
        default=None,
        max_length=100,
        description="模型",
        sa_column_kwargs={"comment": "模型"}
    )

    response_mode: Optional[str] = Field(
        default=None,
        max_length=100,
        description="响应模式",
        sa_column_kwargs={"comment": "响应模式"}
    )

    agent: Optional[str] = Field(
        default=None,
        max_length=100,
        description="智能体",
        sa_column_kwargs={"comment": "智能体"}
    )

    status: Optional[str] = Field(
        default=None,
        max_length=12,
        description="会话状态",
        sa_column_kwargs={"comment": "会话状态"}
    )

    create_time: datetime = Field(
        description="创建时间",
        sa_column_kwargs={"comment": "创建时间"}
    )

    finish_time: datetime = Field(
        description="结束时间",
        sa_column_kwargs={"comment": "结束时间"}
    )

    def handle_dict(self):
        """
        处理字典字段值
        :return:
        """
        if isinstance(self.api_output, dict):
            self.api_output = json.dumps(self.api_output)
        if isinstance(self.api_input, dict):
            self.api_input = json.dumps(self.api_input)
        if self.id is None:
            self.id = uuid.uuid4().hex

    def when_error(self,reason: str):
        """
        当失败时
        :return:
        """
        self.finish_time = datetime.now()
        self.api_output = reason
        self.status = "500"
        self.final_response = DifyResponse.not_found_data()


    def when_success(self, response: DifyResponse):
        """
        当成功时
        :return:
        """
        self.finish_time = datetime.now()
        self.api_output = str(response.model_dump())
        self.status = "200"
        self.final_response = str(response.model_dump())

    @classmethod
    def from_dify_jxm(cls, jxm: DifyJxm) -> "SessionDetail":
        """
         根据 DifyJxm 的实例 转化一个sessionDetail 的实例
        :param jxm: DifyJxm类实例
        :return: SessionDetail 实例
        """
        return cls(
            user_id=jxm.user_id,
            token=jxm.token,
            response_mode=jxm.response_mode,
            user_question=jxm.query,
            create_time=datetime.now()
        )



    # 定义索引和外键约束
    class Config:
        indexes = [
            Index("idx_session_id", "session_id"),
            Index("idx_create_time", "create_time")
        ]
