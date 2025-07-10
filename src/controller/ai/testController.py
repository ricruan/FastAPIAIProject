from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.ai.aiService import get_time_range
from src.db.db import get_db
from src.myHttp.bo.httpResponse import HttpResponse

router = APIRouter(prefix="/test", tags=["测试接口"])


@router.post("/test_get_time_range")
async def erp_test_get_time_range_controller(data: dict, db: Session = Depends(get_db)):
    data = await get_time_range(data["query"],data["model"])
    return HttpResponse.success(data)