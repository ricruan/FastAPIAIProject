import json
import requests
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session
from src.db.db import get_db
from src.myHttp.bo.httpResponse import HttpResponse
from src.myHttp.utils.myHttpUtils import normal_post
from src.service.erpService import erp_execute_sql

router = APIRouter(prefix="/erp", tags=["ERP 相关"])




class SQLQuery(BaseModel):
    sql: str

@router.post("/execute-sql-query")
async def execute_sql_query(sql: SQLQuery, db: Session = Depends(get_db)):
    response = await erp_execute_sql(sql, db)

    return HttpResponse.success(response)

