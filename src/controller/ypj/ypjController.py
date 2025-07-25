import logging

from fastapi import APIRouter

from src.ai.myDashScope.common import get_dashscope_completion

router = APIRouter(prefix="/erp", tags=["ERP 相关"])

logger = logging.getLogger(__name__)

@router.post("/get_address_info")
async def get_address_info():
    result = get_dashscope_completion()