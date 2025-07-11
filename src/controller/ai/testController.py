from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session

from src.ai.aiService import get_time_range, easy_json_structure_extraction
from src.db.db import get_db
from src.myHttp.bo.httpResponse import HttpResponse
from src.pojo.bo.aiBo import GetJsonModel

router = APIRouter(prefix="/test", tags=["测试接口"])



@router.post("/test_get_time_range")
async def erp_test_get_time_range_controller(data: dict, db: Session = Depends(get_db)):
    data = await get_time_range(data["query"],data["model"])
    return HttpResponse.success(data)

@router.post("/test_get_json")
async def get_json_controller(data: GetJsonModel, db: Session = Depends(get_db)):
    data = await easy_json_structure_extraction(**data.model_dump())
    return HttpResponse.success(data)

