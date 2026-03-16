drop DATABASE faq_db;

CREATE DATABASE IF NOT EXISTS faq_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE faq_db;

-- 类目管理表
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    env ENUM('TEST', 'PROD') NOT NULL COMMENT '环境(TEST-测试,PROD-生产)',
    name VARCHAR(64) NOT NULL COMMENT '类目名称',
    parent_id INT COMMENT '父类目ID',
    level INT NOT NULL COMMENT '层级(1-一级,2-二级)',
    original_id INT COMMENT '溯源ID',
    creator VARCHAR(64) NOT NULL COMMENT '创建人',
    modifier VARCHAR(64) COMMENT '修改人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='类目管理表';

-- FAQ主表
CREATE TABLE faqs (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    env ENUM('TEST', 'PROD') NOT NULL COMMENT '环境(TEST-测试,PROD-生产)',
    category_id INT NOT NULL COMMENT '类目ID',
    title VARCHAR(255) NOT NULL COMMENT '问题标题',
    similar_queries JSON COMMENT '相似问法',
    related_ids JSON COMMENT '关联FAQ ID列表',
    tags JSON COMMENT '标签列表',
    status ENUM('ENABLE', 'DISABLE') DEFAULT 'DISABLE' COMMENT '状态(ENABLE-启用,DISABLE-禁用)',
    is_permanent BOOLEAN DEFAULT TRUE COMMENT '是否永久有效',
    start_time DATETIME COMMENT '生效开始时间',
    end_time DATETIME COMMENT '生效结束时间',
    creator VARCHAR(64) NOT NULL COMMENT '创建人',
    modifier VARCHAR(64) COMMENT '修改人',
    answer_type ENUM('TEXT', 'RICH', 'CARD') DEFAULT 'TEXT' COMMENT '答案类型(TEXT-纯文本,RICH-富文本,CARD-卡片)',  
    content TEXT COMMENT '答案具体内容',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'   
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='FAQ主表';