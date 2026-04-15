# ui/departments_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QMessageBox,
    QGroupBox, QHeaderView, QDialog, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sqlite3
from database.db import get_connection


class DepartmentsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Departments")
        self.resize(1200, 750)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        # Header
        title = QLabel("🏢 Department Management")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # === Add New Department ===
        add_group = QGroupBox("Add New Department")
        add_layout = QHBoxLayout()

        self.dept_name = QLineEdit()
        self.dept_name.setPlaceholderText("Department Name (e.g. Computer Science)")
        self.dept_code = QLineEdit()
        self.dept_code.setPlaceholderText("Code (e.g. CS)")

        btn_add = QPushButton("Add Department")
        btn_add.clicked.connect(self.add_department)

        add_layout.addWidget(QLabel("Name:"))
        add_layout.addWidget(self.dept_name)
        add_layout.addWidget(QLabel("Code:"))
        add_layout.addWidget(self.dept_code)
        add_layout.addWidget(btn_add)

        add_group.setLayout(add_layout)
        main_layout.addWidget(add_group)

        # === Departments Table ===
        self.dept_table = QTableWidget()
        self.dept_table.setColumnCount(3)
        self.dept_table.setHorizontalHeaderLabels(["ID", "Department Name", "Code"])
        self.dept_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.dept_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dept_table.doubleClicked.connect(self.show_department_details)
        main_layout.addWidget(self.dept_table)

        # Refresh button
        btn_refresh = QPushButton("Refresh List")
        btn_refresh.clicked.connect(self.load_departments)
        main_layout.addWidget(btn_refresh)

        self.load_departments()

    def load_departments(self):
        """Load all departments into the table"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, code FROM departments ORDER BY name")
        rows = cursor.fetchall()
        conn.close()

        self.dept_table.setRowCount(len(rows))
        for row_idx, (dept_id, name, code) in enumerate(rows):
            self.dept_table.setItem(row_idx, 0, QTableWidgetItem(str(dept_id)))
            self.dept_table.setItem(row_idx, 1, QTableWidgetItem(name))
            self.dept_table.setItem(row_idx, 2, QTableWidgetItem(code))

    def add_department(self):
        name = self.dept_name.text().strip()
        code = self.dept_code.text().strip().upper()

        if not name or not code:
            QMessageBox.warning(self, "Input Error", "Both Name and Code are required!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO departments (name, code) VALUES (?, ?)", (name, code))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", f"Department '{name}' added successfully!")
            self.dept_name.clear()
            self.dept_code.clear()
            self.load_departments()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Duplicate Error", f"Department code '{code}' already exists!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add department: {e}")

    def show_department_details(self, index):
        """When user double-clicks a department row, show courses and intakes"""
        row = index.row()
        dept_id_item = self.dept_table.item(row, 0)
        if not dept_id_item:
            return
        dept_id = int(dept_id_item.text())
        dept_name = self.dept_table.item(row, 1).text()

        dialog = DepartmentDetailDialog(dept_id, dept_name, self)
        dialog.exec_()


# ====================== Detail Dialog ======================
class DepartmentDetailDialog(QDialog):
    def __init__(self, dept_id: int, dept_name: str, parent=None):
        super().__init__(parent)
        self.dept_id = dept_id
        self.setWindowTitle(f"Department: {dept_name}")
        self.resize(900, 650)

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel(f"<b>Department:</b> {dept_name}"))

        # === Add Course ===
        course_group = QGroupBox("Add New Course")
        form = QFormLayout()
        self.course_name = QLineEdit()
        self.course_code = QLineEdit()
        btn_add_course = QPushButton("Add Course")
        btn_add_course.clicked.connect(self.add_course)

        form.addRow("Course Name:", self.course_name)
        form.addRow("Course Code:", self.course_code)
        form.addRow("", btn_add_course)
        course_group.setLayout(form)
        layout.addWidget(course_group)

        # === Courses Table ===
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(3)
        self.course_table.setHorizontalHeaderLabels(["ID", "Course Name", "Code"])
        self.course_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.course_table.doubleClicked.connect(self.show_course_intakes)
        layout.addWidget(self.course_table)

        # Load courses for this department
        self.load_courses()

    def load_courses(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, code 
            FROM courses 
            WHERE department_id = ? 
            ORDER BY name
        """, (self.dept_id,))
        rows = cursor.fetchall()
        conn.close()

        self.course_table.setRowCount(len(rows))
        for i, (cid, name, code) in enumerate(rows):
            self.course_table.setItem(i, 0, QTableWidgetItem(str(cid)))
            self.course_table.setItem(i, 1, QTableWidgetItem(name))
            self.course_table.setItem(i, 2, QTableWidgetItem(code))

    def add_course(self):
        name = self.course_name.text().strip()
        code = self.course_code.text().strip().upper()

        if not name or not code:
            QMessageBox.warning(self, "Error", "Course name and code required!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO courses (department_id, name, code) 
                VALUES (?, ?, ?)
            """, (self.dept_id, name, code))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Course added!")
            self.course_name.clear()
            self.course_code.clear()
            self.load_courses()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Course code already exists!")

    def show_course_intakes(self, index):
        row = index.row()
        course_id_item = self.course_table.item(row, 0)
        if not course_id_item:
            return
        course_id = int(course_id_item.text())
        course_name = self.course_table.item(row, 1).text()

        dialog = IntakeDialog(course_id, course_name, self)
        dialog.exec_()


# ====================== Intake Dialog ======================
class IntakeDialog(QDialog):
    def __init__(self, course_id: int, course_name: str, parent=None):
        super().__init__(parent)
        self.course_id = course_id
        self.setWindowTitle(f"Intakes - {course_name}")
        self.resize(700, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel(f"<b>Course:</b> {course_name}"))

        # Add Intake Form
        form_group = QGroupBox("Add New Intake")
        form = QFormLayout()

        self.intake_label = QLineEdit()
        self.intake_label.setPlaceholderText("e.g. Jan 2026 Intake")
        self.student_count = QSpinBox()
        self.student_count.setRange(0, 10000)
        self.student_count.setValue(50)
        self.academic_year = QLineEdit()
        self.academic_year.setText("2025/2026")

        btn_add = QPushButton("Add Intake")
        btn_add.clicked.connect(self.add_intake)

        form.addRow("Intake Label:", self.intake_label)
        form.addRow("Student Count:", self.student_count)
        form.addRow("Academic Year:", self.academic_year)
        form.addRow("", btn_add)
        form_group.setLayout(form)
        layout.addWidget(form_group)

        # Intakes Table
        self.intake_table = QTableWidget()
        self.intake_table.setColumnCount(4)
        self.intake_table.setHorizontalHeaderLabels(["ID", "Label", "Students", "Academic Year"])
        self.intake_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.intake_table)

        self.load_intakes()

    def load_intakes(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, label, student_count, academic_year 
            FROM intakes 
            WHERE course_id = ? 
            ORDER BY label
        """, (self.course_id,))
        rows = cursor.fetchall()
        conn.close()

        self.intake_table.setRowCount(len(rows))
        for i, (iid, label, students, year) in enumerate(rows):
            self.intake_table.setItem(i, 0, QTableWidgetItem(str(iid)))
            self.intake_table.setItem(i, 1, QTableWidgetItem(label))
            self.intake_table.setItem(i, 2, QTableWidgetItem(str(students)))
            self.intake_table.setItem(i, 3, QTableWidgetItem(year))

    def add_intake(self):
        label = self.intake_label.text().strip()
        students = self.student_count.value()
        year = self.academic_year.text().strip()

        if not label or not year:
            QMessageBox.warning(self, "Error", "Label and Academic Year are required!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO intakes (course_id, label, student_count, academic_year)
                VALUES (?, ?, ?, ?)
            """, (self.course_id, label, students, year))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Intake added successfully!")
            self.intake_label.clear()
            self.load_intakes()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))