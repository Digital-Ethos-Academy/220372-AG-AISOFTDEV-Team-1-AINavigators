-- StaffAlloc SQLite Schema
-- Version: 1.0
-- Author: Senior Data Architect
--
-- This schema is designed for the StaffAlloc application, optimized for a local-first
-- prototype using SQLite. It covers core entities, relationships, and constraints
-- derived from the PRD and architecture narrative.

-- Enable foreign key constraint enforcement.
PRAGMA foreign_keys = ON;

--------------------------------------------------------------------------------
-- CORE ENTITIES
--------------------------------------------------------------------------------

-- Table: users
-- Stores information about all employees and application users.
-- The system_role column is used for Role-Based Access Control (RBAC).
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    system_role TEXT NOT NULL CHECK(system_role IN ('Admin', 'Director', 'PM', 'Employee')),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    last_login_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: roles
-- A standardized list of job roles (e.g., 'SW Engineer', 'Data Scientist').
-- Managed by Admins (US018).
CREATE TABLE roles (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: lcats
-- A standardized list of Labor Categories (e.g., 'Level 1', 'Senior Consultant').
-- Managed by Admins (US018).
CREATE TABLE lcats (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: projects
-- Represents a single project with its core metadata.
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE,
    client TEXT,
    start_date TEXT NOT NULL, -- ISO 8601 format: 'YYYY-MM-DD'
    sprints INTEGER NOT NULL CHECK(sprints > 0),
    manager_id INTEGER, -- The primary PM for the project
    status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Planning', 'Active', 'Closed', 'On Hold')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Table: project_assignments
-- This is a crucial link table. It represents an employee being staffed on a project.
-- It holds the context for the assignment, such as their role and total funded hours for that project.
CREATE TABLE project_assignments (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    lcat_id INTEGER NOT NULL,
    funded_hours INTEGER NOT NULL CHECK(funded_hours >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(project_id, user_id), -- An employee can only be assigned to a project once.
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT,
    FOREIGN KEY (lcat_id) REFERENCES lcats(id) ON DELETE RESTRICT
);

-- Table: allocations
-- This is the central table for the allocation grid, storing the number of hours
-- an employee is allocated for a specific month on a specific project assignment.
-- It is designed to be tall and narrow for efficient querying and aggregation.
CREATE TABLE allocations (
    id INTEGER PRIMARY KEY,
    project_assignment_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK(month >= 1 AND month <= 12),
    allocated_hours INTEGER NOT NULL CHECK(allocated_hours >= 0),

    UNIQUE(project_assignment_id, year, month), -- Can only have one allocation entry per assignment per month.
    FOREIGN KEY (project_assignment_id) REFERENCES project_assignments(id) ON DELETE CASCADE
);

-- Table: monthly_hour_overrides
-- Stores project-specific overrides for the standard number of work hours in a month (US007).
-- If an entry exists here, its value should be used instead of a system-wide calculation.
CREATE TABLE monthly_hour_overrides (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK(month >= 1 AND month <= 12),
    overridden_hours INTEGER NOT NULL CHECK(overridden_hours > 0),

    UNIQUE(project_id, year, month),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

--------------------------------------------------------------------------------
-- AI & METADATA TABLES
--------------------------------------------------------------------------------

-- Table: ai_rag_cache
-- Stores pre-computed text documents for the Retrieval-Augmented Generation (RAG) feature.
-- This table is populated by a background process and used by the AI to answer user queries.
CREATE TABLE ai_rag_cache (
    id INTEGER PRIMARY KEY,
    source_entity TEXT NOT NULL, -- e.g., 'project', 'user', 'allocation_summary'
    source_id INTEGER NOT NULL,
    document_text TEXT NOT NULL,
    last_indexed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(source_entity, source_id)
);

-- Table: ai_recommendations
-- A generic table to store outputs from the AI agent, such as staffing recommendations,
-- conflict resolutions, or workload balancing suggestions.
CREATE TABLE ai_recommendations (
    id INTEGER PRIMARY KEY,
    recommendation_type TEXT NOT NULL CHECK(recommendation_type IN ('STAFFING', 'CONFLICT_RESOLUTION', 'FORECAST', 'WORKLOAD_BALANCE')),
    context_json TEXT, -- JSON blob with relevant data, e.g., {'project_id': 1, 'role_id': 5}
    recommendation_text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending', 'Accepted', 'Rejected', 'Dismissed')),
    generated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    acted_upon_at TEXT
);

-- Table: audit_log
-- A simple audit trail for significant events in the system.
-- While not explicitly in the PRD, this is a best practice for traceability.
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    action TEXT NOT NULL, -- e.g., 'PROJECT_CREATE', 'ALLOCATION_UPDATE'
    entity_type TEXT, -- e.g., 'project', 'allocation', 'user'
    entity_id INTEGER, -- The ID of the entity being acted upon
    details TEXT, -- JSON blob with before/after values or context
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);


--------------------------------------------------------------------------------
-- INDEXES FOR QUERY OPTIMIZATION
--------------------------------------------------------------------------------

-- Indexes on foreign keys and frequently queried columns are critical for performance,
-- especially for dashboard loading and real-time grid validation.

-- Users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_system_role ON users(system_role);

-- Projects table
CREATE INDEX idx_projects_manager_id ON projects(manager_id);
CREATE INDEX idx_projects_status ON projects(status);

-- Project Assignments table
CREATE INDEX idx_project_assignments_project_id ON project_assignments(project_id);
CREATE INDEX idx_project_assignments_user_id ON project_assignments(user_id); -- Crucial for employee timeline view (US012)
CREATE INDEX idx_project_assignments_role_id ON project_assignments(role_id);

-- Allocations table
CREATE INDEX idx_allocations_project_assignment_id ON allocations(project_assignment_id);
CREATE INDEX idx_allocations_year_month ON allocations(year, month); -- Crucial for cross-project FTE checks (US006)

-- Monthly Hour Overrides table
CREATE INDEX idx_monthly_hour_overrides_project_year_month ON monthly_hour_overrides(project_id, year, month);

-- AI RAG Cache table
CREATE INDEX idx_ai_rag_cache_source ON ai_rag_cache(source_entity, source_id);

-- Audit Log table
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);


--------------------------------------------------------------------------------
-- VIEWS FOR ANALYTICS & SIMPLIFIED QUERIES
--------------------------------------------------------------------------------

-- View: v_allocation_details
-- A denormalized view that combines all core allocation information.
-- This simplifies many front-end and back-end queries.
CREATE VIEW v_allocation_details AS
SELECT
    a.id AS allocation_id,
    a.year,
    a.month,
    a.allocated_hours,
    p.id AS project_id,
    p.name AS project_name,
    p.code AS project_code,
    u.id AS user_id,
    u.full_name AS user_name,
    u.email AS user_email,
    r.id AS role_id,
    r.name AS role_name,
    l.id AS lcat_id,
    l.name AS lcat_name,
    pa.id AS project_assignment_id,
    pa.funded_hours
FROM allocations a
JOIN project_assignments pa ON a.project_assignment_id = pa.id
JOIN projects p ON pa.project_id = p.id
JOIN users u ON pa.user_id = u.id
JOIN roles r ON pa.role_id = r.id
JOIN lcats l ON pa.lcat_id = l.id;


-- View: v_monthly_user_summary
-- This view is a candidate for materialization in a more advanced database.
-- It calculates the total hours allocated for each user across all their projects for each month.
-- This is the primary data source for checking cross-project over-allocations (US006)
-- and for powering portfolio-level dashboards (US011, US012).
CREATE VIEW v_monthly_user_summary AS
SELECT
    pa.user_id,
    u.full_name,
    a.year,
    a.month,
    SUM(a.allocated_hours) AS total_monthly_hours
FROM allocations a
JOIN project_assignments pa ON a.project_assignment_id = pa.id
JOIN users u ON pa.user_id = u.id
GROUP BY
    pa.user_id,
    u.full_name,
    a.year,
    a.month;


--------------------------------------------------------------------------------
-- SEED DATA
--------------------------------------------------------------------------------

-- Justified by US018, which requires a standardized list of Roles and LCATs.
-- Seeding these tables ensures consistency from the start.

INSERT INTO roles (name, description) VALUES
('Project Manager', 'Manages project timelines, resources, and budget.'),
('SW Engineer', 'Designs, develops, and maintains software systems.'),
('QA Engineer', 'Ensures software quality through manual and automated testing.'),
('Cyber Analyst', 'Monitors and protects information systems.'),
('Data Scientist', 'Analyzes complex data to extract insights and build models.'),
('UX/UI Designer', 'Designs user interfaces and improves user experience.');

INSERT INTO lcats (name, description) VALUES
('Level 1', 'Entry-level professional with 0-2 years of experience.'),
('Level 2', 'Mid-level professional with 2-5 years of experience.'),
('Level 3', 'Senior professional with 5-10 years of experience.'),
('Principal', 'Expert-level professional with 10+ years of experience.');

-- Seed a default Admin user for initial setup.
-- Default password is 'admin123' (MUST be changed in production).
-- Password hash generated with bcrypt (rounds=12).
INSERT INTO users (email, full_name, password_hash, system_role, is_active) VALUES
('admin@staffalloc.com', 'Admin User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyB3nJXvDXh2', 'Admin', 1);