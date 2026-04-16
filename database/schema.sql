-- ============================================================
--  TIMETABLING SYSTEM — Final Customized Schema
-- ============================================================

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS departments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    code        TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS lecture_halls (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE,
    capacity      INTEGER NOT NULL CHECK (capacity > 0)
);

CREATE TABLE IF NOT EXISTS trainers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id   INTEGER NOT NULL REFERENCES departments(id),
    full_name       TEXT NOT NULL,
    email           TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS courses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id   INTEGER NOT NULL REFERENCES departments(id),
    name            TEXT NOT NULL,
    code            TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS intakes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id       INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    label           TEXT NOT NULL,
    academic_year   TEXT NOT NULL DEFAULT '2025/2026',
    UNIQUE(course_id, label)
);

CREATE TABLE IF NOT EXISTS timeslots (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    day_of_week     TEXT NOT NULL,
    session_number  INTEGER NOT NULL,
    start_time      TEXT NOT NULL,
    end_time        TEXT NOT NULL,
    UNIQUE(day_of_week, session_number)
);

CREATE TABLE IF NOT EXISTS units (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id       INTEGER NOT NULL REFERENCES departments(id),
    name                TEXT NOT NULL,
    code                TEXT,
    hours_per_week      INTEGER DEFAULT 3
);

CREATE TABLE IF NOT EXISTS intake_units (
    intake_id   INTEGER REFERENCES intakes(id) ON DELETE CASCADE,
    unit_id     INTEGER REFERENCES units(id) ON DELETE CASCADE,
    PRIMARY KEY (intake_id, unit_id)
);

CREATE TABLE IF NOT EXISTS timetable_entries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id         INTEGER NOT NULL REFERENCES units(id),
    trainer_id      INTEGER NOT NULL REFERENCES trainers(id),
    hall_id         INTEGER NOT NULL REFERENCES lecture_halls(id),
    intake_id       INTEGER NOT NULL REFERENCES intakes(id),
    timeslot_id     INTEGER NOT NULL REFERENCES timeslots(id),

    UNIQUE(trainer_id, timeslot_id),
    UNIQUE(hall_id,    timeslot_id),
    UNIQUE(intake_id,  timeslot_id)
);

-- =============================================
-- Seed Timeslots (Matching your draft)
-- =============================================
INSERT OR IGNORE INTO timeslots (day_of_week, session_number, start_time, end_time) VALUES
('Monday',    1, '08:00', '09:30'), ('Monday',    2, '10:30', '12:00'),
('Monday',    3, '13:00', '14:30'), ('Monday',    4, '15:00', '16:30'),
('Tuesday',   1, '08:00', '09:30'), ('Tuesday',   2, '10:30', '12:00'),
('Tuesday',   3, '13:00', '14:30'), ('Tuesday',   4, '15:00', '16:30'),
('Wednesday', 1, '08:00', '09:30'), ('Wednesday', 2, '10:30', '12:00'),
('Wednesday', 3, '13:00', '14:30'), ('Wednesday', 4, '15:00', '16:30'),
('Thursday',  1, '08:00', '09:30'), ('Thursday',  2, '10:30', '12:00'),
('Thursday',  3, '13:00', '14:30'), ('Thursday',  4, '15:00', '16:30'),
('Friday',    1, '08:00', '09:30'), ('Friday',    2, '10:30', '12:00'),
('Friday',    3, '13:00', '14:30'), ('Friday',    4, '15:00', '16:30');

-- Seed Departments
INSERT OR IGNORE INTO departments (name, code) VALUES
('Applied Sciences', 'ASC'),
('Health Records & IT', 'HRIT'),
('Clinical Medicine & Surgery', 'DCMS'),
('Health & Social Sciences', 'HSD'),
('Human Nutrition & Dietetics', 'HND'),
('Nursing', 'DNS'),
('Perioperative Theatre', 'PTT');

-- Seed Common Venues
INSERT OR IGNORE INTO lecture_halls (name, capacity) VALUES
('LH 4',30),('LH 5A',50),('LH 1 A',80),('LH 1 B',80),('LH 2',40),('LH 3',75),
('HSD 3',120),('HSD 2',150),('WORKSHOP',35),('LAB 1',35),('LAB 2',35),
('ASC 2',35),('ASC 3',35),('FOODLAB',30),('DT LAB',10),('DRS 2',40),
('COMP LAB 1',30),('COMP LAB 2',30),('THK 2 - 01',20),('THK 2 - 04',12),
('THK 2 - 05',14),('THK 2 - 07',35);