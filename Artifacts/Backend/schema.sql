-- TripSplit SQLite Schema
-- Author: Senior Data Architect
-- Version: 1.0
-- Date: 2023-10-27
--
-- This schema is designed for SQLite and reflects the requirements outlined in the
-- TripSplit Product Requirements Document (PRD) and architecture narrative.
--
-- Design Choices & Conventions:
-- 1.  `id` columns are INTEGER PRIMARY KEY for auto-incrementing behavior (ROWID alias).
-- 2.  Timestamps are stored as TEXT in ISO8601 format (YYYY-MM-DD HH:MM:SS) for readability.
--     `CURRENT_TIMESTAMP` is used for default values.
-- 3.  Currency amounts are stored as INTEGERs in the smallest denomination (e.g., cents)
--     to avoid floating-point inaccuracies.
-- 4.  Foreign key constraints are enabled and include `ON DELETE` clauses to maintain
--     referential integrity.
-- 5.  Indexes are created on foreign keys and frequently queried columns to optimize performance.
-- 6.  Comments explain non-obvious constraints, relationships, and design decisions.

-- Enable foreign key support in SQLite
PRAGMA foreign_keys = ON;

--------------------------------------------------------------------------------
-- Core Entities: Users, Trips, and Participants
--------------------------------------------------------------------------------

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now'))
);

-- Trigger to update the 'updated_at' timestamp on users table changes
CREATE TRIGGER users_updated_at
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    UPDATE users SET updated_at = strftime('%Y-%m-%d %H:%M:%S', 'now') WHERE id = OLD.id;
END;

CREATE TABLE trips (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    owner_user_id INTEGER NOT NULL,
    base_currency TEXT NOT NULL CHECK (length(base_currency) = 3), -- ISO 4217 currency code (e.g., 'USD')
    start_date TEXT, -- YYYY-MM-DD
    end_date TEXT,   -- YYYY-MM-DD
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'settled', 'archived')),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),
    FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE RESTRICT,
    CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date)
);

-- Trigger to update the 'updated_at' timestamp on trips table changes
CREATE TRIGGER trips_updated_at
AFTER UPDATE ON trips
FOR EACH ROW
BEGIN
    UPDATE trips SET updated_at = strftime('%Y-%m-%d %H:%M:%S', 'now') WHERE id = OLD.id;
END;

CREATE TABLE participants (
    id INTEGER PRIMARY KEY,
    trip_id INTEGER NOT NULL,
    user_id INTEGER, -- Nullable for non-account "guest" participants
    display_name TEXT NOT NULL, -- Name used within the trip context
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),

    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    -- If a user deletes their account, we keep their participant record for financial history,
    -- but sever the link to the user account.
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,

    -- A user can only be a participant in a trip once.
    UNIQUE (trip_id, user_id),
    -- A guest's display name must be unique within a single trip.
    UNIQUE (trip_id, display_name)
);

--------------------------------------------------------------------------------
-- Expense Tracking Entities
--------------------------------------------------------------------------------

CREATE TABLE expense_categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    icon_name TEXT -- For UI display
);

CREATE TABLE expenses (
    id INTEGER PRIMARY KEY,
    trip_id INTEGER NOT NULL,
    payer_participant_id INTEGER NOT NULL,
    category_id INTEGER,
    description TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    currency TEXT NOT NULL CHECK (length(currency) = 3),
    expense_date TEXT NOT NULL, -- YYYY-MM-DD
    local_uuid TEXT UNIQUE, -- Client-generated UUID for offline sync and idempotency
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),

    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    FOREIGN KEY (payer_participant_id) REFERENCES participants(id) ON DELETE RESTRICT,
    FOREIGN KEY (category_id) REFERENCES expense_categories(id) ON DELETE SET NULL,

    CHECK (amount_cents > 0)
);

-- Trigger to update the 'updated_at' timestamp on expenses table changes
CREATE TRIGGER expenses_updated_at
AFTER UPDATE ON expenses
FOR EACH ROW
BEGIN
    UPDATE expenses SET updated_at = strftime('%Y-%m-%d %H:%M:%S', 'now') WHERE id = OLD.id;
