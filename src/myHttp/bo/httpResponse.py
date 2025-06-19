from typing import Any, Optional, TypeVar, Generic
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse

T = TypeVar('T')

class HttpResponseModel(BaseModel, Generic[T]):
    """
    HTTP响应模型，用于FastAPI的响应文档生成
    """
    code: int = Field(..., description="HTTP状态码")
    data: Optional[T] = Field(None, description="响应数据")
    msg: str = Field("", description="响应消息")

class HttpResponse(Generic[T]):
    """
    HTTP响应包装类
    
    属性:
        code: HTTP状态码
        data: 响应数据
        msg: 响应消息
    """
    
    def __init__(self, code: int, data: Optional[T] = None, msg: str = ""):
        self.code = code
        self.data = data
        self.msg = msg
    
    @classmethod
    def success(cls, data: Optional[T] = None, msg: str = "success") -> 'HttpResponseModel[T]':
        """
        创建一个成功的响应
        
        参数:
            data: 响应数据
            msg: 响应消息，默认为"success"
            
        返回:
            HttpResponse: 成功的响应对象，状态码为200
        """
        return cls(200, data, msg).model()
    
    @classmethod
    def error(cls, msg: str = "error", code: int = 500, data: Optional[T] = None) -> 'HttpResponseModel[T]':
        """
        创建一个错误的响应
        
        参数:
            msg: 错误消息，默认为"error"
            code: HTTP状态码，默认为500
            data: 响应数据，默认为None
            
        返回:
            HttpResponse: 错误的响应对象
        """
        return cls(code, data, msg).model()
    
    @classmethod
    def bad_request(cls, msg: str = "Bad Request", data: Optional[T] = None) -> 'HttpResponseModel[T]':
        """
        创建一个400错误的响应
        
        参数:
            msg: 错误消息，默认为"Bad Request"
            data: 响应数据，默认为None
            
        返回:
            HttpResponse: 400错误的响应对象
        """
        return cls(400, data, msg).model()
    
    @classmethod
    def not_found(cls, msg: str = "Not Found", data: Optional[T] = None) -> 'HttpResponseModel[T]':
        """
        创建一个404错误的响应
        
        参数:
            msg: 错误消息，默认为"Not Found"
            data: 响应数据，默认为None
            
        返回:
            HttpResponse: 404错误的响应对象
        """
        return cls(404, data, msg).model()
    
    @classmethod
    def unauthorized(cls, msg: str = "Unauthorized", data: Optional[T] = None) -> 'HttpResponseModel[T]':
        """
        创建一个401错误的响应
        
        参数:
            msg: 错误消息，默认为"Unauthorized"
            data: 响应数据，默认为None
            
        返回:
            HttpResponse: 401错误的响应对象
        """
        return cls(401, data, msg).model()
    
    def model(self) -> HttpResponseModel[T]:
        """
        将响应对象转换为Pydantic模型
        
        返回:
            HttpResponseModel: 包含code、data和msg的Pydantic模型
        """
        return HttpResponseModel[T](
            code=self.code,
            data=self.data,
            msg=self.msg
        )

    def dict(self) -> dict:
        """
        将响应对象转换为字典
        
        返回:
            dict: 包含code、data和msg的字典
        """
        return self.model().model_dump(exclude_none=True)

    def json_response(self, status_code: Optional[int] = None) -> JSONResponse:
        """
        创建FastAPI的JSONResponse对象
        
        参数:
            status_code: 可选的HTTP状态码，如果不提供则使用响应对象的code字段
            
        返回:
            JSONResponse: FastAPI的JSON响应对象
        """
        return JSONResponse(
            content=self.dict(),
            status_code=status_code or self.code
        )
