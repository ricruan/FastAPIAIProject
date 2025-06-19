import uuid

from pydantic import BaseModel
from datetime import datetime

from src.pojo.po.apiInfoPo import APIInfo


# 创建APIInfo的请求体模型
class APIInfoCreate(BaseModel):
    type_code: str
    api_code: str
    api_name: str
    api_url: str
    api_desc: str
    api_param_struct: str = None
    api_param_desc: str = None
    api_param_template: str = None

    class Config:
        json_schema_extra = {
            "example": {
                "type_code": "user",
                "api_code": "user_get_info",
                "api_name": "获取用户信息",
                "api_url": "/api/user/info",
                "api_desc": "这是一个获取用户信息的API",
                "api_param_struct": "{\"param1\": \"value1\", \"param2\": \"value2\"}",
                "api_param_desc": "这是请求参数描述",
                "api_param_template": "{\"param1\": \"%{value1}\", \"param2\": \"%{value2}\"}"
            }
        }

    def to_po(self):
        """
        转化成PO对象
        :return: 对应的PO对象
        """
        return APIInfo(
        id=uuid.uuid4(),
        type_code=self.type_code,
        api_code=self.api_code,
        api_name=self.api_name,
        api_url=self.api_url,
        api_desc=self.api_desc,
        api_param_struct=self.api_param_struct,
        api_param_desc=self.api_param_desc,
        api_param_template=self.api_param_template,
        create_time=datetime.now(),
        update_time=datetime.now()
    )