-- ============================================================
--  TIMETABLING SYSTEM — SQLite Schema (Improved)
-- ============================================================

PRAGMA foreign_keys = ON;

-- =============================================
-- Core Entities
-- =============================================

CREATE TABLE IF NOT EXISTS departments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    code        TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS lecture_halls (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    capacity    INTEGER NOT NULL CHECK (capacity > 0)
);

CREATE TABLE IF NOT EXISTS trainers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id   INTEGER NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
    full_name       TEXT NOT NULL,
    email           TEXT UNIQUE,
    CHECK (full_name <> '')
);

CREATE TABLE IF NOT EXISTS courses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id   INTEGER NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
    name            TEXT NOT NULL,
    code            TEXT NOT NULL UNIQUE,
    CHECK (name <> '' AND code <> '')
);

CREATE TABLE IF NOT EXISTS intakes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id       INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    label           TEXT NOT NULL,           -- e.g. "Jan 2026 Intake"
    student_count   INTEGER NOT NULL DEFAULT 0 CHECK (student_count >= 0),
    academic_year   TEXT NOT NULL,           -- e.g. "2025/2026"
    UNIQUE(course_id, label)
);

CREATE TABLE IF NOT EXISTS timeslots (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    day_of_week     TEXT NOT NULL CHECK (day_of_week IN ('Monday','Tuesday','Wednesday','Thursday','Friday')),
    session_number  INTEGER NOT NULL CHECK (session_number BETWEEN 1 AND 4),
    start_time      TEXT NOT NULL,
    end_time        TEXT NOT NULL,
    UNIQUE(day_of_week, session_number)
);

CREATE TABLE IF NOT EXISTS units (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id       INTEGER NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
    name                TEXT NOT NULL,
    code                TEXT NOT NULL UNIQUE,
    hours_per_week      INTEGER NOT NULL DEFAULT 2 CHECK (hours_per_week > 0),
    is_shared           INTEGER NOT NULL DEFAULT 0 CHECK (is_shared IN (0,1))
);

-- Shared units across departments
CREATE TABLE IF NOT EXISTS unit_shared_departments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id         INTEGER NOT NULL REFERENCES units(id) ON DELETE CASCADE,
    department_id   INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    UNIQUE(unit_id, department_id)
);

-- Trainers assigned to teach a unit
CREATE TABLE IF NOT EXISTS unit_trainers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id         INTEGER NOT NULL REFERENCES units(id) ON DELETE CASCADE,
    trainer_id      INTEGER NOT NULL REFERENCES trainers(id) ON DELETE CASCADE,
    UNIQUE(unit_id, trainer_id)
);

-- =============================================
-- Main Timetable Table
-- =============================================

CREATE TABLE IF NOT EXISTS timetable_entries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id         INTEGER NOT NULL REFERENCES units(id) ON DELETE CASCADE,
    trainer_id      INTEGER NOT NULL REFERENCES trainers(id) ON DELETE RESTRICT,
    hall_id         INTEGER NOT NULL REFERENCES lecture_halls(id) ON DELETE RESTRICT,
    intake_id       INTEGER NOT NULL REFERENCES intakes(id) ON DELETE CASCADE,
    timeslot_id     INTEGER NOT NULL REFERENCES timeslots(id) ON DELETE RESTRICT,

    -- Prevent double-booking
    UNIQUE(trainer_id, timeslot_id),   -- One trainer per timeslot
    UNIQUE(hall_id,    timeslot_id),   -- One hall per timeslot
    UNIQUE(intake_id,  timeslot_id)    -- One class per intake per timeslot
);

-- =============================================
-- Seed Data: Timeslots (Mon–Fri, 4 sessions)
-- =============================================

INSERT OR IGNORE INTO timeslots (day_of_week, session_number, start_time, end_time) VALUES
    ('Monday',    1, '08:00', '10:00'),
    ('Monday',    2, '10:30', '12:30'),
    ('Monday',    3, '14:00', '16:00'),
    ('Monday',    4, '16:30', '18:30'),   -- Fixed: was overlapping before

    ('Tuesday',   1, '08:00', '10:00'),
    ('Tuesday',   2, '10:30', '12:30'),
    ('Tuesday',   3, '14:00', '16:00'),
    ('Tuesday',   4, '16:30', '18:30'),

    ('Wednesday', 1, '08:00', '10:00'),
    ('Wednesday', 2, '10:30', '12:30'),
    ('Wednesday', 3, '14:00', '16:00'),
    ('Wednesday', 4, '16:30', '18:30'),

    ('Thursday',  1, '08:00', '10:00'),
    ('Thursday',  2, '10:30', '12:30'),
    ('Thursday',  3, '14:00', '16:00'),
    ('Thursday',  4, '16:30', '18:30'),

    ('Friday',    1, '08:00', '10:00'),
    ('Friday',    2, '10:30', '12:30'),
    ('Friday',    3, '14:00', '16:00'),
    ('Friday',    4, '16:30', '18:30');

    -- =============================================
-- Link Intakes to Units (Many-to-Many)
-- =============================================
CREATE TABLE IF NOT EXISTS intake_units (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    intake_id       INTEGER NOT NULL REFERENCES intakes(id) ON DELETE CASCADE,
    unit_id         INTEGER NOT NULL REFERENCES units(id) ON DELETE CASCADE,
    UNIQUE(intake_id, unit_id)
);

-- Optional: Add some sample data later if needed