# ui/units_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QSpinBox,
    QCheckBox, QFormLayout, QMessageBox, QGroupBox, QHeaderView, QDialog,
    QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sqlite3
from database.db import get_connection


class UnitsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Units / Subjects")
        self.resize(1250, 780)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        title = QLabel("📚 Unit / Subject Management")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Add New Unit
        add_group = QGroupBox("Add New Unit")
        form = QFormLayout()

        self.unit_name = QLineEdit()
        self.unit_code = QLineEdit()
        self.dept_combo = QComboBox()
        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(1, 6)
        self.hours_spin.setValue(2)
        self.shared_check = QCheckBox("Shared across departments")

        btn_add = QPushButton("Add Unit")
        btn_add.clicked.connect(self.add_unit)

        form.addRow("Unit Name:", self.unit_name)
        form.addRow("Unit Code:", self.unit_code)
        form.addRow("Department:", self.dept_combo)
        form.addRow("Hours per Week:", self.hours_spin)
        form.addRow("", self.shared_check)
        form.addRow("", btn_add)

        add_group.setLayout(form)
        main_layout.addWidget(add_group)

        # Units Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Code", "Department", "Hours"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.doubleClicked.connect(self.show_unit_details)

        main_layout.addWidget(self.table)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_units)
        btn_delete = QPushButton("Delete Selected Unit")
        btn_delete.clicked.connect(self.delete_unit)

        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_delete)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.load_departments()
        self.load_units()

    def load_departments(self):
        self.dept_combo.clear()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM departments ORDER BY name")
        for did, name in cursor.fetchall():
            self.dept_combo.addItem(name, did)
        conn.close()

    def load_units(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.name, u.code, d.name, u.hours_per_week
            FROM units u
            JOIN departments d ON u.department_id = d.id
            ORDER BY u.name
        """)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, (uid, name, code, dept, hours) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(uid)))
            self.table.setItem(i, 1, QTableWidgetItem(name))
            self.table.setItem(i, 2, QTableWidgetItem(code))
            self.table.setItem(i, 3, QTableWidgetItem(dept))
            self.table.setItem(i, 4, QTableWidgetItem(str(hours)))

    def add_unit(self):
        name = self.unit_name.text().strip()
        code = self.unit_code.text().strip().upper()
        dept_id = self.dept_combo.currentData()
        hours = self.hours_spin.value()
        is_shared = 1 if self.shared_check.isChecked() else 0

        if not name or not code or dept_id is None:
            QMessageBox.warning(self, "Error", "Please fill all required fields!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO units (department_id, name, code, hours_per_week, is_shared)
                VALUES (?, ?, ?, ?, ?)
            """, (dept_id, name, code, hours, is_shared))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", f"Unit '{code}' added successfully!")
            self.clear_form()
            self.load_units()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Duplicate", f"Unit code '{code}' already exists.")

    def clear_form(self):
        self.unit_name.clear()
        self.unit_code.clear()
        self.hours_spin.setValue(2)
        self.shared_check.setChecked(False)

    def show_unit_details(self, index):
        row = index.row()
        unit_id = int(self.table.item(row, 0).text())
        unit_name = self.table.item(row, 1).text()

        dialog = UnitDetailDialog(unit_id, unit_name, self)
        dialog.exec_()

    def delete_unit(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Please select a unit first.")
            return

        unit_id = int(self.table.item(row, 0).text())
        code = self.table.item(row, 2).text()

        reply = QMessageBox.question(self, "Delete Unit",
            f"Delete unit '{code}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM units WHERE id = ?", (unit_id,))
                conn.commit()
                conn.close()
                self.load_units()
                QMessageBox.information(self, "Deleted", "Unit deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


# ====================== Detail Dialog with Intake Assignment ======================
class UnitDetailDialog(QDialog):
    def __init__(self, unit_id: int, unit_name: str, parent=None):
        super().__init__(parent)
        self.unit_id = unit_id
        self.setWindowTitle(f"Manage Intakes for: {unit_name}")
        self.resize(850, 600)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"<b>Unit:</b> {unit_name}"))

        group = QGroupBox("Assign Unit to Intakes")
        group_layout = QVBoxLayout()

        self.intake_list = QListWidget()
        self.load_available_intakes()

        btn_assign = QPushButton("Assign Selected Intakes to this Unit")
        btn_assign.clicked.connect(self.assign_intakes)

        group_layout.addWidget(self.intake_list)
        group_layout.addWidget(btn_assign)
        group.setLayout(group_layout)
        layout.addWidget(group)

    def load_available_intakes(self):
        self.intake_list.clear()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id, c.name AS course_name, i.label, i.student_count
            FROM intakes i
            JOIN courses c ON i.course_id = c.id
            WHERE i.id NOT IN (SELECT intake_id FROM intake_units WHERE unit_id = ?)
            ORDER BY c.name, i.label
        """, (self.unit_id,))
        
        for iid, course, label, students in cursor.fetchall():
            text = f"{course} → {label}  ({students} students)"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, iid)
            self.intake_list.addItem(item)
        conn.close()

    def assign_intakes(self):
        selected = self.intake_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select at least one intake.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        count = 0

        for item in selected:
            intake_id = item.data(Qt.UserRole)
            try:
                cursor.execute("INSERT INTO intake_units (intake_id, unit_id) VALUES (?, ?)",
                             (intake_id, self.unit_id))
                count += 1
            except sqlite3.IntegrityError:
                pass  # already assigned

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", f"Unit assigned to {count} intake(s).")
        self.load_available_intakes()