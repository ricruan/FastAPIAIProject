from string import Template

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

    @classmethod
    def to_messages(cls, prompt: str, query: str):
        return [cls.as_system(prompt), cls.as_user(query)]


    def template_handle(self,variable:dict):
        template =  Template(self.content)
        self.content = template.substitute(**variable)
        return self