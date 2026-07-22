-- Database Schema for AI Agent System
-- This schema supports multi-agent workflow orchestration

-- Agents table: stores registered agent information
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    model_name TEXT DEFAULT 'qwen2.5',
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    config_json TEXT DEFAULT '{}'
);

-- Tasks table: stores workflow tasks
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,
    parent_task_id TEXT,
    type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    priority INTEGER DEFAULT 0,
    payload TEXT NOT NULL,
    result TEXT,
    error_message TEXT,
    assigned_agent TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (assigned_agent) REFERENCES agents(name)
);

-- Workflow executions table: tracks complete workflow runs
CREATE TABLE IF NOT EXISTS workflow_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT UNIQUE NOT NULL,
    workflow_name TEXT NOT NULL,
    status TEXT DEFAULT 'running',
    total_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    failed_tasks INTEGER DEFAULT 0,
    started_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT,
    metadata_json TEXT DEFAULT '{}'
);

-- Agent metrics table: performance tracking
CREATE TABLE IF NOT EXISTS agent_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    timestamp TEXT DEFAULT (datetime('now')),
    tasks_completed INTEGER DEFAULT 0,
    avg_response_time_ms REAL DEFAULT 0.0,
    error_count INTEGER DEFAULT 0,
    token_usage INTEGER DEFAULT 0,
    FOREIGN KEY (agent_name) REFERENCES agents(name)
);

-- Prompts library: reusable prompt templates
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT DEFAULT 'general',
    template TEXT NOT NULL,
    variables_json TEXT DEFAULT '[]',
    version TEXT DEFAULT '1.0.0',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Audit log: comprehensive activity tracking
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT (datetime('now')),
    event_type TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    action TEXT NOT NULL,
    user_id TEXT,
    details_json TEXT DEFAULT '{}',
    ip_address TEXT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_timestamp ON agent_metrics(timestamp, agent_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_event_type ON audit_log(event_type);

-- Insert default agents
INSERT OR IGNORE INTO agents (name, type, model_name) VALUES 
    ('code_generator', 'generation', 'qwen2.5-coder'),
    ('refactoring', 'analysis', 'qwen2.5-coder'),
    ('code_view', 'analysis', 'qwen2.5'),
    ('testing', 'generation', 'qwen2.5-coder'),
    ('bug_detection', 'analysis', 'qwen2.5-coder'),
    ('documentation', 'generation', 'qwen2.5'),
    ('migration', 'operations', 'qwen2.5'),
    ('devops', 'operations', 'qwen2.5'),
    ('release', 'operations', 'qwen2.5');

-- Insert default prompts
INSERT OR IGNORE INTO prompts (name, category, template, variables_json) VALUES
    ('code_generation', 'development', 'Generate {{language}} code that {{description}}. Follow best practices and include error handling.', '["language", "description"]'),
    ('code_review', 'analysis', 'Review this {{language}} code for bugs, security issues, and performance problems:\n\n{{code}}', '["language", "code"]'),
    ('test_generation', 'testing', 'Write comprehensive tests for this {{language}} function:\n\n{{code}}\n\nInclude edge cases and error scenarios.', '["language", "code"]'),
    ('documentation', 'documentation', 'Write clear documentation for this {{type}}:\n\n{{content}}\n\nInclude usage examples.', '["type", "content"]');
