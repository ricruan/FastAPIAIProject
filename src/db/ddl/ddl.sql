-- stone_ai_db.api_info definition

CREATE TABLE `api_info` (
  `id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '唯一标识',
  `type_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '类型编码',
  `api_code` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'API编码',
  `api_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'API名称',
  `api_url` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'API访问路径',
  `api_header` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'API请求头',
  `api_desc` text COLLATE utf8mb4_unicode_ci COMMENT 'API描述',
  `api_param_struct` text COLLATE utf8mb4_unicode_ci COMMENT 'API参数结构',
  `api_param_desc` text COLLATE utf8mb4_unicode_ci COMMENT 'API参数描述',
  `api_param_template` text COLLATE utf8mb4_unicode_ci COMMENT 'API参数示例',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_api_code` (`api_code`) COMMENT 'API编码唯一索引',
  KEY `idx_api_name` (`api_name`) COMMENT 'API名称索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='API信息表';


INSERT INTO stone_ai_db.api_info
(id, type_code, api_code, api_name, api_url, api_header, api_desc, api_param_struct, api_param_desc, api_param_template, create_time, update_time)
VALUES('3fdify2e8a7c-1d9e-4b6f-a8c3-7b5d2e6f4a1c', 'dify', 'jixiaomei', '极小妹Dify接口', 'http://1.12.43.211/v1/chat-messages', '{"Authorization":"Bearer app-4Vs16Hilvp1K2UtlBn3mqLBa"}', '极小妹的Dify接口', NULL, NULL, NULL, '2025-06-23 03:21:57', '2025-06-23 03:27:30');
INSERT INTO stone_ai_db.api_info
(id, type_code, api_code, api_name, api_url, api_header, api_desc, api_param_struct, api_param_desc, api_param_template, create_time, update_time)
VALUES('3fdify21535c-1d9e-4b6f-a8c3-7b5d2e6f4a1c', 'dify', 'erp_exec_sql', 'ERP执行SQL接口', 'https://pmserp.toasin.cn/api/demo/executeSqlQuery', '', 'ERP系统执行SQL的接口', NULL, NULL, NULL, '2025-06-23 03:21:57', '2025-06-23 03:27:30');


