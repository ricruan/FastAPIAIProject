from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from src.db.db import get_db
from src.pojo.po.aiCodePo import Code
from src.dao.aiCodeDao import (
    create_code,
    batch_create_codes,
    get_code_by_id,
    get_code_by_code,
    get_codes_by_type,
    get_codes_by_parent_code,
    search_codes,
    update_code,
    delete_code,
    delete_codes_by_type,
    delete_codes_by_parent_code,
    count_codes_by_type,
    get_all_codes,
    get_codes_by_mapper
)
from src.myHttp.bo.httpResponse import HttpResponse, HttpResponseModel
from pydantic import BaseModel
from src.utils.pageSearchUtil import PageRequest, CodePageResponse, paginate_query

router = APIRouter(prefix="/ai/code", tags=["Code"])

# 创建编码的请求模型
class CodeCreate(BaseModel):
    code: str
    value: Optional[str] = None
    desc: Optional[str] = None
    type: Optional[str] = None
    mapper: Optional[str] = None
    parent_code: Optional[str] = None

    def to_po(self) -> Code:
        """
        将VO转换为PO
        """
        return Code(
            id=str(uuid.uuid4()),
            code=self.code,
            value=self.value,
            desc=self.desc,
            type=self.type,
            mapper=self.mapper,
            parent_code=self.parent_code,
            create_time=datetime.now(),
            update_time=datetime.now()
        )

# 批量创建编码的请求模型
class BatchCodeCreate(BaseModel):
    codes: List[CodeCreate]

# 更新编码的请求模型
class CodeUpdate(BaseModel):
    value: Optional[str] = None
    desc: Optional[str] = None
    type: Optional[str] = None
    mapper: Optional[str] = None
    parent_code: Optional[str] = None

@router.get("/{code_id}", response_model=HttpResponseModel[Code])
async def get_code(code_id: str, db: Session = Depends(get_db)):
    """
    根据ID获取编码信息

    Args:
        code_id: 编码ID
        db: 数据库会话

    Returns:
        编码信息
    """
    code = get_code_by_id(db, code_id)
    if not code:
        return HttpResponse.error(msg=f"Code with id {code_id} not found")
    return HttpResponse.success(code)

@router.get("/by-code/{code_value}", response_model=HttpResponseModel[Code])
async def get_by_code(code_value: str, db: Session = Depends(get_db)):
    """
    根据编码值获取编码信息

    Args:
        code_value: 编码值
        db: 数据库会话

    Returns:
        编码信息
    """
    code = get_code_by_code(db, code_value)
    if not code:
        return HttpResponse.error(msg=f"Code with value {code_value} not found")
    return HttpResponse.success(code)

@router.get("/by-type/{type_value}", response_model=HttpResponseModel[List[Code]])
async def get_by_type(type_value: str, db: Session = Depends(get_db)):
    """
    根据类型获取编码列表

    Args:
        type_value: 类型值
        db: 数据库会话

    Returns:
        编码列表
    """
    codes = get_codes_by_type(db, type_value)
    return HttpResponse.success(codes)

@router.get("/by-parent/{parent_code}", response_model=HttpResponseModel[List[Code]])
async def get_by_parent(parent_code: str, db: Session = Depends(get_db)):
    """
    根据上级编码获取编码列表

    Args:
        parent_code: 上级编码
        db: 数据库会话

    Returns:
        编码列表
    """
    codes = get_codes_by_parent_code(db, parent_code)
    return HttpResponse.success(codes)

@router.get("/by-mapper/{mapper}", response_model=HttpResponseModel[List[Code]])
async def get_by_mapper(mapper: str, db: Session = Depends(get_db)):
    """
    根据映射实体获取编码列表

    Args:
        mapper: 映射实体名称
        db: 数据库会话

    Returns:
        编码列表
    """
    codes = get_codes_by_mapper(db, mapper)
    return HttpResponse.success(codes)

@router.get("/all", response_model=HttpResponseModel[List[Code]])
async def get_all(db: Session = Depends(get_db)):
    """
    获取所有编码

    Args:
        db: 数据库会话

    Returns:
        所有编码列表
    """
    codes = get_all_codes(db)
    return HttpResponse.success(codes)

@router.get("/count/{type_value}", response_model=HttpResponseModel[int])
async def count_by_type(type_value: str, db: Session = Depends(get_db)):
    """
    统计指定类型的编码数量

    Args:
        type_value: 类型值
        db: 数据库会话

    Returns:
        编码数量
    """
    count = count_codes_by_type(db, type_value)
    return HttpResponse.success(count)

