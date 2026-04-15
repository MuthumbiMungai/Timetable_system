# ui/units_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QSpinBox,
    QCheckBox, QFormLayout, QMessageBox, QGroupBox, QHeaderView, QDialog,
    QListWidget, QListWidgetItem, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sqlite3
from database.db import get_connection
from datetime import datetime


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

        # Action Buttons
        action_layout = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Refresh")
        btn_edit = QPushButton("✏️ Edit Selected")
        btn_delete = QPushButton("🗑️ Delete Selected")
        btn_summary = QPushButton("📊 View Summary / Log")

        btn_refresh.clicked.connect(self.load_units)
        btn_edit.clicked.connect(self.edit_unit)
        btn_delete.clicked.connect(self.delete_unit)
        btn_summary.clicked.connect(self.show_summary)

        action_layout.addWidget(btn_refresh)
        action_layout.addWidget(btn_edit)
        action_layout.addWidget(btn_delete)
        action_layout.addWidget(btn_summary)
        action_layout.addStretch()
        main_layout.addLayout(action_layout)

        # Units Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Code", "Department", "Hours"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.doubleClicked.connect(self.show_unit_details)

        main_layout.addWidget(self.table)

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
            QMessageBox.warning(self, "Duplicate", f"Unit code '{code}' already exists!")

    def clear_form(self):
        self.unit_name.clear()
        self.unit_code.clear()
        self.hours_spin.setValue(2)
        self.shared_check.setChecked(False)

    def edit_unit(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Please select a unit to edit!")
            return

        unit_id = int(self.table.item(row, 0).text())
        curr_name = self.table.item(row, 1).text()
        curr_code = self.table.item(row, 2).text()
        curr_hours = int(self.table.item(row, 4).text())

        new_name, ok = QInputDialog.getText(self, "Edit Unit", "Unit Name:", text=curr_name)
        if not ok or not new_name.strip(): return
        new_code, ok = QInputDialog.getText(self, "Edit Unit", "Unit Code:", text=curr_code)
        if not ok or not new_code.strip(): return
        new_hours, ok = QInputDialog.getInt(self, "Edit Unit", "Hours per Week:", 
                                           value=curr_hours, min=1, max=6)
        if not ok: return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE units SET name=?, code=?, hours_per_week=? 
                WHERE id=?
            """, (new_name.strip(), new_code.strip().upper(), new_hours, unit_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Unit updated successfully!")
            self.load_units()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Unit code already exists!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_unit(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Please select a unit first.")
            return

        unit_id = int(self.table.item(row, 0).text())
        code = self.table.item(row, 2).text()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM intake_units WHERE unit_id = ?", (unit_id,))
        assigned = cursor.fetchone()[0]
        conn.close()

        if assigned > 0:
            reply = QMessageBox.question(self, "Warning",
                                         f"Unit '{code}' is assigned to {assigned} intake(s).\n"
                                         "Continue with deletion?", QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return

        reply = QMessageBox.question(self, "Delete Unit",
                                     f"Delete unit '{code}'?\nThis cannot be undone.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM intake_units WHERE unit_id = ?", (unit_id,))
            cursor.execute("DELETE FROM units WHERE id = ?", (unit_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Unit deleted successfully.")
            self.load_units()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_summary(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM units"); total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM intake_units"); assignments = cursor.fetchone()[0]

        cursor.execute("""
            SELECT d.name, COUNT(u.id)
            FROM departments d
            LEFT JOIN units u ON u.department_id = d.id
            GROUP BY d.id ORDER BY d.name
        """)
        breakdown = cursor.fetchall()
        conn.close()

        text = f"<b>📚 UNITS SUMMARY</b><br>Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}<br><br>"
        text += f"Total Units: {total}<br>Total Assignments: {assignments}<br><br><b>Department Breakdown:</b><br>"
        for dept, count in breakdown:
            text += f"• {dept} → {count} unit(s)<br>"

        msg = QMessageBox(self)
        msg.setWindowTitle("Units Summary / Log")
        msg.setTextFormat(Qt.RichText)
        msg.setText(text)
        msg.exec_()

    def show_unit_details(self, index):
        row = index.row()
        unit_id = int(self.table.item(row, 0).text())
        unit_name = self.table.item(row, 1).text()
        dialog = UnitDetailDialog(unit_id, unit_name, self)
        dialog.exec_()