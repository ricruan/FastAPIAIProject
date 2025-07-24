import json
import logging

from fastapi import APIRouter, Depends
from sqlmodel import Session
from starlette.responses import StreamingResponse
from src.ai.aiService import sse_event_generator, easy_json_structure_extraction
from src.common.enum.codeEnum import CodeEnum
from src.dao.sessionDetailDao import create_session_detail
from src.pojo.bo.erpBo import SQLQuery, ERPOrderSearch, ERPInventoryDetailSearch, ERPInventoryDetailAnalysis, \
    ERPSellerSaleInfo, ERPUserSaleInfo, ERPSellerSaleInfoAnalysis
from src.db.db import get_db
from src.myHttp.bo.httpResponse import HttpResponse
from src.pojo.bo.aiBo import GetJsonModel
from src.pojo.po.sessionDetailPo import SessionDetail
from src.pojo.vo.difyResponse import DifyResponse
from src.pojo.vo.erpVo import PipoFile
from src.service.aiCodeService import get_code_value_by_code
from src.service.erpService import erp_execute_sql, erp_generate_popi, erp_order_search, \
    erp_inventory_detail_search_by_cn, erp_user_sale_info, inventory_analysis, erp_seller_sale_info_analysis, \
    erp_generate_pi, erp_order_search_without_check, erp_inventory_detail_search
from src.utils.dataUtils import translate_dict_keys_4_list

router = APIRouter(prefix="/erp", tags=["ERP 相关"])

logger = logging.getLogger(__name__)

@router.post("/execute-sql-query")
async def execute_sql_query(sql: SQLQuery, db: Session = Depends(get_db)):
    response = await erp_execute_sql(sql, db)

    return HttpResponse.success(response)


@router.post("/generate_popi")
async def generate_po_pi(data: dict, db: Session = Depends(get_db)):
    response = await erp_generate_popi(data, db)
    return HttpResponse.success(response)

@router.post("/generate_popi/fake")
async def generate_po_pi(data: PipoFile, db: Session = Depends(get_db)):
    if data.type.upper() == "PO":
        response = await erp_generate_popi({'ids' : data.ids,'token' : data.token}, db)
    else :
        response = await erp_generate_pi({'ids' : data.ids,'token' : data.token}, db)
    dify_res = DifyResponse.to_url(response)
    sd = SessionDetail(api_input=data.query,user_question=data.query,session_id=data.session_id)
    sd.when_success(output=response,response=dify_res)
    create_session_detail(session=db,session_detail=sd)
    return HttpResponse.success([dify_res])

@router.post("/generate_pi")
async def generate_po_pi(data: dict, db: Session = Depends(get_db)):
    response = await erp_generate_pi(data, db)
    return HttpResponse.success(response)

@router.post("/order_search")
async def order_search(data: ERPOrderSearch, db: Session = Depends(get_db)):
    response = await erp_order_search(data.model_dump(), db)
    result = translate_dict_keys_4_list(response, get_code_value_by_code(db, CodeEnum.ORDER_SEARCH_MAPPING.value))
    return HttpResponse.success(result)

@router.post("/token_check")
async def login_check(data: dict, db: Session = Depends(get_db)):
    params = ERPOrderSearch(token=data.get("token"))
    response = await erp_order_search_without_check(params.model_dump(), db)
    if 'token' in response['msg']:
        return HttpResponse.error(response['msg'])
    return HttpResponse.success("token有效")


@router.post("/inventory_detail")
async def inventory_detail(data: ERPInventoryDetailSearch, db: Session = Depends(get_db)):
    response = await erp_inventory_detail_search(data.model_dump(), db)
    return HttpResponse.success(response)

@router.post("/inventory_detail_analysis")
async def inventory_detail_analysis(data: ERPInventoryDetailAnalysis, db: Session = Depends(get_db)):
    response = await erp_inventory_detail_search(data.to_parent().model_dump(), db)
    prompt_text = get_code_value_by_code(session=db ,code_value = CodeEnum.ERP_INVENTORY_ANALYSIS_PROMPT_CODE.value)
    result = await inventory_analysis(data=response,prompt_text=prompt_text,model=data.model,stream=data.stream)
    if data.stream:
        return StreamingResponse(
        sse_event_generator(result),
        media_type="text/event-stream"
    )
    else:
        return HttpResponse.success(result)

@router.post("/seller_sale_info")
async def seller_sale_info(data: ERPSellerSaleInfo, db: Session = Depends(get_db)):
    response = await erp_user_sale_info(data.model_dump(), db)
    return HttpResponse.success(response)

@router.post("/dify/seller_sale_info")
async def dify_seller_sale_info(data: ERPUserSaleInfo, db: Session = Depends(get_db)):
    param = GetJsonModel(query=data.query,model="deepseek-chat",api_code=CodeEnum.ERP_USER_SALE_INFO_API_CODE.value)
    json_data = await easy_json_structure_extraction(param)
    result = await erp_user_sale_info({**json.loads(json_data), "token": data.token}, db)
    return HttpResponse.success(result)

@router.post("/seller_sale_info_analysis")
async def seller_sale_info_analysis(params: ERPSellerSaleInfoAnalysis, db: Session = Depends(get_db)):
    result = await erp_seller_sale_info_analysis(llm_params=params, sale_data=params.sale_data, session=db)
    if params.stream:
        return StreamingResponse(
            sse_event_generator(result),
            media_type="text/event-stream"
        )
    return HttpResponse.success(result)
