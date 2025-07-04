from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional

class AIException(Exception):
    """基础AI异常类"""
    def __init__(self, code: int, message: str, detail: Optional[str] = None):
        self.code = code
        self.message = message
        self.detail = detail

    @classmethod
    def quick_raise(cls,message: str, code: int=500, detail: Optional[str] = None):
        raise cls(code, message, detail)

