# ui/intakes_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QSpinBox,
    QFormLayout, QMessageBox, QGroupBox, QHeaderView, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sqlite3
from database.db import get_connection
from datetime import datetime


class IntakesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Intakes")
        self.resize(1100, 700)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        title = QLabel("👥 Intake Management")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Add New Intake
        add_group = QGroupBox("Add New Intake")
        form = QFormLayout()

        self.course_combo = QComboBox()
        self.intake_label = QLineEdit()
        self.intake_label.setPlaceholderText("e.g. Jan 2026 Intake")
        self.student_count = QSpinBox()
        self.student_count.setRange(0, 10000)
        self.student_count.setValue(50)
        self.academic_year = QLineEdit()
        self.academic_year.setText("2025/2026")

        btn_add = QPushButton("Add Intake")
        btn_add.clicked.connect(self.add_intake)

        form.addRow("Course:", self.course_combo)
        form.addRow("Intake Label:", self.intake_label)
        form.addRow("Student Count:", self.student_count)
        form.addRow("Academic Year:", self.academic_year)
        form.addRow("", btn_add)
        add_group.setLayout(form)
        main_layout.addWidget(add_group)

        # Action Buttons
        action_layout = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Refresh")
        btn_edit = QPushButton("✏️ Edit Selected")
        btn_delete = QPushButton("🗑️ Delete Selected")
        btn_summary = QPushButton("📊 View Summary / Log")

        btn_refresh.clicked.connect(self.load_intakes)
        btn_edit.clicked.connect(self.edit_intake)
        btn_delete.clicked.connect(self.delete_intake)
        btn_summary.clicked.connect(self.show_summary)

        action_layout.addWidget(btn_refresh)
        action_layout.addWidget(btn_edit)
        action_layout.addWidget(btn_delete)
        action_layout.addWidget(btn_summary)
        action_layout.addStretch()
        main_layout.addLayout(action_layout)

        # Intakes Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Course", "Label", "Students", "Academic Year"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.table)

        self.load_courses()
        self.load_intakes()

    def load_courses(self):
        self.course_combo.clear()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, d.name || ' - ' || c.name 
            FROM courses c 
            JOIN departments d ON c.department_id = d.id 
            ORDER BY d.name, c.name
        """)
        for cid, display in cursor.fetchall():
            self.course_combo.addItem(display, cid)
        conn.close()

    def load_intakes(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id, c.name, i.label, i.student_count, i.academic_year
            FROM intakes i
            JOIN courses c ON i.course_id = c.id
            ORDER BY c.name, i.label
        """)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, (iid, course, label, students, year) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(iid)))
            self.table.setItem(i, 1, QTableWidgetItem(course))
            self.table.setItem(i, 2, QTableWidgetItem(label))
            self.table.setItem(i, 3, QTableWidgetItem(str(students)))
            self.table.setItem(i, 4, QTableWidgetItem(year))

    def add_intake(self):
        course_id = self.course_combo.currentData()
        label = self.intake_label.text().strip()
        students = self.student_count.value()
        year = self.academic_year.text().strip()

        if not label or not year or course_id is None:
            QMessageBox.warning(self, "Error", "All fields are required!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO intakes (course_id, label, student_count, academic_year)
                VALUES (?, ?, ?, ?)
            """, (course_id, label, students, year))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Intake added successfully!")
            self.intake_label.clear()
            self.load_intakes()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Intake label already exists for this course!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def edit_intake(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select an intake to edit!")
            return

        intake_id = int(self.table.item(row, 0).text())
        curr_label = self.table.item(row, 2).text()
        curr_students = int(self.table.item(row, 3).text())
        curr_year = self.table.item(row, 4).text()

        new_label, ok = QInputDialog.getText(self, "Edit Intake", "Label:", text=curr_label)
        if not ok or not new_label.strip(): return
        new_students, ok = QInputDialog.getInt(self, "Edit Intake", "Students:", value=curr_students, min=0, max=10000)
        if not ok: return
        new_year, ok = QInputDialog.getText(self, "Edit Intake", "Academic Year:", text=curr_year)
        if not ok or not new_year.strip(): return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE intakes SET label=?, student_count=?, academic_year=? WHERE id=?", 
                           (new_label.strip(), new_students, new_year.strip(), intake_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Intake updated!")
            self.load_intakes()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_intake(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select an intake!")
            return

        intake_id = int(self.table.item(row, 0).text())
        label = self.table.item(row, 2).text()

        reply = QMessageBox.question(self, "Confirm Delete", 
                                     f"Delete intake '{label}' and related timetable entries?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes: return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM timetable_entries WHERE intake_id=?", (intake_id,))
            cursor.execute("DELETE FROM intakes WHERE id=?", (intake_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Intake deleted.")
            self.load_intakes()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_summary(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM intakes"); total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT course_id) FROM intakes"); courses = cursor.fetchone()[0]

        cursor.execute("""
            SELECT c.name, COUNT(i.id)
            FROM courses c
            LEFT JOIN intakes i ON i.course_id = c.id
            GROUP BY c.id ORDER BY c.name
        """)
        breakdown = cursor.fetchall()
        conn.close()

        text = f"<b>👥 INTAKES SUMMARY</b><br>Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}<br><br>"
        text += f"Total Intakes: {total}<br>Courses with Intakes: {courses}<br><br><b>Breakdown:</b><br>"
        for course, count in breakdown:
            text += f"• {course} → {count} intake(s)<br>"

        msg = QMessageBox(self)
        msg.setWindowTitle("Intakes Summary / Log")
        msg.setTextFormat(Qt.RichText)
        msg.setText(text)
        msg.exec_()