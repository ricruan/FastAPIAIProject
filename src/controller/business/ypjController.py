import logging
import os
from dotenv import load_dotenv
from fastapi import APIRouter
from starlette.responses import StreamingResponse
from src.ai.myDashScope.common import get_dashscope_completion, DashScopeAPIParam, sse_event_generator, result_handle

router = APIRouter(prefix="/ypj", tags=["易拍居 相关"])

logger = logging.getLogger(__name__)

load_dotenv()

@router.post("/get_address_info")
async def get_address_info(params: DashScopeAPIParam):
    params.app_id=os.getenv("ADDRESS_APP_ID")
    result = get_dashscope_completion(params)
    result = result_handle(result,params.stream)
    if params.stream:
        return StreamingResponse(
            sse_event_generator(result),
            media_type="text/event-stream"
        )
    else:
        return result
