-- Leantime Database Initialization Script
-- This script sets up the initial database configuration for Leantime

-- Ensure UTF8MB4 character set for full Unicode support
ALTER DATABASE leantime_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant additional permissions for MCP integration
GRANT ALL PRIVILEGES ON leantime_db.* TO 'leantime_user'@'%';

-- Create indexes for performance optimization
-- These will be created by Leantime installer, but we prepare the structure

-- Create a table to track Dopemux integration status
CREATE TABLE IF NOT EXISTS dopemux_integration_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    component VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    sync_count INT DEFAULT 0,
    error_message TEXT,
    INDEX idx_component (component),
    INDEX idx_status (status),
    INDEX idx_last_sync (last_sync)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert initial integration tracking records
INSERT IGNORE INTO dopemux_integration_status (component, status) VALUES
('task_master_ai', 'pending'),
('mcp_bridge', 'pending'),
('adhd_optimizations', 'enabled'),
('context_preservation', 'enabled');

-- Create table for ADHD-specific user preferences
CREATE TABLE IF NOT EXISTS dopemux_adhd_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    attention_pattern VARCHAR(50) DEFAULT 'adaptive',
    break_interval INT DEFAULT 25,
    context_switch_buffer INT DEFAULT 10,
    notification_batch_size INT DEFAULT 5,
    focus_mode_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create table for task decomposition tracking
CREATE TABLE IF NOT EXISTS dopemux_task_decomposition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    ai_provider VARCHAR(50),
    complexity_score DECIMAL(3,2),
    estimated_effort_hours DECIMAL(5,2),
    dependency_map JSON,
    decomposition_metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_task_id (task_id),
    INDEX idx_complexity (complexity_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Flush privileges to ensure changes take effect
FLUSH PRIVILEGES;