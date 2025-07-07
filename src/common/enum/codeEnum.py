from enum import Enum

class CodeEnum(Enum):
    ORDER_SEARCH_MAPPING = ("order_search_mapping","订单搜索接口返回结果字段的中文映射")

    JXM_API_CODE = ("jixiaomei","极小妹接口的API编码")

    def __init__(self, value, description):
        self._value_ = value  # 必须定义 _value_，这是枚举的实际值
        self.description = description  # 自定义属性