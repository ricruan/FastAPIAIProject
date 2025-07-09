from pydantic import BaseModel

from src.ai.enum.aiEnum import AIPromptRole


class PromptContent(BaseModel):
    role: str
    content: str

    @classmethod
    def as_system(cls,content:str):
        return cls(role=AIPromptRole.SYSTEM.value,content=content)

    @classmethod
    def as_user(cls,content:str):
        return cls(role=AIPromptRole.USER.value,content=content)

    @classmethod
    def as_assistant(cls,content:str):
        return cls(role=AIPromptRole.ASSISTANT.value,content=content)