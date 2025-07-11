from enum import Enum

class CodeEnum(Enum):
    ORDER_SEARCH_MAPPING = ("order_search_mapping","订单搜索接口返回结果字段的中文映射")
    ERP_EXEC_SQL_API_CODE = ("erp_exec_sql","执行SQL的API编码")
    ERP_GEN_POPI_API_CODE = ("erp_generate_popi","生成POPI的API编码")
    ERP_ORDER_SEARCH_API_CODE = ("erp_order_search","订单查询的API编码")
    ERP_INVENTORY_DETAIL_SEARCH_API_CODE = ("erp_inventory_detail_search","库存详情查询的API编码")
    ERP_INVENTORY_ANALYSIS_PROMPT_CODE = ("erp_inventory_analysis_prompt","库存分析提示的API编码")
    JSON_STRUCTURE_EXTRACTION_PROMPT_CODE = ("json_structure_extraction","JSON结构化提取的提示词编码")
    DATETIME_TO_TIMESTAMP_FUNC_CODE = ("datetime_to_timestamp","日期时间转时间戳的函数编码")
    ERP_USER_SALE_INFO_API_CODE = ("erp_user_sale_info","ERP用户销售信息查询的API编码")
    ERP_SELLER_WORK_ANALYSIS_PROMPT_CODE = ("erp_seller_work_analysis_prompt","ERP销售工作分析的提示词编码")

    JXM_API_CODE = ("jixiaomei","极小妹接口的API编码")

    def __init__(self, value, description):
        self._value_ = value  # 必须定义 _value_，这是枚举的实际值
        self.description = description  # 自定义属性