import requests
from fastapi import APIRouter

from src.myHttp.bo.httpResponse import HttpResponse

router = APIRouter(prefix="/erp", tags=["ERP 相关"])
# 接口 URL
url = "https://pmserp.toasin.cn/api/demo/executeSqlQuery"

# 请求头
headers = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer YOUR_ACCESS_TOKEN"  # 如果需要认证，取消注释并替换 Token
}



@router.post("/execute-sql-query")
async def execute_sql_query(sql: str):

    try:
        # 发送 POST 请求，设置超时时间为 10 秒
        response = requests.post(url, json={"sql":sql}, headers=headers, timeout=10)

        # 检查响应状态码
        if response.status_code == 200:
            # 请求成功，解析 JSON 数据
            data = response.json()
            return HttpResponse.success(data)

        else:

            return HttpResponse.error(msg="请求失败，请稍后重试！")

    except requests.exceptions.Timeout:
        return HttpResponse.error(msg="请求超时，请稍后重试！")

    except requests.exceptions.RequestException as e:
        # 其他请求异常（如网络错误、SSL 错误等）
        return HttpResponse.error(msg="请求失败，请稍后重试！" + e.__str__())

