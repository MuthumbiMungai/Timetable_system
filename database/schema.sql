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
    label           TEXT NOT NULL,
    student_count   INTEGER NOT NULL DEFAULT 0 CHECK (student_count >= 0),
    academic_year   TEXT NOT NULL,
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

CREATE TABLE IF NOT EXISTS unit_shared_departments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id         INTEGER NOT NULL REFERENCES units(id) ON DELETE CASCADE,
    department_id   INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    UNIQUE(unit_id, department_id)
);

CREATE TABLE IF NOT EXISTS unit_trainers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id         INTEGER NOT NULL REFERENCES units(id) ON DELETE CASCADE,
    trainer_id      INTEGER NOT NULL REFERENCES trainers(id) ON DELETE CASCADE,
    UNIQUE(unit_id, trainer_id)
);

-- =============================================
-- Many-to-Many: Intakes <-> Units
-- =============================================
CREATE TABLE IF NOT EXISTS intake_units (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    intake_id       INTEGER NOT NULL REFERENCES intakes(id) ON DELETE CASCADE,
    unit_id         INTEGER NOT NULL REFERENCES units(id) ON DELETE CASCADE,
    UNIQUE(intake_id, unit_id)
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

    UNIQUE(trainer_id, timeslot_id),
    UNIQUE(hall_id,    timeslot_id),
    UNIQUE(intake_id,  timeslot_id)
);

-- =============================================
-- Seed Data: Timeslots (Mon–Fri, 4 sessions)
-- =============================================

INSERT OR IGNORE INTO timeslots (day_of_week, session_number, start_time, end_time) VALUES
    ('Monday',    1, '08:00', '10:00'),
    ('Monday',    2, '10:30', '12:30'),
    ('Monday',    3, '14:00', '16:00'),
    ('Monday',    4, '16:30', '18:30'),
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
-- Seed Data: Departments
-- =============================================

INSERT OR IGNORE INTO departments (name, code) VALUES
    ('Applied Sciences',                    'APPLIED'),
    ('Clinical Medicine & Surgery',         'CMS'),
    ('Human Nutrition & Dietetics',         'HND'),
    ('Health Records & IT',                 'HRIT'),
    ('Health & Social Sciences',            'HSS'),
    ('Nursing',                             'NURS'),
    ('Perioperative Theatre',               'PT');

-- =============================================
-- Seed Data: Trainers
-- =============================================

