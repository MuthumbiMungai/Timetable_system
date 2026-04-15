# 📅 Timetable Management System

A desktop application built with **Python** and **PyQt5** for managing academic timetables, departments, trainers, units, and student intakes. Designed for educational institutions to streamline scheduling and resource allocation.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [Known Issues & Improvements](#known-issues--improvements)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **Timetable Management System** is a local desktop application that helps academic administrators manage:

- Departments and their courses
- Student intakes per course
- Trainers/lecturers and their assignments
- Teaching units/subjects
- Weekly timetable scheduling across sessions and days

All data is stored locally using **SQLite**, making the application lightweight and easy to deploy without a server.

---

## Features

### 🏢 Department Management
- Add departments with a name and unique code
- View all departments in a sortable table
- Drill down into a department to manage its courses
- Courses are linked to departments and display inside a detail dialog

### 📖 Course Management *(inside Department Details)*
- Add courses with a name and unique code, linked to a specific department
- View all courses under a department
- Double-click a course to manage its student intakes

### 👥 Intake Management *(inside Course Details)*
- Add intakes per course (e.g. "Jan 2026 Intake")
- Track student count and academic year per intake
- Intakes are used throughout the system for timetable and unit assignments

### 👨‍🏫 Trainer Management
- Add trainers with full name, department, and optional email
- View all trainers in a searchable table
- Edit trainer details via a double-click dialog
- Delete trainers with a confirmation prompt
- Trainers are linked to departments

### 📚 Unit / Subject Management
- Add units with a name, code, department, weekly hours, and a "shared" flag
- Mark units as shared across departments
- Assign units to one or more intakes via a multi-select dialog
- Delete units with confirmation
- Duplicate unit codes are prevented

### 🗓️ Timetable View
- Weekly grid view: **Monday–Friday** across **4 daily sessions**
  - Session 1: 08:00 – 10:00
  - Session 2: 10:30 – 12:30
  - Session 3: 14:00 – 16:00
  - Session 4: 16:30 – 18:30
- Filter timetable by intake
- Scheduled slots highlighted in green
- Empty slots shown in light grey
- Timetable entries display: Unit, Trainer, Hall, and Intake label

---

## Project Structure

```
timetable_system/
│
├── main.py                  # App entry point
│
├── database/
│   ├── db.py                # DB connection & initialization
│   └── schema.sql           # SQL schema (tables & seed data)
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py       # Dashboard / home screen
│   ├── departments_window.py # Department, Course & Intake management
│   ├── trainers_window.py   # Trainer management
│   ├── units_window.py      # Unit/Subject management
│   └── timetable_window.py  # Weekly timetable grid view
│
├── models/                  # (Reserved for data models)
├── services/                # (Reserved for business logic)
├── resources/               # (Reserved for icons/assets)
├── utils/                   # (Reserved for helper utilities)
│
├── .gitignore
└── README.md
```

---

## Requirements

- Python **3.8+**
- PyQt5

Install dependencies:

```bash
pip install PyQt5
```

---

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/MuthumbiMungai/Timetable_system.git
cd Timetable_system
```

2. **Install dependencies:**

```bash
pip install PyQt5
```

3. **Run the application:**

```bash
python main.py
```

The database (`timetable.db`) will be created automatically on first launch using `schema.sql`.

---

## Usage

When you launch the app, the main dashboard presents five navigation buttons:

| Button | Module | Status |
|--------|--------|--------|
| Manage Departments | Departments, Courses & Intakes | ✅ Ready |
| Manage Trainers | Trainer CRUD + Edit dialog | ✅ Ready |
| Manage Units | Units + Intake assignment | ✅ Ready |
| Manage Intakes | Standalone intake view | 🔧 Coming Soon |
| View / Generate Timetable | Weekly grid view | ✅ Ready (view only) |

### Adding a Department
1. Click **Manage Departments**
2. Enter the department name and code, then click **Add Department**
3. Double-click any department row to open its courses

### Adding a Course & Intake
1. Inside the Department detail dialog, enter a course name and code
2. Click **Add Course**
3. Double-click the course to open the Intakes dialog
4. Fill in the intake label, student count, and academic year

### Adding a Trainer
1. Click **Manage Trainers**
2. Fill in the trainer's name, select their department, and optionally add an email
3. Click **Add Trainer**
4. Double-click any row to edit; use **Delete Selected** to remove

### Adding a Unit
1. Click **Manage Units**
2. Fill in the unit name, code, department, weekly hours
3. Optionally check **Shared across departments**
4. Double-click any unit to assign it to student intakes

### Viewing the Timetable
1. Click **View / Generate Timetable**
2. Use the **Filter by Intake** dropdown to narrow results
3. Click **Refresh Timetable** to reload
4. Green cells = scheduled; empty cells = available

---

## Database Schema

The app uses **SQLite** with the following core tables:

| Table | Description |
|-------|-------------|
| `departments` | Stores department name and code |
| `courses` | Courses linked to departments |
| `intakes` | Student intakes per course with count and academic year |
| `trainers` | Trainers linked to departments |
| `units` | Teaching units/subjects linked to departments |
| `intake_units` | Many-to-many: units assigned to intakes |
| `lecture_halls` | Available rooms/halls |
| `timeslots` | Days and session numbers |
| `timetable_entries` | Scheduled classes linking unit, trainer, hall, intake, timeslot |

---

## Known Issues & Improvements

| Issue | Description | Priority |
|-------|-------------|----------|
| Emoji encoding | Emojis in window titles appear garbled on some systems | Low |
| DB path | `timetable.db` is created relative to run directory | Medium |
| Foreign keys | SQLite foreign key enforcement not enabled by default | Medium |
| No delete for departments | Departments cannot currently be deleted from the UI | Medium |
| Intakes button | "Manage Intakes" on dashboard shows a placeholder message | High |
| Timetable assignment | Classes cannot yet be assigned from the timetable UI | High |

---

## Roadmap

- [ ] Timetable assignment UI (drag-and-drop or form-based)
- [ ] Standalone Intakes management screen
- [ ] Delete department functionality
- [ ] Conflict detection (trainer double-booking, hall clashes)
- [ ] Export timetable to PDF or Excel
- [ ] Search and filter across all tables
- [ ] Dark mode support
- [ ] User authentication (admin login)

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "Add: your feature description"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a Pull Request

Please ensure your code follows the existing style and includes comments where necessary.

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

*Built with ❤️ using Python & PyQt5*