@router.post("/", response_model=HttpResponseModel[Code])
async def create_code_endpoint(code_data: CodeCreate, db: Session = Depends(get_db)):
    """
    创建编码

    Args:
        code_data: 编码数据
        db: 数据库会话

    Returns:
        创建的编码
    """
    try:
        # 检查编码是否已存在
        existing_code = get_code_by_code(db, code_data.code)
        if existing_code:
            return HttpResponse.error(msg=f"Code with value {code_data.code} already exists")

        # 转换为PO并创建
        code_po = code_data.to_po()
        created_code = create_code(db, code_po)
        return HttpResponse.success(created_code)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.post("/batch", response_model=HttpResponseModel[List[Code]])
async def batch_create_codes_endpoint(batch_data: BatchCodeCreate, db: Session = Depends(get_db)):
    """
    批量创建编码

    Args:
        batch_data: 批量编码数据
        db: 数据库会话

    Returns:
        创建的编码列表
    """
    try:
        # 转换为PO并批量创建
        code_pos = [code.to_po() for code in batch_data.codes]
        created_codes = batch_create_codes(db, code_pos)
        return HttpResponse.success(created_codes)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.put("/{code_id}", response_model=HttpResponseModel[Code])
async def update_code_endpoint(code_id: str, code_data: CodeUpdate, db: Session = Depends(get_db)):
    """
    更新编码

    Args:
        code_id: 编码ID
        code_data: 更新的编码数据
        db: 数据库会话

    Returns:
        更新后的编码
    """
    # 转换为字典
    update_data = code_data.model_dump(exclude_unset=True)

    # 更新编码
    updated_code = update_code(db, code_id, update_data)
    if not updated_code:
        return HttpResponse.error(msg=f"Code with id {code_id} not found")

    return HttpResponse.success(updated_code)

@router.delete("/{code_id}", response_model=HttpResponseModel[bool])
async def delete_code_endpoint(code_id: str, db: Session = Depends(get_db)):
    """
    删除编码

    Args:
        code_id: 编码ID
        db: 数据库会话

    Returns:
        是否成功删除
    """
    result = delete_code(db, code_id)
    if not result:
        return HttpResponse.error(msg=f"Code with id {code_id} not found")

    return HttpResponse.success(True)

@router.delete("/by-type/{type_value}", response_model=HttpResponseModel[int])
async def delete_by_type(type_value: str, db: Session = Depends(get_db)):
    """
    删除指定类型的所有编码

    Args:
        type_value: 类型值
        db: 数据库会话

    Returns:
        删除的记录数量
    """
    count = delete_codes_by_type(db, type_value)
    return HttpResponse.success(count)

@router.delete("/by-parent/{parent_code}", response_model=HttpResponseModel[int])
async def delete_by_parent(parent_code: str, db: Session = Depends(get_db)):
    """
    删除指定上级编码的所有编码

    Args:
        parent_code: 上级编码
        db: 数据库会话

    Returns:
        删除的记录数量
    """
    count = delete_codes_by_parent_code(db, parent_code)
    return HttpResponse.success(count)

@router.post("/search", response_model=HttpResponseModel[List[Code]])
async def search_codes_endpoint(search_params: Dict[str, Any] | None, db: Session = Depends(get_db)):
    """
    搜索编码

    Args:
        search_params: 搜索参数
        db: 数据库会话

    Returns:
        符合条件的编码列表
    """
    try:
        results = search_codes(db, search_params)
        return HttpResponse.success(results)
    except Exception as e:
        return HttpResponse.error(msg=str(e))

@router.post("/page", response_model=HttpResponseModel[CodePageResponse])
async def page_codes(page_request: PageRequest, db: Session = Depends(get_db)):
    """
    分页查询编码
    
    Args:
        page_request: 分页请求参数，包含页码、每页大小、排序和搜索条件
        db: 数据库会话
        
    Returns:
        分页响应，包含总记录数、总页数和当前页数据
    """
    try:
        # 创建基础查询
        base_query = select(Code)
        
        # 使用通用分页查询函数
        page_result = paginate_query(db, Code, page_request, base_query)
        
        return HttpResponse.success(page_result)
    except Exception as e:
        return HttpResponse.error(msg=str(e))