INSERT OR IGNORE INTO trainers (department_id, full_name) VALUES
    -- APPLIED SCIENCES (full-time)
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Andrew Mungai'),
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Bii Patrick Kipngeno'),
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Dick Komala'),
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Dorothy Adhiambo'),
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Esther Wanjiku'),
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Felix Langat'),
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Hannah Kahoro'),
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Jane Osoo'),
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Faith Laurine Wesonga'),
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Marvin Mutugi'),
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Mutuma Mbaya'),
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Samwel Ingosi'),
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Stephen Odiwuor'),
    -- CLINICAL MEDICINE & SURGERY (full-time)
    ((SELECT id FROM departments WHERE code='CMS'),     'Eric Mutugi'),
    -- HUMAN NUTRITION & DIETETICS (full-time)
    ((SELECT id FROM departments WHERE code='HND'),     'Fiona Kwamboka'),
    ((SELECT id FROM departments WHERE code='HND'),     'Martin Wanjohi'),
    ((SELECT id FROM departments WHERE code='HND'),     'Mary Kaganjo'),
    ((SELECT id FROM departments WHERE code='HND'),     'Maureen Ayuma'),
    ((SELECT id FROM departments WHERE code='HND'),     'Milkah Wambui'),
    ((SELECT id FROM departments WHERE code='HND'),     'Wilfred Osozi'),
    -- HEALTH RECORDS & IT (full-time)
    ((SELECT id FROM departments WHERE code='HRIT'),    'Antony Maina'),
    ((SELECT id FROM departments WHERE code='HRIT'),    'Beatrice Chepngeno'),
    ((SELECT id FROM departments WHERE code='HRIT'),    'BrianWakhale'),
    ((SELECT id FROM departments WHERE code='HRIT'),    'Derick Kibaso'),
    ((SELECT id FROM departments WHERE code='HRIT'),    'Evon Akinyi'),
    ((SELECT id FROM departments WHERE code='HRIT'),    'Geoffrey Karanja'),
    ((SELECT id FROM departments WHERE code='HRIT'),    'George Kahuria'),
    ((SELECT id FROM departments WHERE code='HRIT'),    'Jackline Kerubo'),
    ((SELECT id FROM departments WHERE code='HRIT'),    'Judith Kariuki'),
    ((SELECT id FROM departments WHERE code='HRIT'),    'Kennedy Kiplangat'),
    ((SELECT id FROM departments WHERE code='HRIT'),    'Moses Yego'),
    ((SELECT id FROM departments WHERE code='HRIT'),    'Phena Nasimiyu'),
    ((SELECT id FROM departments WHERE code='HRIT'),    'Victor Kariuki'),
    -- HEALTH & SOCIAL SCIENCES (full-time)
    ((SELECT id FROM departments WHERE code='HSS'),     'Benjamin Saitabau'),
    ((SELECT id FROM departments WHERE code='HSS'),     'Danson Nyamu'),
    ((SELECT id FROM departments WHERE code='HSS'),     'Elijah Mugambi'),
    ((SELECT id FROM departments WHERE code='HSS'),     'Ezra Odhiambo'),
    ((SELECT id FROM departments WHERE code='HSS'),     'Humphrey Mubweka'),
    ((SELECT id FROM departments WHERE code='HSS'),     'Jacinta Kibetu'),
    ((SELECT id FROM departments WHERE code='HSS'),     'Job Kwemoi'),
    ((SELECT id FROM departments WHERE code='HSS'),     'Luke Muthambi'),
    ((SELECT id FROM departments WHERE code='HSS'),     'Patrick Ngali'),
    ((SELECT id FROM departments WHERE code='HSS'),     'Peter Kimani'),
    ((SELECT id FROM departments WHERE code='HSS'),     'Peter Maina'),
    ((SELECT id FROM departments WHERE code='HSS'),     'Silphana Mutunga'),
    -- NURSING (full-time)
    ((SELECT id FROM departments WHERE code='NURS'),    'Agnes Mwololo'),
    ((SELECT id FROM departments WHERE code='NURS'),    'Beatrice Muthoni'),
    ((SELECT id FROM departments WHERE code='NURS'),    'Fredrick Ciira'),
    ((SELECT id FROM departments WHERE code='NURS'),    'Godfrey Muriuki'),
    ((SELECT id FROM departments WHERE code='NURS'),    'Jackson Ombaso'),
    ((SELECT id FROM departments WHERE code='NURS'),    'Joan Rotich'),
    ((SELECT id FROM departments WHERE code='NURS'),    'Mercy Kalungu'),
    ((SELECT id FROM departments WHERE code='NURS'),    'Nahashon Rotich'),
    ((SELECT id FROM departments WHERE code='NURS'),    'Paul Kibet'),
    ((SELECT id FROM departments WHERE code='NURS'),    'Robin Ibuloi'),
    ((SELECT id FROM departments WHERE code='NURS'),    'Ruth Moraa'),
    ((SELECT id FROM departments WHERE code='NURS'),    'Wilson Mosingi'),
    -- PERIOPERATIVE THEATRE (full-time)
    ((SELECT id FROM departments WHERE code='PT'),      'Bonface Mwendwa'),
    ((SELECT id FROM departments WHERE code='PT'),      'Brian Ondieki'),
    ((SELECT id FROM departments WHERE code='PT'),      'Dennis Kamau'),
    ((SELECT id FROM departments WHERE code='PT'),      'Frankline Kegocha'),
    ((SELECT id FROM departments WHERE code='PT'),      'Harrison Makuba'),
    ((SELECT id FROM departments WHERE code='PT'),      'Robinson Mwenda'),
    ((SELECT id FROM departments WHERE code='PT'),      'Sarah Jebet'),
    -- APPLIED SCIENCES (part-time)
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Kelvin Koech'),
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Kiplangat Evans'),
    ((SELECT id FROM departments WHERE code='APPLIED'), 'Gerald Njau'),
    -- CLINICAL MEDICINE & SURGERY (part-time)
    ((SELECT id FROM departments WHERE code='CMS'),     'Dorris Wairati'),
    ((SELECT id FROM departments WHERE code='CMS'),     'Timothy Otiso'),
    ((SELECT id FROM departments WHERE code='CMS'),     'Ann Nyanjau'),
    ((SELECT id FROM departments WHERE code='CMS'),     'Sammy Njeru'),
    ((SELECT id FROM departments WHERE code='CMS'),     'Hellen Wairimu'),
    -- PERIOPERATIVE THEATRE (part-time)
    ((SELECT id FROM departments WHERE code='PT'),      'Sylvia Onduso'),
    ((SELECT id FROM departments WHERE code='PT'),      'Florence Miriti'),
    -- HEALTH RECORDS & IT (part-time)
    ((SELECT id FROM departments WHERE code='HRIT'),    'Stephen Mwangi'),
    -- HUMAN NUTRITION & DIETETICS (part-time)
    ((SELECT id FROM departments WHERE code='HND'),     'Elias Kirimi');

-- =============================================
-- Seed Data: All Venues
-- =============================================

INSERT OR IGNORE INTO lecture_halls (name, capacity) VALUES
    -- BLOCK A
    ('DRS 2',      40),
    ('WORKSHOP',   35),
    ('COMPLAB 1',  30),
    ('COMPLAB 2',  30),
    ('SKILLSLAB',  35),
    ('FOODLAB',    30),
    ('DT LAB',     10),
    ('LAB 1',      35),
    ('LAB 2',      35),
    -- BLOCK B
    ('COMPLAB 3',  50),
    ('HND 3',      40),
    ('MLS 1',      40),
    ('MLS 2',      40),
    ('NS 1',       40),
    ('NS 2',       40),
    ('NS 3',       40),
    ('PT 1',       40),
    ('HSD 1',     100),
    -- BLOCK C
    ('ASC 1',      35),
    ('ASC 2',      35),
    ('ASC 3',      35),
    ('PT 2',       40),
    ('HSD 3',     120),
    ('DCM 1',      40),
    ('DCM 2',      40),
    ('HR 1',       30),
    ('HR 2',       30),
    ('HSD 2',     150),
    -- HOSTEL BLOCK
    ('LH',        150),
    ('LH 1 A',     80),
    ('LH 1 B',     80),
    ('LH 2',       40),
    ('LH 3',       75),
    ('LH 4',       30),
    ('LH 5',      100),
    ('LH 5 A',     50),
    ('LH 5B',      50),
    ('PHYSIOGYM',  40),
    -- THIKA 2 CAMPUS
    ('THK 2 - 01',  20),
    ('THK 2 - 02',  60),
    ('THK 2 - 03',  20),
    ('THK 2 - 04',  12),
    ('THK 2 - 05',  14),
    ('THK 2 - 06',  40),
    ('THK 2 - 07',  35),
    ('THK 2 - 08',  60),
    ('THK 2 - 09',  60),
    ('THK 2 - 10', 100);