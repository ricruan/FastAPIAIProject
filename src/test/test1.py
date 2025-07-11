import json

s = "{\"code\":200,\"data\":[{\"category_id\":96120,\"category_name\":\"集成电路\",\"total_amount\":70000,\"order_count\":1},{\"category_id\":95967,\"category_name\":\"中央处理器\",\"total_amount\":160,\"order_count\":1}],\"msg\":\"success\"}"


def main(sql_data) -> dict:
    json_data = json.loads(sql_data)
    if len(json_data["data"]) > 0:
        return {"result": {"type": "data", "data": json_data["data"]}}
    else:
        return {"result": {"type": "text", "data": "未查询到数据"}}
print(main(s))