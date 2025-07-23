from typing import Optional

from pydantic import BaseModel,Field


class DifyModel(BaseModel):
    query: str = Field("", description="用户问题", example="你好")
    conversation_id: Optional[str] = Field("", description="Dify会话ID 可不填", example="")
    response_mode: str  = Field("streaming", description="响应模式", example="streaming")
    user: str = Field(..., description="用户ID", example="dify_test")
    inputs: dict = Field({}, description="额外入参", example="{}")

class DifyYpjInputs(BaseModel):
    houses_id: str = Field(..., description="房屋ID", example="11287")


class DifyYpj(DifyModel):
    inputs: DifyYpjInputs


#  历史遗留产物 👇
class DifyJxm(BaseModel):
    """Dify Jxm VO对象"""
    query: str  # 用户查询内容
    user_id: str  # 用户ID
    token: str  # 用户token
    nickname: str  # 用户昵称
    response_mode: str  # 响应模式
    conversation_id: Optional[str]  # 可选会话ID
    api_code: str  # API编码

    class Config:
        json_schema_extra = {
            "example": {
                "query": "你好",
                "user_id": "123",
                "token": "123",
                "nickname": "123",
                "response_mode": "blocking",
                "conversation_id": "",
                "api_code": "jixiaomei",
            }
        }


    def to_jxm(self) -> dict:
        """
        转换为JXM对话流的入参
        :return:
        """
        return {
            "inputs": {
                "userid":self.user_id,
                "token":self.token,
                "nickname":self.nickname,
            },
            "query": self.query,
            "response_mode": self.response_mode,
            "conversation_id": self.conversation_id,
            "user": self.user_id
        }

