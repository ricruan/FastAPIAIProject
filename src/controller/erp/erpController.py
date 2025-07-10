from fastapi import APIRouter, Depends
from pydantic import BaseModel,Field
from sqlmodel import Session
from starlette.responses import StreamingResponse

from src.ai.aiService import inventory_analysis, get_time_range, sse_event_generator
from src.common.enum.codeEnum import CodeEnum
from src.db.db import get_db
from src.myHttp.bo.httpResponse import HttpResponse
from src.service.aiCodeService import get_code_value_by_code
from src.service.erpService import erp_execute_sql, erp_generate_popi, erp_order_search, \
    erp_inventory_detail_search_by_cn
from src.utils.dataUtils import translate_dict_keys_4_list

router = APIRouter(prefix="/erp", tags=["ERP 相关"])




class SQLQuery(BaseModel):
    sql: str

class ERPOrderSearch(BaseModel):
    client: str = Field(..., description="客户名称", example="中盛")
    seller: str = Field(..., description="销售名称", example="张三")
    page: str = Field("1", description="页码（默认1，从1开始）", example="1")
    pagesize: str = Field("10", description="每页条数（默认10，如10/20/50）", example="10")
    token: str = Field(..., description="token")

class ERPInventoryDetailSearch(BaseModel):
    code: str = Field(..., description="库存编码", example="IC-2505-0711-8812")
    warehouse_name: str = Field(..., description="仓库名称", example="香港仓1")
    token: str = Field(..., description="token")

class ERPInventoryDetailAnalysis(ERPInventoryDetailSearch):
    model: str = Field("deepseek", description="模型名称", example="deepseek")
    is_stream: bool = Field(True, description="是否流式响应", example=True)

    def to_parent(self):
        return ERPInventoryDetailSearch(**self.model_dump())

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
    result = translate_dict_keys_4_list(response, get_code_value_by_code(db, CodeEnum.ORDER_SEARCH_MAPPING.value))
    return HttpResponse.success(result)

@router.post("/inventory_detail")
async def order_search(data: ERPInventoryDetailSearch, db: Session = Depends(get_db)):
    response = await erp_inventory_detail_search_by_cn(data.model_dump(), db)
    return HttpResponse.success(response)

@router.post("/inventory_detail_analysis")
async def order_search(data: ERPInventoryDetailAnalysis, db: Session = Depends(get_db)):
    response = await erp_inventory_detail_search_by_cn(data.to_parent().model_dump(), db)
    prompt_text = get_code_value_by_code(session=db ,code_value = CodeEnum.ERP_INVENTORY_ANALYSIS_PROMPT_CODE.value)
    result = await inventory_analysis(data=response,prompt_text=prompt_text,model=data.model,stream=data.is_stream)
    if data.is_stream:
        return StreamingResponse(
        sse_event_generator(result),
        media_type="text/event-stream"
    )
    else:
        return HttpResponse.success(result)
