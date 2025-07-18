import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, ClassVar, List

from sqlalchemy import Text
from sqlmodel import SQLModel, Field, Index, text, ForeignKey

from src.pojo.vo.difyResponse import DifyResponse
from src.pojo.vo.jixiaomeiVo import DifyJxm
from src.utils.dataUtils import dict_list_2_json, dict_2_json, is_valid_json

logger = logging.getLogger(__name__)

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
        sa_type=Text,
        sa_column_kwargs={"comment": "接口原始入参"}
    )

    api_output: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="接口原始出参",
        sa_column_kwargs={"comment": "接口原始出参"}
    )

    user_question: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="对话用户问题",
        sa_column_kwargs={"comment": "对话用户问题"}
    )

    final_response: Optional[str] = Field(
        default=None,
        sa_type=Text,
        description="对话最终返回",
        sa_column_kwargs={"comment": "对话最终返回"}
    )

    process_log: Optional[str] = Field(
        default=None,
        sa_type=Text,
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
        self.final_response = dict_list_2_json([DifyResponse.not_found_data().model_dump()])


    def when_success(self,output: dict|str, response: DifyResponse|list|str):
        """
        当成功时,修改自身部分属性
        :param output: api的返回结果 dict类型
        :param response: 最终的返回体
        :return: void
        """
        self.finish_time = datetime.now()
        if isinstance(output,str):
            self.api_output = output
        else :
            self.api_output = dict_2_json(output)
        self.status = "200"
        if isinstance(response, list):
            self.final_response = dict_list_2_json(response)
        elif  isinstance(response, DifyResponse):
            self.final_response = dict_list_2_json([response.model_dump()])
        else :
            self.final_response = response

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

    def get_answer_from_fp(self):
        """
        从final_response中获取回答内容
        :return:
        """
        try:
            if not is_valid_json(self.final_response):
                return None
            json_data = json.loads(self.final_response)
            if not isinstance(json_data, list):
                return None

            return "".join([item['data'] for item in list(json_data)])
        except Exception as e :
            logger.error("获取会话详情的AI回答时发生异常 \n" + e)
            return None



    # 定义索引和外键约束
    class Config:
        indexes = [
            Index("idx_session_id", "session_id"),
            Index("idx_create_time", "create_time")
        ]


class DialogCarrierEnum(Enum):
    DIFY_ERP = ("dify_erp", "来源于Dify的Erp系统")

    def __init__(self, value, description):
        self._value_ = value  # 必须定义 _value_，这是枚举的实际值
        self.description = description  # 自定义属性