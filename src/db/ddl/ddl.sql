-- stone_ai_db.api_info definition

CREATE TABLE `api_info` (
  `id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '唯一标识',
  `type_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '类型编码',
  `api_code` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'API编码',
  `api_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'API名称',
  `api_url` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'API访问路径',
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


