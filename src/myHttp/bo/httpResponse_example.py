from fastapi import Query, APIRouter
from typing import List, Dict, Any
from pydantic import BaseModel

from src.myHttp.bo.httpResponse import HttpResponse, HttpResponseModel

router = APIRouter(prefix="/http/example", tags=["HTTP 的示例接口"])

# 定义一个数据模型用于示例
class UserModel(BaseModel):
    id: int
    name: str
    email: str

# 使用HttpResponseModel作为响应模型，这样FastAPI会自动生成正确的API文档
@app.get("/example/success", response_model=HttpResponseModel[Dict[str, Any]])
async def example_success():
    # 创建一个成功的响应，只需提供data
    data = {"name": "示例数据", "value": 123}
    response = HttpResponse.success(data=data)
    
    # 直接使用json_response方法返回JSONResponse
    return response.json_response()

@app.get("/example/success-custom-msg", response_model=HttpResponseModel[Dict[str, Any]])
async def example_success_custom_msg():
    # 创建一个成功的响应，自定义消息
    data = {"name": "示例数据", "value": 123}
    response = HttpResponse.success(data=data, msg="操作成功完成")
    
    return response.json_response()

@app.get("/example/error", response_model=HttpResponseModel[None])
async def example_error():
    # 创建一个错误的响应
    response = HttpResponse.error(msg="发生了一个错误")
    
    # 注意：这里我们可以覆盖状态码，使其与HTTP标准一致
    # 虽然我们的响应体中code=500，但HTTP状态码可以是200
    # 这样客户端总是能收到我们的错误信息，而不是被HTTP错误拦截
    return response.json_response(status_code=200)

@app.get("/example/not-found", response_model=HttpResponseModel[None])
async def example_not_found():
    # 创建一个404错误的响应
    response = HttpResponse.not_found(msg="未找到请求的资源")
    
    return response.json_response(status_code=200)

@app.get("/example/custom", response_model=HttpResponseModel[Dict[str, Any]])
async def example_custom():
    # 直接创建自定义响应
    response = HttpResponse(code=201, data={"id": 1}, msg="资源已创建")
    
    return response.json_response()

@app.get("/users/{user_id}", response_model=HttpResponseModel[UserModel])
async def get_user(user_id: int):
    # 模拟从数据库获取用户
    if user_id == 1:
        user = UserModel(id=1, name="张三", email="zhangsan@example.com")
        return HttpResponse.success(data=user).json_response()
    else:
        return HttpResponse.not_found(msg=f"用户ID {user_id} 不存在").json_response()

@app.get("/users", response_model=HttpResponseModel[List[UserModel]])
async def get_users(limit: int = Query(10, ge=1, le=100)):
    # 模拟从数据库获取用户列表
    users = [
        UserModel(id=1, name="张三", email="zhangsan@example.com"),
        UserModel(id=2, name="李四", email="lisi@example.com")
    ]
    return HttpResponse.success(data=users).json_response()

# 在实际应用中，你可以创建一个响应处理中间件，自动将返回值包装为HttpResponse
