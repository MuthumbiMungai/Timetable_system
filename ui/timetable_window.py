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


class TimetableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🗓️ Weekly Timetable View")
        self.resize(1250, 780)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        # Header
        title = QLabel("🗓️ Weekly Timetable")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Filters
        filter_layout = QHBoxLayout()
        
        self.intake_combo = QComboBox()
        self.intake_combo.addItem("All Intakes", None)
        self.load_intakes()

        btn_refresh = QPushButton("Refresh Timetable")
        btn_refresh.clicked.connect(self.load_timetable)

        filter_layout.addWidget(QLabel("Filter by Intake:"))
        filter_layout.addWidget(self.intake_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(btn_refresh)

        main_layout.addLayout(filter_layout)

        # Timetable Grid
        self.grid = QTableWidget()
        self.grid.setColumnCount(5)  # Monday to Friday
        self.grid.setHorizontalHeaderLabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        
        # Rows = Timeslots (we have 4 sessions)
        self.grid.setRowCount(4)
        self.grid.setVerticalHeaderLabels([
            "Session 1\n08:00 - 10:00",
            "Session 2\n10:30 - 12:30",
            "Session 3\n14:00 - 16:00",
            "Session 4\n16:30 - 18:30"
        ])

        self.grid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.grid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # Style
        self.grid.setStyleSheet("""
            QTableWidget {
                font-size: 10pt;
                gridline-color: #ccc;
            }
            QTableWidget::item {
                padding: 8px;
                border: 1px solid #ddd;
            }
        """)

        main_layout.addWidget(self.grid)

        # Legend / Info
        legend = QLabel(
            "💡 Double-click any cell to assign a class (coming soon)\n"
            "Green = Scheduled | Empty = Available"
        )
        legend.setAlignment(Qt.AlignCenter)
        legend.setStyleSheet("color: #555; font-size: 10pt;")
        main_layout.addWidget(legend)

        self.load_timetable()

    def load_intakes(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id, c.name, i.label 
            FROM intakes i
            JOIN courses c ON i.course_id = c.id
            ORDER BY c.name, i.label
        """)
        for iid, course, label in cursor.fetchall():
            self.intake_combo.addItem(f"{course} - {label}", iid)
        conn.close()

    def load_timetable(self):
        """Load current timetable entries into the grid"""
        intake_id = self.intake_combo.currentData()

        # Clear grid
        for row in range(self.grid.rowCount()):
            for col in range(self.grid.columnCount()):
                item = QTableWidgetItem("")
                item.setBackground(QColor("#f8f9fa"))
                self.grid.setItem(row, col, item)

        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                t.day_of_week,
                t.session_number,
                u.name AS unit_name,
                tr.full_name AS trainer,
                h.name AS hall,
                i.label AS intake_label
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

        day_map = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2,
            "Thursday": 3, "Friday": 4
        }

        for entry in entries:
            day_of_week, session_num, unit, trainer, hall, intake = entry
            col = day_map.get(day_of_week)
            row = session_num - 1  # 1-based to 0-based

            if col is not None and 0 <= row < 4:
                text = f"{unit}\n{trainer}\n{hall}\n{intake}"
                item = QTableWidgetItem(text)
                item.setBackground(QColor("#d4edda"))   # Light green
                item.setTextAlignment(Qt.AlignCenter)
                self.grid.setItem(row, col, item)

        if not entries:
            QMessageBox.information(self, "Info", "No timetable entries found yet.\n\nYou can start assigning classes once we implement the assignment feature.")


# For now we only show the view. Assignment feature (drag & drop / form) will be added in the next iteration.