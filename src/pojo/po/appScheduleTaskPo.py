from datetime import datetime
from enum import Enum
from typing import Optional, ClassVar, List, Any

from sqlalchemy import Text
from sqlmodel import SQLModel, Field, Index


class TaskType(str, Enum):
    """
    任务类型枚举
    """
    SCHEDULE = "0"  # 日程
    TASK = "1"  # 任务
    # 可根据需要补充其他类型


class TaskSource(str, Enum):
    """
    数据来源枚举
    """
    WEWORK = "0"  # 企微
    FEISHU = "1"  # 飞书
    MANUAL = "2"  # 手动录入
    OTHER = "3"  # 其他
    STONE = "4"
    # 可根据需要补充其他来源


class TaskStatus(str, Enum):
    """
    任务状态枚举
    """
    INCOMPLETE = "0"  # 未完成
    COMPLETE = "1"  # 已完成


class ImportanceFlag(str, Enum):
    """
    重要性标志枚举
    """
    NOT_IMPORTANT = "0"  # 否
    IMPORTANT = "1"  # 是


class UrgencyFlag(str, Enum):
    """
    紧急性标志枚举
    """
    NOT_URGENT = "0"  # 否
    URGENT = "1"  # 是


class AppScheduleTask(SQLModel, table=True):
    """
    日程及任务表模型
    """
    __tablename__ = "app_schedule_task"

    # 定义表级参数，包括表注释
    __table_args__ = {
        "comment": "日程及任务表",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci"
    }

    # 定义应该使用like查询的字段列表
    like_search_fields: ClassVar[List[str]] = [
        "user_name", "content"
    ]
    
    def convert_enum_values(self, to_string: bool = True) -> "AppScheduleTask":
        """
        转换枚举类型属性的值，可以在字符数字值和枚举对象之间双向转换
        
        Args:
            to_string: 转换方向，True表示将枚举对象转换为字符数字值，False表示将字符数字值转换为枚举对象
            
        Returns:
            转换后的AppScheduleTask对象（self）
        """
        # 定义需要处理的枚举类型属性及其对应的枚举类
        enum_fields = {
            'type': TaskType,
            'status': TaskStatus,
            'source': TaskSource,
            'is_urgent': UrgencyFlag,
            'is_important': ImportanceFlag
        }
        
        for field_name, enum_class in enum_fields.items():
            field_value = getattr(self, field_name, None)
            
            # 跳过None值
            if field_value is None:
                continue
                
            if to_string:
                # 将枚举对象转换为字符数字值
                if isinstance(field_value, enum_class):
                    # 枚举对象已经是字符串形式，直接获取其值
                    setattr(self, field_name, field_value.value)
            else:
                # 将字符数字值转换为枚举对象
                if isinstance(field_value, str):
                    # 查找匹配的枚举对象
                    for enum_item in enum_class:
                        if enum_item.value == field_value:
                            setattr(self, field_name, enum_item)
                            break
        
        return self


    id: str = Field(
        primary_key=True,
        max_length=36,
        description="唯一标识(uuid)",
        sa_column_kwargs={"comment": "唯一标识(uuid)"}
    )

    user_id: Optional[str] = Field(
        default=None,
        max_length=64,
        index=True,
        description="创建人用户ID",
        sa_column_kwargs={"comment": "创建人用户ID"}
    )

    user_name: Optional[str] = Field(
        max_length=64,
        description="创建人名称",
        sa_column_kwargs={"comment": "创建人名称"}
    )

    type: str = Field(
        max_length=10,
        index=True,
        description="类型(0:日程, 1:任务)",
        sa_column_kwargs={"comment": "类型(0:日程, 1:任务)"}
    )

    start_time: Optional[datetime] = Field(
        default=None,
        description="开始时间",
        sa_column_kwargs={"comment": "开始时间"}
    )

    end_time: Optional[datetime] = Field(
        default=None,
        description="结束时间",
        sa_column_kwargs={"comment": "结束时间"}
    )

    create_time: Optional[datetime] = Field(
        description="创建时间",
        sa_column_kwargs={"comment": "创建时间"}
    )

    complete_time: Optional[datetime] = Field(
        default=None,
        description="完成时间",
        sa_column_kwargs={"comment": "完成时间"}
    )

    content: str = Field(
        sa_type=Text,
        description="内容",
        sa_column_kwargs={"comment": "内容"}
    )

    status: str = Field(
        max_length=20,
        index=True,
        description="状态(0:未完成, 1:已完成)",
        sa_column_kwargs={"comment": "状态(0:未完成, 1:已完成)"}
    )

    source: Optional[str] = Field(
        default=None,
        max_length=20,
        description="数据来源(企微、飞书、手动录入、其他)",
        sa_column_kwargs={"comment": "数据来源(企微、飞书、手动录入、其他)"}
    )

    is_urgent: Optional[str] = Field(
        default=None,
        max_length=10,
        description="是否紧急(0:否, 1:是)",
        sa_column_kwargs={"comment": "是否紧急(0:否, 1:是)"}
    )

    is_important: Optional[str] = Field(
        default=None,
        max_length=10,
        description="是否重要(0:否, 1:是)",
        sa_column_kwargs={"comment": "是否重要(0:否, 1:是)"}
    )

    attachment: str = Field(
        default=None,
        description="附件,对应上传文件ID或url",
        sa_column_kwargs={"comment": "附件,对应上传文件ID或url"}
    )

    # 定义索引
    class Config:
        indexes = [
            Index("idx_user", "user_id"),
            Index("idx_type", "type"),
            Index("idx_create_time", "create_time"),
            Index("idx_status", "status")
        ]
