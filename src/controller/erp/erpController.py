import json

import requests
from fastapi import APIRouter
from pydantic import BaseModel

from src.myHttp.bo.httpResponse import HttpResponse
from src.myHttp.utils.myHttpUtils import normal_post
from src.service.erpService import erp_execute_sql

router = APIRouter(prefix="/erp", tags=["ERP 相关"])




class SQLQuery(BaseModel):
    sql: str

@router.post("/execute-sql-query")
async def execute_sql_query(sql: SQLQuery):

    try:
        # 发送 POST 请求，设置超时时间为 10 秒
        response = await erp_execute_sql(sql)

        return HttpResponse.success(response)

    except requests.exceptions.Timeout:
        return HttpResponse.error(msg="请求超时，请稍后重试！")

    except requests.exceptions.RequestException as e:
        # 其他请求异常（如网络错误、SSL 错误等）
        return HttpResponse.error(msg="请求失败，请稍后重试！" + e.__str__())

