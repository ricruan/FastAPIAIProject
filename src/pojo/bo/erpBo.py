from pydantic import BaseModel, Field

from src.pojo.bo.aiBo import ModelConfig, Query, NormalLLMRequestModel


class TokenModel(BaseModel):
    token: str = Field(..., description="token")


class SQLQuery(BaseModel):
    sql: str

class ERPOrderSearch(TokenModel):
    client: str = Field("", description="客户名称", example="中盛")
    seller: str = Field("", description="销售名称", example="张三")
    page: str = Field("1", description="页码（默认1，从1开始）", example="1")
    pagesize: str = Field("10", description="每页条数（默认10，如10/20/50）", example="10")

class ERPInventoryDetailSearch(TokenModel):
    code: str = Field(..., description="库存编码", example="IC-2505-0711-8812")
    warehouse_name: str = Field(..., description="仓库名称", example="香港仓1")

class ERPInventoryDetailAnalysis(ERPInventoryDetailSearch,ModelConfig):

    def to_parent(self):
        return ERPInventoryDetailSearch(**self.model_dump())

class ERPUserSaleInfo(TokenModel,Query):
    pass

class ERPSellerSaleInfo(TokenModel):
    seller_name: str = Field(..., description="销售名称", example="Tony")
    startDate: str = Field(..., description="开始时间", example="2025-05-12")
    endDate: str = Field(..., description="结束时间", example="2025-05-13")


class ERPSaveOrder(BaseModel):
    user_id: str = Field(..., description="用户ID", example="123")
    result: str = Field(..., description="最终保存返回结果", example="{}")

class ERPSellerSaleInfoAnalysis(NormalLLMRequestModel):
    sale_data: str = Field(..., description="销售情况数据", example='''[{"category_id":96120,"category_name":"集成电路","total_amount":210000,"order_count":3},{"category_id":95967,"category_name":"中央处理器","total_amount":1600,"order_count":10}]''')