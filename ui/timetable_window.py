# ui/timetable_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QHeaderView,
    QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
import sqlite3
from database.db import get_connection
import random


class TimetableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🗓️ Weekly Timetable View / Generate")
        self.resize(1250, 780)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        title = QLabel("🗓️ Weekly Timetable")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Filters + Generate
        filter_layout = QHBoxLayout()
        
        self.intake_combo = QComboBox()
        self.intake_combo.addItem("All Intakes", None)
        self.load_intakes()

        btn_refresh = QPushButton("Refresh Timetable")
        btn_generate = QPushButton("🚀 Generate Timetable (Greedy)")
        btn_clear = QPushButton("Clear Current Timetable")

        btn_refresh.clicked.connect(self.load_timetable)
        btn_generate.clicked.connect(self.generate_timetable)
        btn_clear.clicked.connect(self.clear_timetable)

        filter_layout.addWidget(QLabel("Filter by Intake:"))
        filter_layout.addWidget(self.intake_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(btn_refresh)
        filter_layout.addWidget(btn_generate)
        filter_layout.addWidget(btn_clear)

        main_layout.addLayout(filter_layout)

        # Timetable Grid
        self.grid = QTableWidget()
        self.grid.setColumnCount(5)
        self.grid.setHorizontalHeaderLabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        self.grid.setRowCount(4)
        self.grid.setVerticalHeaderLabels([
            "Session 1\n08:00 - 10:00",
            "Session 2\n10:30 - 12:30",
            "Session 3\n14:00 - 16:00",
            "Session 4\n16:30 - 18:30"
        ])

        self.grid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.grid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        self.grid.setStyleSheet("""
            QTableWidget { font-size: 10pt; gridline-color: #ccc; }
            QTableWidget::item { padding: 8px; border: 1px solid #ddd; }
        """)

        main_layout.addWidget(self.grid)

        legend = QLabel("💡 Green = Scheduled | Empty = Available\nDouble-click cell for manual assignment (coming soon)")
        legend.setAlignment(Qt.AlignCenter)
        legend.setStyleSheet("color: #555; font-size: 10pt;")
        main_layout.addWidget(legend)

        self.load_timetable()

    def load_intakes(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id, c.name, i.label 
            FROM intakes i JOIN courses c ON i.course_id = c.id 
            ORDER BY c.name, i.label
        """)
        for iid, course, label in cursor.fetchall():
            self.intake_combo.addItem(f"{course} - {label}", iid)
        conn.close()

    def load_timetable(self):
        intake_id = self.intake_combo.currentData()
        # Clear grid
        for r in range(self.grid.rowCount()):
            for c in range(self.grid.columnCount()):
                item = QTableWidgetItem("")
                item.setBackground(QColor("#f8f9fa"))
                self.grid.setItem(r, c, item)

        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT t.day_of_week, t.session_number, u.name, tr.full_name, h.name, i.label
            FROM timetable_entries te
            JOIN timeslots t ON te.timeslot_id = t.id
            JOIN units u ON te.unit_id = u.id
            JOIN trainers tr ON te.trainer_id = tr.id
            JOIN lecture_halls h ON te.hall_id = h.id
            JOIN intakes i ON te.intake_id = i.id
        """
        params = []
        if intake_id:
            query += " WHERE te.intake_id = ?"
            params.append(intake_id)
        query += " ORDER BY t.day_of_week, t.session_number"

        cursor.execute(query, params)
        entries = cursor.fetchall()
        conn.close()

        day_map = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "Friday":4}

        for entry in entries:
            day, session, unit, trainer, hall, intake = entry
            col = day_map.get(day)
            row = session - 1
            if col is not None and 0 <= row < 4:
                text = f"{unit}\n{trainer}\n{hall}\n{intake}"
                item = QTableWidgetItem(text)
                item.setBackground(QColor("#d4edda"))
                item.setTextAlignment(Qt.AlignCenter)
                self.grid.setItem(row, col, item)

    def clear_timetable(self):
        reply = QMessageBox.question(self, "Clear Timetable", "Delete ALL timetable entries?", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes: return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM timetable_entries")
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Success", "Timetable cleared.")
        self.load_timetable()

    def generate_timetable(self):
        intake_id = self.intake_combo.currentData()
        if not intake_id:
            QMessageBox.warning(self, "Warning", "Please select a specific intake to generate timetable for.")
            return

        reply = QMessageBox.question(self, "Generate", 
                                     "Generate timetable for this intake?\n(This will clear existing entries for this intake)", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes: return

        # Clear previous entries for this intake
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM timetable_entries WHERE intake_id=?", (intake_id,))
        conn.commit()

        # Simple Greedy Scheduler (basic version - can be improved)
        # Get available units for this intake
        cursor.execute("""
            SELECT u.id, u.name, u.hours_per_week 
            FROM intake_units iu 
            JOIN units u ON iu.unit_id = u.id 
            WHERE iu.intake_id = ?
        """, (intake_id,))
        units = cursor.fetchall()

        # Get available trainers and halls (simple random selection for demo)
        cursor.execute("SELECT id FROM trainers")
        trainers = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id FROM lecture_halls")
        halls = [row[0] for row in cursor.fetchall()]

        day_map = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
        timeslot_ids = list(range(1, 21))  # 5 days * 4 sessions

        assigned = 0
        for unit_id, unit_name, hours in units:
            for _ in range(hours):  # assign roughly hours_per_week sessions
                if not trainers or not halls:
                    break
                trainer_id = random.choice(trainers)
                hall_id = random.choice(halls)
                timeslot_id = random.choice(timeslot_ids)

                try:
                    cursor.execute("""
                        INSERT INTO timetable_entries 
                        (unit_id, trainer_id, hall_id, intake_id, timeslot_id)
                        VALUES (?, ?, ?, ?, ?)
                    """, (unit_id, trainer_id, hall_id, intake_id, timeslot_id))
                    conn.commit()
                    assigned += 1
                except sqlite3.IntegrityError:
                    pass  # conflict - skip

        conn.close()
        QMessageBox.information(self, "Generation Complete", 
                                f"Generated {assigned} timetable entries for the selected intake.\n\n"
                                "Note: This is a basic greedy version. Conflicts are skipped.")
        self.load_timetable()