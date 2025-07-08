-- 2025.06.26
INSERT INTO stone_ai_db.api_info
(id, type_code, api_code, api_name, api_url, api_header, api_desc, api_param_struct, api_param_desc, api_param_template, create_time, update_time)
VALUES('3fdify2e8a7c-1d9e-4b6f-a8c3-7b5d2e6f4a1c', 'dify', 'jixiaomei', '极小妹Dify接口', 'http://1.12.43.211/v1/chat-messages', '{"Authorization":"Bearer app-4Vs16Hilvp1K2UtlBn3mqLBa"}', '极小妹的Dify接口', NULL, NULL, NULL, '2025-06-23 03:21:57', '2025-06-23 03:27:30');
INSERT INTO stone_ai_db.api_info
(id, type_code, api_code, api_name, api_url, api_header, api_desc, api_param_struct, api_param_desc, api_param_template, create_time, update_time)
VALUES('3fdify21535c-1d9e-4b6f-a8c3-7b5d2e6f4a1c', 'dify', 'erp_exec_sql', 'ERP执行SQL接口', 'https://pmserp.toasin.cn/api/demo/executeSqlQuery', '', 'ERP系统执行SQL的接口', NULL, NULL, NULL, '2025-06-23 03:21:57', '2025-06-23 03:27:30');
INSERT INTO stone_ai_db.api_info
(id, type_code, api_code, api_name, api_url, api_header, api_desc, api_param_struct, api_param_desc, api_param_template, create_time, update_time)
VALUES('3fdify2e9s6c-1d9e-4b6f-a8c3-7b5d2e6f4a1c', 'erp', 'erp_generate_popi', 'PO/PI生成接口', 'https://pmserp.toasin.cn/api/sales/downloadcontract', '', 'ERP系统生成PO/PI的接口', NULL, NULL, NULL, '2025-06-23 03:21:57', '2025-06-23 03:27:30');
INSERT INTO stone_ai_db.api_info
(id, type_code, api_code, api_name, api_url, api_header, api_desc, api_param_struct, api_param_desc, api_param_template, create_time, update_time)
VALUES('d1d2c3y6s6c-1d9e-4b6f-a8c3-7b5d2e6f4a1c', 'erp', 'erp_order_search', '订单查询接口', 'https://pmserp.toasin.cn/api/sales/querySalesOrders', '', 'ERP系统生成订单查询的接口', NULL, NULL, NULL, '2025-06-23 03:21:57', '2025-06-23 03:27:30');

INSERT INTO stone_ai_db.code
(id, code, value, `desc`, `type`, mapper, parent_code, create_time, update_time)
VALUES('6f9d9fb0-a05e-42c0-a185-52606388689c', 'order_search_mapping', '{"amount":"应收金额","client_name":"客户名称","create_time":"下单时间","currency":"应收金额","instorage_status":"入库状态","invoice_createtime":"开票时间","invoice_status":"开票状态","ordercode":"销售单号","paystatus":"收款状态","paytime":"收款时间","reviewtime":"审批时间","seller_name":"销售经理","status":"审批状态","storagetime":"入库时间","type":"类型","id":"订单ID"}', 'ERP系统订单查询接口返回结果的字段含义映射', 'para', NULL, NULL, '2025-07-07', '2025-07-07');
INSERT INTO stone_ai_db.code
(id, code, value, `desc`, `type`, mapper, parent_code, create_time, update_time)
VALUES('715910e1-8546-41ce-bd84-3f6377561b9b', 'erp_inventory_detail_search_1', '{"category":"品类","brand":"品牌","model":"型号","name":"名称","parameter":"参数","upccoding":"料号","warehouse":"所在仓库","usablestocknum":" 可售库存","stocknum":"实际在库","purchaseways":"采购在途","transferProductsways":"调拨在途","sale_occupytotals":"销售占用","proess_occupytotals":"生产占用","borrownum":"生产借用","rmastocknum":"售后借用","samplestocknum":"样品待还","lockstocknum":"冻结库存","rejectstocknum":"不良品","0_1_month":"库龄1个月内","1_3_months":"库龄1-3个月","3_6_months":"库龄3-6个月","6_12_months":"库龄6-12个月","over_1_year":"库龄1年以上 "}', 'ERP系统库存详情查询接口返回结果的字段含义映射,第一部分', 'para', NULL, NULL, '2025-07-07', '2025-07-07');
INSERT INTO stone_ai_db.code
(id, code, value, `desc`, `type`, mapper, parent_code, create_time, update_time)
VALUES('c2a7687e-0d8e-4991-998e-779b83a4966f', 'erp_inventory_detail_search_2', '{"order_no":"采购单号","intention_type":"采购目的","quantity":"采购数量","outbound_quantity":"库存数量","inventory_age":"库龄"}', 'ERP系统库存详情查询接口返回结果的字段含义映射,第二部分', 'para', NULL, NULL, '2025-07-07', '2025-07-07');














