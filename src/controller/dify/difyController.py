import logging
import json

import requests
from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.dao.apiInfoDao import get_info_by_api_code
from src.db.db import get_db
from src.myHttp.bo.httpResponse import HttpResponse
from src.myHttp.utils.myHttpUtils import normal_post
from src.pojo.vo.jixiaomeiVo import DifyJxm
from src.service.difyService import dify_result_handler

router = APIRouter(prefix="/dify", tags=["DIFY 相关"])


# 请求头
headers = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer YOUR_ACCESS_TOKEN"  # 如果需要认证，取消注释并替换 Token
}
JXM_API_CODE = "jixiaomei" # pmspte 更换成这个


logger = logging.getLogger(__name__)


@router.post("/chatflow-jxm")
async def execute_sql_query(param: DifyJxm, db: Session = Depends(get_db)):
    api_code = JXM_API_CODE
    api_info =get_info_by_api_code(session=db, api_code=api_code)
    api_url = api_info.api_url
    api_header = api_info.api_header


    response =await  normal_post(api_url, param.to_jxm(), json.loads(api_header))
    result = await dify_result_handler(response)
    return HttpResponse.success([result])