END;

CREATE TABLE expense_splits (
    id INTEGER PRIMARY KEY,
    expense_id INTEGER NOT NULL,
    participant_id INTEGER NOT NULL,
    amount_owed_cents INTEGER NOT NULL,
    -- The application layer is responsible for ensuring that the sum of splits for an
    -- expense equals the total expense amount. A database trigger could enforce this
    -- but would add significant complexity.

    FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE,
    FOREIGN KEY (participant_id) REFERENCES participants(id) ON DELETE RESTRICT,

    CHECK (amount_owed_cents > 0),
    UNIQUE (expense_id, participant_id)
);

CREATE TABLE receipts (
    id INTEGER PRIMARY KEY,
    expense_id INTEGER NOT NULL UNIQUE, -- Enforces one receipt per expense
    storage_path TEXT NOT NULL, -- Path to the file in local storage/S3
    mime_type TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    uploaded_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),

    FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE
);

--------------------------------------------------------------------------------
-- Settlement & Payment Entities
--------------------------------------------------------------------------------

CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    trip_id INTEGER NOT NULL,
    payer_participant_id INTEGER NOT NULL,
    receiver_participant_id INTEGER NOT NULL,
    amount_cents INTEGER NOT NULL,
    payment_date TEXT NOT NULL, -- YYYY-MM-DD
    method TEXT DEFAULT 'manual' CHECK (method IN ('manual', 'venmo', 'paypal')), -- For future integrations
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),

    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    FOREIGN KEY (payer_participant_id) REFERENCES participants(id) ON DELETE RESTRICT,
    FOREIGN KEY (receiver_participant_id) REFERENCES participants(id) ON DELETE RESTRICT,

    CHECK (amount_cents > 0),
    CHECK (payer_participant_id != receiver_participant_id)
);

--------------------------------------------------------------------------------
-- AI & Audit Entities
--------------------------------------------------------------------------------

CREATE TABLE ai_rag_cache (
    id INTEGER PRIMARY KEY,
    trip_id INTEGER NOT NULL,
    query_hash TEXT NOT NULL UNIQUE, -- MD5/SHA256 hash of the user's query text
    response_text TEXT NOT NULL,
    context_hash TEXT NOT NULL, -- Hash of the underlying data to detect staleness
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),
    last_accessed_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),

    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

CREATE TABLE ai_categorization_feedback (
    id INTEGER PRIMARY KEY,
    expense_id INTEGER NOT NULL UNIQUE, -- One feedback entry per expense
    suggested_category_id INTEGER,
    user_chosen_category_id INTEGER,
    was_suggestion_accepted INTEGER NOT NULL CHECK (was_suggestion_accepted IN (0, 1)), -- BOOLEAN: 0=false, 1=true
    feedback_timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),

    FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE,
    FOREIGN KEY (suggested_category_id) REFERENCES expense_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (user_chosen_category_id) REFERENCES expense_categories(id) ON DELETE SET NULL
);

--------------------------------------------------------------------------------
-- Indexes for Performance Optimization
--------------------------------------------------------------------------------

-- Index for trips owned by a user
CREATE INDEX idx_trips_owner_user_id ON trips(owner_user_id);

-- Indexes for participants table to quickly find participants of a trip or a user's trips
CREATE INDEX idx_participants_trip_id ON participants(trip_id);
CREATE INDEX idx_participants_user_id ON participants(user_id);

-- Indexes for expenses table for fast lookups by trip and payer
CREATE INDEX idx_expenses_trip_id ON expenses(trip_id);
CREATE INDEX idx_expenses_payer_participant_id ON expenses(payer_participant_id);
CREATE INDEX idx_expenses_category_id ON expenses(category_id);
CREATE INDEX idx_expenses_expense_date ON expenses(expense_date);

-- Indexes for expense_splits for balance calculations
CREATE INDEX idx_expense_splits_expense_id ON expense_splits(expense_id);
CREATE INDEX idx_expense_splits_participant_id ON expense_splits(participant_id);

