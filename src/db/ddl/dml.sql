-- 2025.06.26
INSERT INTO stone_ai_db.api_info
(id, type_code, api_code, api_name, api_url, api_header, api_desc, api_param_struct, api_param_desc, api_param_template, create_time, update_time)
VALUES('3fdify2e8a7c-1d9e-4b6f-a8c3-7b5d2e6f4a1c', 'dify', 'jixiaomei', '极小妹Dify接口', 'http://1.12.43.211/v1/chat-messages', '{"Authorization":"Bearer app-4Vs16Hilvp1K2UtlBn3mqLBa"}', '极小妹的Dify接口', NULL, NULL, NULL, '2025-06-23 03:21:57', '2025-06-23 03:27:30');
INSERT INTO stone_ai_db.api_info
(id, type_code, api_code, api_name, api_url, api_header, api_desc, api_param_struct, api_param_desc, api_param_template, create_time, update_time)
VALUES('3fdify21535c-1d9e-4b6f-a8c3-7b5d2e6f4a1c', 'dify', 'erp_exec_sql', 'ERP执行SQL接口', 'https://pmserp.toasin.cn/api/demo/executeSqlQuery', '', 'ERP系统执行SQL的接口', NULL, NULL, NULL, '2025-06-23 03:21:57', '2025-06-23 03:27:30');
INSERT INTO stone_ai_db.api_info
(id, type_code, api_code, api_name, api_url, api_header, api_desc, api_param_struct, api_param_desc, api_param_template, create_time, update_time)
VALUES('3fdify2e9s6c-1d9e-4b6f-a8c3-7b5d2e6f4a1c', 'business', 'erp_generate_popi', 'PO/PI生成接口', 'https://pmserp.toasin.cn/api/sales/downloadcontract', '', 'ERP系统生成PO/PI的接口', NULL, NULL, NULL, '2025-06-23 03:21:57', '2025-06-23 03:27:30');
INSERT INTO stone_ai_db.api_info
(id, type_code, api_code, api_name, api_url, api_header, api_desc, api_param_struct, api_param_desc, api_param_template, create_time, update_time)
VALUES('d1d2c3y6s6c-1d9e-4b6f-a8c3-7b5d2e6f4a1c', 'business', 'erp_order_search', '订单查询接口', 'https://pmserp.toasin.cn/api/sales/querySalesOrders', '', 'ERP系统生成订单查询的接口', NULL, NULL, NULL, '2025-06-23 03:21:57', '2025-06-23 03:27:30');
INSERT INTO stone_ai_db.api_info
(id, type_code, api_code, api_name, api_url, api_header, api_desc, api_param_struct, api_param_desc, api_param_template, create_time, update_time)
VALUES('k1c2x3q36sc-1d9e-4b6f-a8c3-7b5d2e6f4a1c', 'business', 'erp_inventory_detail_search', '库存详情查询接口', 'https://pmserp.toasin.cn/api/inventory/get_stock_details', '', 'ERP系统生成库存详情查询的接口', NULL, NULL, NULL, '2025-06-23 03:21:57', '2025-06-23 03:27:30');
INSERT INTO stone_ai_db.api_info
(id, type_code, api_code, api_name, api_url, api_header, api_desc, api_param_struct, api_param_desc, api_param_template, create_time, update_time)
VALUES('cd386762-a3d8-4390-a430-13e54b88d0a1', 'func', 'datetime_to_timestamp', '时间转Unix时间戳函数', '', NULL, '将给定的日期时间和时区偏移转换为Unix时间戳（秒级）', '[{"year": "2024", "month": "1","day": "1"},{"year": "2024", "month": "2","day": "1"}]', 'year (int): 年份，如2025', '输入：2025年6月13日张三的销售额是多少', '2025-07-09 10:22:47', '2025-07-09 10:22:47');
INSERT INTO stone_ai_db.api_info
(id, type_code, api_code, api_name, api_url, api_header, api_desc, api_param_struct, api_param_desc, api_param_template, create_time, update_time)
VALUES('9c604732-eca7-484d-bf28-8e0b446dcfdb', 'business', 'erp_user_sale_info', 'ERP获取用户销售情况', 'https://pmserp.toasin.cn/api/sales/getSalesStatistics', NULL, 'ERP系统获取用户在指定时间范围内的销售情况', '{"seller_name":"Tony","startDate":"2021-05-12","endDate":"2025-09-13"}', ' seller_name 字符类型 销售员，人名或英文名
 startDate 字符类型 开始时间，未识别到可提取为空字符串
 endDate 字符类型 结束时间，未识别到可提取为空字符串', ' 输入： 2025年6月13日张三的销售额是多少
 输出： {"seller_name":"张三","startDate":"2025-06-13","endDate":"2025-06-13"}

 输入：2025年6月Ric的订单数量是多少
 输出： {"seller_name":"Ric","startDate":"2025-06-01","endDate":"2025-07-01"}', '2025-07-10 15:13:32', '2025-07-10 15:13:32');


INSERT INTO stone_ai_db.code
(id, code, value, `desc`, `type`, mapper, parent_code, create_time, update_time)
VALUES('6f9d9fb0-a05e-42c0-a185-52606388689c', 'order_search_mapping', '{"amount":"应收金额","client_name":"客户名称","create_time":"下单时间","currency":"应收金额","instorage_status":"入库状态","invoice_createtime":"开票时间","invoice_status":"开票状态","ordercode":"销售单号","paystatus":"收款状态","paytime":"收款时间","reviewtime":"审批时间","seller_name":"销售经理","status":"审批状态","storagetime":"入库时间","type":"类型","id":"订单ID"}', 'ERP系统订单查询接口返回结果的字段含义映射', 'para', NULL, NULL, '2025-07-07', '2025-07-07');
INSERT INTO stone_ai_db.code
(id, code, value, `desc`, `type`, mapper, parent_code, create_time, update_time)
VALUES('715910e1-8546-41ce-bd84-3f6377561b9b', 'erp_inventory_detail_search_1', '{"category":"品类","brand":"品牌","model":"型号","name":"名称","parameter":"参数","upccoding":"料号","warehouse":"所在仓库","usablestocknum":" 可售库存","stocknum":"实际在库","purchaseways":"采购在途","transferProductsways":"调拨在途","sale_occupytotals":"销售占用","proess_occupytotals":"生产占用","borrownum":"生产借用","rmastocknum":"售后借用","samplestocknum":"样品待还","lockstocknum":"冻结库存","rejectstocknum":"不良品","0_1_month":"库龄1个月内","1_3_months":"库龄1-3个月","3_6_months":"库龄3-6个月","6_12_months":"库龄6-12个月","over_1_year":"库龄1年以上 "}', 'ERP系统库存详情查询接口返回结果的字段含义映射,第一部分', 'para', NULL, NULL, '2025-07-07', '2025-07-07');
INSERT INTO stone_ai_db.code
(id, code, value, `desc`, `type`, mapper, parent_code, create_time, update_time)
VALUES('c2a7687e-0d8e-4991-998e-779b83a4966f', 'erp_inventory_detail_search_2', '{"order_no":"采购单号","intention_type":"采购目的","quantity":"采购数量","outbound_quantity":"库存数量","inventory_age":"库龄"}', 'ERP系统库存详情查询接口返回结果的字段含义映射,第二部分', 'para', NULL, NULL, '2025-07-07', '2025-07-07');
INSERT INTO stone_ai_db.code
(id, code, value, `desc`, `type`, mapper, parent_code, create_time, update_time)
VALUES('cd368d94-80f3-4fb9-8b98-efa46cac3ae9', 'json_structure_extraction', '## 目标
基于以下内容从用户问题中提取JSON结构数据，返回结果参考【结构示例】中的【参考示例】
## 规则
1.禁止生成【```json ```】
2.确保输出的内容可以直接被json.loads()解析

## 结构示例
$struct
## 额外补充
$date_info
', '通用JSON结构提取提示词', 'para', NULL, NULL, '2025-07-09', '2025-07-09');

INSERT INTO stone_ai_db.code
(id, code, value, `desc`, `type`, mapper, parent_code, create_time, update_time)
VALUES('4489af6d-acca-494d-8ff9-e9af3d859871', 'erp_inventory_analysis_prompt', '## 背景
你是一名数据分析师,正在分析一家公司的库存数据,基于已有的数据挖掘出库存量与市场趋势及资金占用之间的关系,并基于此提出库存优化建议.

## 任务
1. 基于已有数据对库存现状进行总结
2. 基于已有数据对库存问题进行分析(滞销风险,资金占用,市场趋势)
3. 基于已有数据对库存优化提出建议

## 回复示例
1.库存现状
- 当前库存量: 200PCS (剩余10%未消耗)
- 采购时间: 2023年2月1日
- 库龄: 超过1年(已超出一般IT硬件库存周转周期)
- 采购价格: 200元/PCS
- 当前市场价: 180元/PCS (已低于采购价格,存在滞销风险)
2.库存问题分析
- 存在滞销风险
    - 该型号为 DDR4 8G 内存条,当前市场价低于采购价格,存在滞销风险
    - 市场需求可能逐步转向DDR5,长期库存可能导致进一步贬值
    - 库龄超过1年，若继续积压,可能面临报废或折价抛售的风险
- 资金占用
    - 剩余库存价值 36,000元(200PCS * 180元/PCS)
    - 采购成本 40,000元(200PCS * 200元/PCS)
    - 存在资金占用,若长期积压,可能面临资金链断裂的风险
- 市场趋势
    - 服务器内存价格受供需影响,DDR4可能进入降价周期，需警惕进一步跌价
3.建议处理方案
- 优先内部消化(如适用) :
    - 与研发部门沟通,是否可以内部消化,优先使用库存
- 促销/折价销售:
    - 以170-175元/PCS的价格向渠道商或客户促销，加速周转
- 二手/翻新市场处理:
    - 以150-160元/PCS的价格向二手/翻新市场销售', 'ERP相关 库存分析提示词', 'para', NULL, NULL, '2025-07-09', '2025-07-09');











