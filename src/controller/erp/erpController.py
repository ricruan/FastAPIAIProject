from fastapi import APIRouter, Depends
from pydantic import BaseModel,Field
from sqlmodel import Session
from src.db.db import get_db
from src.myHttp.bo.httpResponse import HttpResponse
from src.service.erpService import erp_execute_sql, erp_generate_popi,erp_order_search

router = APIRouter(prefix="/erp", tags=["ERP 相关"])




class SQLQuery(BaseModel):
    sql: str

class ERPOrderSearch(BaseModel):
    client: str = Field(..., description="客户名称", example="中盛")
    seller: str = Field(..., description="销售名称", example="张三")
    page: str = Field("1", description="页码（默认1，从1开始）", example="1")
    pagesize: str = Field("10", description="每页条数（默认10，如10/20/50）", example="10")
    token: str = Field(..., description="token")

@router.post("/execute-sql-query")
async def execute_sql_query(sql: SQLQuery, db: Session = Depends(get_db)):
    response = await erp_execute_sql(sql, db)

    return HttpResponse.success(response)


@router.post("/generate_popi")
async def generate_po_pi(data: dict, db: Session = Depends(get_db)):
    response = await erp_generate_popi(data, db)

    return HttpResponse.success(response)

@router.post("/order_search")
async def order_search(data: ERPOrderSearch, db: Session = Depends(get_db)):
    response = await erp_order_search(data.model_dump(), db)

    return HttpResponse.success(response)
