from pydantic import BaseModel, Field


class PipoFile(BaseModel):
    ids: str = Field(..., description="文件ID", example="1")
    user: str = Field(..., description="用户ID", example="123")
    query: str = Field(..., description="用户问题", example="下载刚刚创建订单的合同")
    session_id: str = Field(..., description="会话ID", example="")
    token: str =Field(..., description="ERP token", example="")
    type: str = Field("PO",description="类型 PO/PI", example="PO")
