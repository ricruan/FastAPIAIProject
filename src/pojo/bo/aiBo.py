from pydantic import BaseModel, Field

from src.ai.pojo.promptBo import PromptContent


class ModelConfig(BaseModel):
    model: str = Field("deepseek-chat", description="模型名称", example="deepseek-chat")
    stream: bool = Field(True, description="是否流式响应", example=True)
    messages: list[PromptContent] | None = Field(None, description="提示词信息", example="[]")


class Query(BaseModel):
    query: str = Field(..., description="用户问题", example="你好")


class GetJsonModel(BaseModel):
    query: str = Field(..., description="用户问题", example="你好")
    model: str = Field("deepseek-chat", description="调用模型", example="deepseek-chat")
    api_code: str = Field(..., description="API编码", example="test")


class NormalLLMRequestModel(Query, ModelConfig):
    pass