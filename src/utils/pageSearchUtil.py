from typing import TypeVar, Generic, List, Dict, Any, Optional, Sequence
from pydantic import BaseModel, Field
from sqlmodel import Session, select, SQLModel
from sqlalchemy import func, Select

# 导入Code模型用于创建具体的分页响应类
from src.pojo.po.aiCodePo import Code

T = TypeVar('T')

class PageRequest(BaseModel):
    """
    分页请求参数模型
    """
    page: int = Field(default=1, ge=1, description="页码，从1开始")
    page_size: int = Field(default=10, ge=1, le=100, description="每页记录数，默认10，最大100")
    sort_field: Optional[str] = Field(default=None, description="排序字段")
    sort_order: Optional[str] = Field(default="asc", description="排序方向，asc或desc")
    search_params: Optional[Dict[str, Any]] = Field(default=None, description="搜索参数")

class PageResponse(BaseModel, Generic[T]):
    """
    分页响应模型
    """
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页记录数")
    total: int = Field(description="总记录数")
    total_pages: int = Field(description="总页数")
    data: List[T] = Field(description="当前页数据")
    
    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "page": 1,
                "page_size": 10,
                "total": 100,
                "total_pages": 10,
                "data": []
            }
        }
    }

def paginate_query(
    session: Session,
    model_class: type[SQLModel],
    page_request: PageRequest,
    base_query: Optional[Select] = None
) -> Any:
    """
    通用分页查询函数

    Args:
        session: 数据库会话
        model_class: 模型类
        page_request: 分页请求参数
        base_query: 基础查询，如果提供则在此基础上进行分页，否则创建新查询

    Returns:
        分页响应对象，根据模型类型返回不同的分页响应类
    """
    # 创建基础查询
    if base_query is None:
        query = select(model_class)
    else:
        query = base_query

    # 应用搜索条件
    if page_request.search_params:
        query = apply_search_filters(query, model_class, page_request.search_params)

    # 计算总记录数
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # 应用排序
    if page_request.sort_field and hasattr(model_class, page_request.sort_field):
        sort_field = getattr(model_class, page_request.sort_field)
        if page_request.sort_order.lower() == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

    # 应用分页
    offset = (page_request.page - 1) * page_request.page_size
    query = query.offset(offset).limit(page_request.page_size)

    # 执行查询
    results = session.exec(query).all()

    # 计算总页数
    total_pages = (total + page_request.page_size - 1) // page_request.page_size if total > 0 else 0

    # 根据模型类型返回适当的分页响应对象
    if model_class == Code:
        return CodePageResponse(
            page=page_request.page,
            page_size=page_request.page_size,
            total=total,
            total_pages=total_pages,
            data=results
        )
    else:
        # 对于其他模型类型，返回通用的分页响应对象
        return PageResponse(
            page=page_request.page,
            page_size=page_request.page_size,
            total=total,
            total_pages=total_pages,
            data=results
        )

def apply_search_filters(query: Select, model_class: type[SQLModel], search_params: Dict[str, Any]) -> Select:
    """
    应用搜索过滤条件

    Args:
        query: 基础查询
        model_class: 模型类
        search_params: 搜索参数

    Returns:
        应用了过滤条件的查询
    """
    # 获取模型类的所有字段名
    model_fields = [column.name for column in model_class.__table__.columns]

    # 获取模型类中定义的like_search_fields（如果存在）
    like_search_fields = getattr(model_class, "like_search_fields", []) if hasattr(model_class, "like_search_fields") else []

    # 动态构建查询条件
    for field, value in search_params.items():
        if field in model_fields and value is not None:
            # 根据字段是否在like_search_fields中决定查询方式
            if field in like_search_fields and isinstance(value, str):
                query = query.where(getattr(model_class, field).like(f"%{value}%"))
            else:
                # 对于其他字段，使用精确匹配
                query = query.where(getattr(model_class, field) == value)

    return query

# 为Code模型创建具体的分页响应类
class CodePageResponse(BaseModel):
    """
    Code模型的分页响应模型
    """
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页记录数")
    total: int = Field(description="总记录数")
    total_pages: int = Field(description="总页数")
    data: List[Code] = Field(description="当前页数据")
    
    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "page": 1,
                "page_size": 10,
                "total": 100,
                "total_pages": 10,
                "data": []
            }
        }
    }

def create_page_response(
    page: int,
    page_size: int,
    total: int,
    data: List[Any]
) -> PageResponse:
    """
    创建分页响应对象

    Args:
        page: 当前页码
        page_size: 每页记录数
        total: 总记录数
        data: 当前页数据

    Returns:
        分页响应对象
    """
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PageResponse(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        data=data
    )

def create_code_page_response(
    page: int,
    page_size: int,
    total: int,
    data: List[Code]
) -> CodePageResponse:
    """
    创建Code模型的分页响应对象

    Args:
        page: 当前页码
        page_size: 每页记录数
        total: 总记录数
        data: 当前页数据

    Returns:
        Code模型的分页响应对象
    """
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return CodePageResponse(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        data=data
    )
