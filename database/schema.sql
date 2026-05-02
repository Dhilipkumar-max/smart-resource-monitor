-- Create database (Commented out for Railway compatibility)
-- CREATE DATABASE IF NOT EXISTS live_resource_monitor;
-- USE live_resource_monitor;

-- System metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cpu_usage DECIMAL(5,2) NOT NULL,
    memory_usage DECIMAL(5,2) NOT NULL,
    available_memory DECIMAL(8,2) NOT NULL,
    
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB;

-- Application metrics table
CREATE TABLE IF NOT EXISTS app_metrics (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    app_name VARCHAR(255) NOT NULL,
    pid INT UNSIGNED NOT NULL,
    cpu_usage DECIMAL(5,2) NOT NULL,
    memory_usage DECIMAL(10,2) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    system_metric_id INT UNSIGNED,
    
    FOREIGN KEY (system_metric_id) 
        REFERENCES system_metrics(id) 
        ON DELETE CASCADE,
    
    INDEX idx_app_name (app_name),
    INDEX idx_app_timestamp (app_name, timestamp),
    INDEX idx_pid (pid),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB;

-- Optional: Create view for easy querying
CREATE OR REPLACE VIEW current_resource_status AS
SELECT 
    s.timestamp,
    s.cpu_usage as system_cpu,
    s.memory_usage as system_memory,
    a.app_name,
    a.cpu_usage as app_cpu,
    a.memory_usage as app_memory
FROM system_metrics s
LEFT JOIN app_metrics a ON s.id = a.system_metric_id
WHERE s.timestamp >= NOW() - INTERVAL 5 MINUTE
ORDER BY s.timestamp DESC, a.cpu_usage DESC;
