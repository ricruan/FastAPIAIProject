import logging
from fastapi import Depends
from src.dao.apiInfoDao import get_info_by_api_code
from src.db.db import get_db
from src.myHttp.utils.myHttpUtils import normal_post
from sqlmodel import Session

logger = logging.getLogger(__name__)
url = "https://pmserp.toasin.cn/api/demo/executeSqlQuery"
ERP_EXEC_SQL_API_CODE = "erp_exec_sql"

async def erp_execute_sql(sql, session: Session):
    api_info = get_info_by_api_code(session,ERP_EXEC_SQL_API_CODE)


    if isinstance(sql,str):
        sql = {"sql": sql}
    else:
        sql = sql.model_dump()
    response = await normal_post(url, data=sql, headers={})
    return response['data']


