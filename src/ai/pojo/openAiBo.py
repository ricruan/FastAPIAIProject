from pydantic import BaseModel, Field


class OpenAiParam(BaseModel):
    messages: list = Field(None, description="消息", example="")
    stream: bool = Field(False, description="流式响应", example=False)
    model: str = Field(None, description="模型", example="qwen-plus")
    api_key: str = Field(None, description="API KEY", example="cs-xxx222333")
    base_url: str = Field(None, description="基础URL", example="http:/")
    temperature: float = Field(1.0, description="温度", example=1.0)



class QwenOpenAiParm(OpenAiParam):
    enable_search: bool = Field(False, description="是否启用", example=False)