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


-- stone_ai_db.`session` definition

CREATE TABLE `session` (
  `id` varchar(64) NOT NULL COMMENT '唯一标识',
  `dify_conversation_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'dify的会话ID',
  `session_title` varchar(255) DEFAULT NULL COMMENT '会话标题',
  `session_desc` text COMMENT '会话描述',
  `create_time` datetime NOT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `user_id` varchar(64) NOT NULL COMMENT '用户ID',
  `token` varchar(255) DEFAULT NULL COMMENT 'token',
  `history_semantic` text COMMENT '历史会话语义',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='会话表';


-- stone_ai_db.session_detail definition
CREATE TABLE `session_detail` (
  `id` varchar(64) NOT NULL COMMENT '唯一标识',
  `session_id` varchar(64) NOT NULL COMMENT '会话主题id',
  `dialog_carrier` varchar(255) DEFAULT NULL COMMENT '对话载体',
  `api_input` text COMMENT '接口原始入参',
  `api_output` text COMMENT '接口原始出参',
  `user_question` text COMMENT '对话用户问题',
  `final_response` text COMMENT '对话最终返回',
  `process_log` text COMMENT '会话流程日志',
  `model` varchar(100) DEFAULT NULL COMMENT '模型',
  `response_mode` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '响应模式',
  `agent` varchar(100) DEFAULT NULL COMMENT '智能体',
  `status` varchar(12) DEFAULT NULL COMMENT '会话状态',
  `create_time` datetime NOT NULL COMMENT '创建时间',
  `finish_time` datetime DEFAULT NULL COMMENT '结束时间',
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_create_time` (`create_time`),
  CONSTRAINT `fk_session_detail_session` FOREIGN KEY (`session_id`) REFERENCES `session` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='会话详情表';


CREATE TABLE `code` (
  `id` varchar(36) NOT NULL COMMENT '唯一标识，存储UUID',
  `code` varchar(64) NOT NULL COMMENT '编码',
  `value` text COMMENT '码值',
  `desc` text COMMENT '描述',
  `type` varchar(64) COMMENT '类型',
  `mapper` varchar(64) COMMENT '映射实体',
  `parent_code` varchar(64) COMMENT '上级编码',
  `create_time` date COMMENT '创建时间',
  `update_time` date COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_code` (`code`),
  KEY `idx_parent_code` (`parent_code`),
  KEY `idx_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='编码表';