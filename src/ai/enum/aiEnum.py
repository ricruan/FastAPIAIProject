from enum import Enum


class AIPromptRole(str, Enum):
    """
    AI 提示词中的角色类型枚举（Role Types in AI Prompts）。
    定义常见的 AI 角色分类，用于提示词工程（Prompt Engineering）。
    """
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"