-- Indexes for payments for settlement history
CREATE INDEX idx_payments_trip_id ON payments(trip_id);
CREATE INDEX idx_payments_payer_participant_id ON payments(payer_participant_id);
CREATE INDEX idx_payments_receiver_participant_id ON payments(receiver_participant_id);

-- Index for AI cache
CREATE INDEX idx_ai_rag_cache_trip_id ON ai_rag_cache(trip_id);

--------------------------------------------------------------------------------
-- Views for Analytics and Simplified Queries
--------------------------------------------------------------------------------

-- This view is a candidate for materialization in a more advanced database system.
-- In SQLite, it serves as a powerful, reusable query for calculating real-time balances.
-- It forms the backbone for the dashboard, settlement recommendations, and RAG queries.
CREATE VIEW v_participant_balances AS
WITH
total_paid AS (
    -- Calculate the total amount each participant has paid for expenses in each trip
    SELECT
        p.trip_id,
        p.id AS participant_id,
        COALESCE(SUM(e.amount_cents), 0) AS total_paid_cents
    FROM
        participants p
    LEFT JOIN
        expenses e ON p.id = e.payer_participant_id
    GROUP BY
        p.trip_id, p.id
),
total_owed AS (
    -- Calculate the total amount each participant owes from expense splits in each trip
    SELECT
        p.trip_id,
        p.id AS participant_id,
        COALESCE(SUM(es.amount_owed_cents), 0) AS total_owed_cents
    FROM
        participants p
    LEFT JOIN
        expense_splits es ON p.id = es.participant_id
    GROUP BY
        p.trip_id, p.id
),
total_settled_paid AS (
    -- Calculate the total amount each participant has paid in settlements
    SELECT
        p.trip_id,
        p.id AS participant_id,
        COALESCE(SUM(pm.amount_cents), 0) AS total_settled_paid_cents
    FROM
        participants p
    LEFT JOIN
        payments pm ON p.id = pm.payer_participant_id
    GROUP BY
        p.trip_id, p.id
),
total_settled_received AS (
    -- Calculate the total amount each participant has received in settlements
    SELECT
        p.trip_id,
        p.id AS participant_id,
        COALESCE(SUM(pm.amount_cents), 0) AS total_settled_received_cents
    FROM
        participants p
    LEFT JOIN
        payments pm ON p.id = pm.receiver_participant_id
    GROUP BY
        p.trip_id, p.id
)
SELECT
    p.id AS participant_id,
    p.trip_id,
    p.display_name,
    p.user_id,
    tp.total_paid_cents,
    to.total_owed_cents,
    tsp.total_settled_paid_cents,
    tsr.total_settled_received_cents,
    -- Net Balance = (Paid for others + Received in settlements) - (Owed for self + Paid in settlements)
    (tp.total_paid_cents + tsr.total_settled_received_cents) - (to.total_owed_cents + tsp.total_settled_paid_cents) AS net_balance_cents
FROM
    participants p
JOIN
    total_paid tp ON p.id = tp.participant_id
JOIN
    total_owed to ON p.id = to.participant_id
JOIN
    total_settled_paid tsp ON p.id = tsp.participant_id
JOIN
    total_settled_received tsr ON p.id = tsr.participant_id;


--------------------------------------------------------------------------------
-- Seed Data
-- Justified by the PRD's requirement for smart categorization, which implies a
-- predefined list of common categories for the AI to suggest from.
--------------------------------------------------------------------------------

INSERT INTO expense_categories (name, icon_name) VALUES
    ('Food & Drink', 'utensils'),
    ('Accommodation', 'hotel'),
    ('Transport', 'car'),
    ('Activities', 'ticket-alt'),
    ('Shopping', 'shopping-bag'),
    ('Groceries', 'shopping-cart'),
    ('Flights', 'plane'),
    ('Fees & Charges', 'file-invoice-dollar'),
    ('Entertainment', 'film'),
    ('Miscellaneous', 'question-circle');

-- End of schema file