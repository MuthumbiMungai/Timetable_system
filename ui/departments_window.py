# ui/departments_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QMessageBox,
    QGroupBox, QHeaderView, QDialog, QSpinBox, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sqlite3
from database.db import get_connection
from datetime import datetime


class DepartmentsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Departments")
        self.resize(1200, 750)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        title = QLabel("🏢 Department Management")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Add New Department
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

        # Action Buttons
        action_layout = QHBoxLayout()
        btn_edit = QPushButton("✏️ Edit Selected")
        btn_delete = QPushButton("🗑️ Delete Selected")
        btn_summary = QPushButton("📊 View Summary / Log")

        btn_edit.clicked.connect(self.edit_department)
        btn_delete.clicked.connect(self.delete_department)
        btn_summary.clicked.connect(self.show_summary)

        action_layout.addWidget(btn_edit)
        action_layout.addWidget(btn_delete)
        action_layout.addWidget(btn_summary)
        main_layout.addLayout(action_layout)

        # Departments Table
        self.dept_table = QTableWidget()
        self.dept_table.setColumnCount(3)
        self.dept_table.setHorizontalHeaderLabels(["ID", "Department Name", "Code"])
        self.dept_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.dept_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dept_table.doubleClicked.connect(self.show_department_details)
        main_layout.addWidget(self.dept_table)

        btn_refresh = QPushButton("🔄 Refresh List")
        btn_refresh.clicked.connect(self.load_departments)
        main_layout.addWidget(btn_refresh)

        self.load_departments()

    def load_departments(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, code FROM departments ORDER BY name")
        rows = cursor.fetchall()
        conn.close()

        self.dept_table.setRowCount(len(rows))
        for i, (did, name, code) in enumerate(rows):
            self.dept_table.setItem(i, 0, QTableWidgetItem(str(did)))
            self.dept_table.setItem(i, 1, QTableWidgetItem(name))
            self.dept_table.setItem(i, 2, QTableWidgetItem(code))

    def add_department(self):
        name = self.dept_name.text().strip()
        code = self.dept_code.text().strip().upper()
        if not name or not code:
            QMessageBox.warning(self, "Error", "Name and Code are required!")
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO departments (name, code) VALUES (?, ?)", (name, code))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", f"Department '{name}' added!")
            self.dept_name.clear()
            self.dept_code.clear()
            self.load_departments()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", f"Code '{code}' already exists!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def edit_department(self):
        row = self.dept_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a department to edit!")
            return
        dept_id = int(self.dept_table.item(row, 0).text())
        curr_name = self.dept_table.item(row, 1).text()
        curr_code = self.dept_table.item(row, 2).text()

        new_name, ok = QInputDialog.getText(self, "Edit Department", "Name:", text=curr_name)
        if not ok or not new_name.strip(): return
        new_code, ok = QInputDialog.getText(self, "Edit Department", "Code:", text=curr_code)
        if not ok or not new_code.strip(): return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE departments SET name=?, code=? WHERE id=?", 
                           (new_name.strip(), new_code.strip().upper(), dept_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Department updated!")
            self.load_departments()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_department(self):
        row = self.dept_table.currentRow()
        if row < 0: 
            QMessageBox.warning(self, "Error", "Select a department!")
            return
        dept_id = int(self.dept_table.item(row, 0).text())
        name = self.dept_table.item(row, 1).text()

        reply = QMessageBox.question(self, "Confirm Delete", 
                                     f"Delete '{name}' and ALL related courses & intakes?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes: return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM intakes WHERE course_id IN (SELECT id FROM courses WHERE department_id=?)", (dept_id,))
            cursor.execute("DELETE FROM courses WHERE department_id=?", (dept_id,))
            cursor.execute("DELETE FROM departments WHERE id=?", (dept_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Department and related data deleted.")
            self.load_departments()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_summary(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM departments"); depts = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM courses"); courses = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM intakes"); intakes = cursor.fetchone()[0]

        cursor.execute("""
            SELECT d.name, d.code, COUNT(c.id) 
            FROM departments d LEFT JOIN courses c ON c.department_id = d.id 
            GROUP BY d.id ORDER BY d.name
        """)
        data = cursor.fetchall()
        conn.close()

        text = f"<b>📊 TIMETABLE SYSTEM SUMMARY</b><br>Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}<br><br>"
        text += f"Total Departments: {depts}<br>Total Courses: {courses}<br>Total Intakes: {intakes}<br><br><b>Breakdown:</b><br>"
        for name, code, cnt in data:
            text += f"• {name} ({code}) → {cnt} course(s)<br>"

        msg = QMessageBox(self)
        msg.setWindowTitle("System Summary / Log")
        msg.setTextFormat(Qt.RichText)
        msg.setText(text)
        msg.exec_()

    def show_department_details(self, index):
        """Safely handle double-click on department row"""
        if not index.isValid():
            return

        row = index.row()
        
        id_item = self.dept_table.item(row, 0)
        name_item = self.dept_table.item(row, 1)

        if not id_item or not name_item:
            QMessageBox.warning(self, "Error", "Could not read department data.")
            return

        try:
            dept_id = int(id_item.text())
            dept_name = name_item.text()
        except (ValueError, AttributeError):
            QMessageBox.warning(self, "Error", "Invalid department data.")
            return

        dialog = DepartmentDetailDialog(dept_id, dept_name, self)
        dialog.exec_()


# ====================== Department Detail Dialog ======================
class DepartmentDetailDialog(QDialog):
    def __init__(self, dept_id: int, dept_name: str, parent=None):
        super().__init__(parent)
        self.dept_id = dept_id
        self.setWindowTitle(f"Department: {dept_name}")
        self.resize(950, 650)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel(f"<b>Department:</b> {dept_name}"))

        # Add Course Section
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

        self.course_table = QTableWidget()
        self.course_table.setColumnCount(3)
        self.course_table.setHorizontalHeaderLabels(["ID", "Course Name", "Code"])
        self.course_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.course_table.doubleClicked.connect(self.show_course_intakes)
        layout.addWidget(self.course_table)

        self.load_courses()

    def load_courses(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, code FROM courses WHERE department_id = ? ORDER BY name", (self.dept_id,))
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
            QMessageBox.warning(self, "Error", "Name and Code required!")
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO courses (department_id, name, code) VALUES (?, ?, ?)", 
                           (self.dept_id, name, code))
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
        course_id = int(self.course_table.item(row, 0).text())
        course_name = self.course_table.item(row, 1).text()
        dialog = IntakeDialog(course_id, course_name, self)
        dialog.exec_()


# ====================== Intake Dialog (with Edit & Delete) ======================
class IntakeDialog(QDialog):
    def __init__(self, course_id: int, course_name: str, parent=None):
        super().__init__(parent)
        self.course_id = course_id
        self.setWindowTitle(f"Intakes - {course_name}")
        self.resize(850, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel(f"<b>Course:</b> {course_name}"))

        # Action buttons
        act = QHBoxLayout()
        btn_edit = QPushButton("✏️ Edit Selected")
        btn_delete = QPushButton("🗑️ Delete Selected")
        btn_edit.clicked.connect(self.edit_intake)
        btn_delete.clicked.connect(self.delete_intake)
        act.addWidget(btn_edit)
        act.addWidget(btn_delete)
        layout.addLayout(act)

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

        form.addRow("Label:", self.intake_label)
        form.addRow("Students:", self.student_count)
        form.addRow("Academic Year:", self.academic_year)
        form.addRow("", btn_add)
        form_group.setLayout(form)
        layout.addWidget(form_group)

        self.intake_table = QTableWidget()
        self.intake_table.setColumnCount(4)
        self.intake_table.setHorizontalHeaderLabels(["ID", "Label", "Students", "Academic Year"])
        self.intake_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.intake_table)

        self.load_intakes()

    def load_intakes(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, label, student_count, academic_year FROM intakes WHERE course_id = ? ORDER BY label", (self.course_id,))
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
            QMessageBox.warning(self, "Error", "Label and Year required!")
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO intakes (course_id, label, student_count, academic_year) VALUES (?, ?, ?, ?)",
                           (self.course_id, label, students, year))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Intake added!")
            self.intake_label.clear()
            self.load_intakes()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def edit_intake(self):
        row = self.intake_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select an intake!")
            return
        iid = int(self.intake_table.item(row, 0).text())
        curr_label = self.intake_table.item(row, 1).text()
        curr_students = int(self.intake_table.item(row, 2).text())
        curr_year = self.intake_table.item(row, 3).text()

        new_label, ok = QInputDialog.getText(self, "Edit Intake", "Label:", text=curr_label)
        if not ok or not new_label.strip(): return
        new_students, ok = QInputDialog.getInt(self, "Edit Intake", "Students:", value=curr_students, min=0, max=10000)
        if not ok: return
        new_year, ok = QInputDialog.getText(self, "Edit Intake", "Year:", text=curr_year)
        if not ok or not new_year.strip(): return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE intakes SET label=?, student_count=?, academic_year=? WHERE id=?", 
                           (new_label.strip(), new_students, new_year.strip(), iid))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Intake updated!")
            self.load_intakes()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_intake(self):
        row = self.intake_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select an intake!")
            return
        iid = int(self.intake_table.item(row, 0).text())
        label = self.intake_table.item(row, 1).text()

        reply = QMessageBox.question(self, "Confirm", f"Delete intake '{label}'?", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes: return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM timetable_entries WHERE intake_id=?", (iid,))
            cursor.execute("DELETE FROM intakes WHERE id=?", (iid,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Intake deleted.")
            self.load_intakes()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))