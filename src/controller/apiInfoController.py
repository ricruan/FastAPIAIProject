from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict, Any, List
from src.db.db import get_db
from src.pojo.po.apiInfoPo import APIInfo
from src.dao.apiInfoDao import get_info_by_api_code,get_info_by_type_code, create_api_info, search_api_info # 获取数据库会话
from src.pojo.vo.apiInfoVo import APIInfoCreate
from src.myHttp.bo.httpResponse import HttpResponse, HttpResponseModel
from src.service.apiInfoService import get_api_info_4_task_classify

router = APIRouter(prefix="/api/info", tags=["API Info"])

@router.get("/api/{api_code}")
async def get_api_info_by_api_code(api_code: str, db: Session = Depends(get_db)) :
    """
    根据API编码获取API信息
    :param api_code:  api编码
    :param db: db
    :return:  查询结果
    """
    api_info = get_info_by_api_code(db, api_code)
    return HttpResponse.success(api_info)

@router.get("/type/{type_code}", response_model=HttpResponseModel[List[Dict[str, Any]]])
async def get_api_info_by_type_code(type_code: str, db: Session = Depends(get_db)) :
    """
    根据API编码获取API信息
    :param type_code:  api分类编码
    :param db: db
    :return:  查询结果
    """
    api_info = get_info_by_type_code(db, type_code)
    data = get_api_info_4_task_classify(api_info)
    return HttpResponse.success(data)

@router.post("/", response_model=HttpResponseModel[APIInfo])
async def create_api_info_endpoint(api_info_data: APIInfoCreate, db: Session = Depends(get_db)) :
    """
    创建API信息
    :param api_info_data: vo入参
    :param db: db
    :return:  反显数据
    """
    # 检查API编码是否已存在
    existing_api_info = get_info_by_api_code(db, api_info_data.api_code)
    if existing_api_info:
        raise HTTPException(
            status_code=400,
            detail=f"API with code {api_info_data.api_code} already exists"
        )
    
    # 创建APIInfo对象
    api_info = api_info_data.to_po()
    
    try:
        # 调用CRUD函数创建APIInfo
        created_api_info = create_api_info(db, api_info)
        return HttpResponse.success(created_api_info)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.post("/search", response_model=HttpResponseModel[List[APIInfo]])
async def search_api_info_endpoint(search_params: Dict[str, Any], db: Session = Depends(get_db)) -> HttpResponseModel[List[APIInfo]]:
    """
    根据提供的参数搜索API信息
    
    :param search_params: 搜索参数字典，键为APIInfo的字段名，值为搜索条件
    :param db: 数据库会话
    :return: 符合条件的APIInfo列表
    """
    try:
        # 调用CRUD函数搜索APIInfo
        results = search_api_info(db, search_params)
        return HttpResponse.success(results)
    except Exception as e:
        return HttpResponse.error(msg=str(e))
