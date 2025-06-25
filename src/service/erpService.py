from src.myHttp.utils.myHttpUtils import normal_post

url = "https://pmserp.toasin.cn/api/demo/executeSqlQuery"

async def erp_execute_sql(sql):
    if isinstance(sql,str):
        sql = {"sql": sql}
    else:
        sql = sql.model_dump()
    response = await normal_post(url, data=sql, headers={})
    return response['data']


