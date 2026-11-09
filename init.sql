create table if not exists jobs (
    job_id CHAR(36) PRIMARY KEY,
    status ENUM('pending', 'processing', 'completed', 'failed', 'review') NOT NULL DEFAULT 'pending' ,
    file_hash CHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_jobs_file_hash (file_hash)
);

create table documents (
    document_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id CHAR(36) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (job_id)
    REFERENCES jobs(job_id)
    ON DELETE CASCADE
);

create table ocr_results (
    ocr_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id CHAR(36) NOT NULL,
    raw_text LONGTEXT,
    confidence DECIMAL(5,2),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (job_id)
    REFERENCES jobs(job_id)
    ON DELETE CASCADE
);

create table extractions (
    extraction_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id CHAR(36) NOT NULL,
    extracted_data JSON,
    model_used VARCHAR(100),
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (job_id)
    REFERENCES jobs(job_id)
    ON DELETE CASCADE
);

create table validation_results (
    validation_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id CHAR(36) NOT NULL,
    is_valid BOOLEAN NOT NULL,
    errors JSON,
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (job_id)
    REFERENCES jobs(job_id)
    ON DELETE CASCADE
);

create table events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id CHAR(36) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (job_id)
    REFERENCES jobs(job_id)
    ON DELETE CASCADE
);

create table workflows (
    workflow_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    definition JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

create table workflow_steps (
    step_id INT AUTO_INCREMENT PRIMARY KEY,
    workflow_id INT NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    step_type VARCHAR(100) NOT NULL,
    order_index INT NOT NULL,
    config JSON,
    depends_on JSON,

    FOREIGN KEY (workflow_id)
    REFERENCES workflows(workflow_id)
);

create table workflow_runs (
    run_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id CHAR(36) NOT NULL,
    workflow_id INT NOT NULL,
    status ENUM('pending', 'running', 'completed', 'failed') NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,

    FOREIGN KEY (workflow_id)
    REFERENCES workflows(workflow_id),

    FOREIGN KEY (job_id)
    REFERENCES jobs(job_id)
    ON DELETE CASCADE
);

create table step_runs (
    step_run_id INT AUTO_INCREMENT PRIMARY KEY,
    run_id INT NOT NULL,
    step_id INT NOT NULL,
    status ENUM('pending', 'running', 'completed', 'failed') NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    result JSON,
    error_message TEXT,
    retry_count INT NOT NULL DEFAULT 0,

    FOREIGN KEY (run_id)
    REFERENCES workflow_runs(run_id)
    ON DELETE CASCADE,

    FOREIGN KEY (step_id)
    REFERENCES workflow_steps(step_id)
);

