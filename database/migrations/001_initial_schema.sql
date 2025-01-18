-- Initial schema for core evaluation tables

-- Model Registry
CREATE TABLE model_registry (
    model_id VARCHAR(36) PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    model_version VARCHAR(100) NOT NULL,
    provider_type VARCHAR(50) NOT NULL,
    provider_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    model_architecture VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deprecated_at TIMESTAMP,
    UNIQUE(model_name, model_version)
);

-- Unit Test Suites
CREATE TABLE unit_test_suites (
    suite_id VARCHAR(36) PRIMARY KEY,
    suite_name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    priority INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP,
    UNIQUE(suite_name)
);

-- Unit Tests
CREATE TABLE unit_tests (
    test_id VARCHAR(36) PRIMARY KEY,
    suite_id VARCHAR(36) REFERENCES unit_test_suites(suite_id),
    test_name VARCHAR(255) NOT NULL,
    test_type VARCHAR(100) NOT NULL,
    test_description TEXT,
    input_data TEXT,  -- JSON stored as TEXT in SQLite
    expected_output TEXT,  -- JSON stored as TEXT in SQLite
    compliance_rules TEXT,  -- JSON stored as TEXT in SQLite
    timeout_seconds INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP,
    UNIQUE(suite_id, test_name)
);

-- Unit Test Runs
CREATE TABLE unit_test_runs (
    run_id VARCHAR(36) PRIMARY KEY,
    test_id VARCHAR(36) REFERENCES unit_tests(test_id),
    model_id VARCHAR(36) REFERENCES model_registry(model_id),
    run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    execution_time INTEGER,  -- Store interval as integer milliseconds
    actual_output TEXT,  -- JSON stored as TEXT in SQLite
    error_message TEXT,
    stack_trace TEXT,
    environment_info TEXT  -- JSON stored as TEXT in SQLite
);

-- Create indexes for better query performance
CREATE INDEX idx_model_registry_provider ON model_registry(provider_type, provider_name);
CREATE INDEX idx_unit_test_runs_status ON unit_test_runs(status);
CREATE INDEX idx_unit_test_runs_timestamp ON unit_test_runs(run_timestamp);