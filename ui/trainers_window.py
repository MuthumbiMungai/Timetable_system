# ui/trainers_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QFormLayout,
    QMessageBox, QGroupBox, QHeaderView, QDialog, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sqlite3
from database.db import get_connection
from datetime import datetime


class TrainersWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Trainers")
        self.resize(1100, 700)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        title = QLabel("👨‍🏫 Trainer Management")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Add New Trainer
        add_group = QGroupBox("Add New Trainer")
        add_layout = QHBoxLayout()

        self.trainer_name = QLineEdit()
        self.trainer_name.setPlaceholderText("Full Name")
        self.trainer_email = QLineEdit()
        self.trainer_email.setPlaceholderText("Email (optional)")

        self.dept_combo = QComboBox()
        self.load_departments()

        btn_add = QPushButton("Add Trainer")
        btn_add.clicked.connect(self.add_trainer)

        add_layout.addWidget(QLabel("Name:"))
        add_layout.addWidget(self.trainer_name)
        add_layout.addWidget(QLabel("Department:"))
        add_layout.addWidget(self.dept_combo)
        add_layout.addWidget(QLabel("Email:"))
        add_layout.addWidget(self.trainer_email)
        add_layout.addWidget(btn_add)

        add_group.setLayout(add_layout)
        main_layout.addWidget(add_group)

        # Action Buttons
        action_layout = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Refresh")
        btn_edit = QPushButton("✏️ Edit Selected")
        btn_delete = QPushButton("🗑️ Delete Selected")
        btn_summary = QPushButton("📊 View Summary / Log")

        btn_refresh.clicked.connect(self.load_trainers)
        btn_edit.clicked.connect(self.edit_trainer)
        btn_delete.clicked.connect(self.delete_trainer)
        btn_summary.clicked.connect(self.show_summary)

        action_layout.addWidget(btn_refresh)
        action_layout.addWidget(btn_edit)
        action_layout.addWidget(btn_delete)
        action_layout.addWidget(btn_summary)
        action_layout.addStretch()
        main_layout.addLayout(action_layout)

        # Trainers Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Full Name", "Department", "Email"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.doubleClicked.connect(self.edit_trainer)   # Double-click also edits
        main_layout.addWidget(self.table)

        self.load_trainers()

    def load_departments(self):
        self.dept_combo.clear()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM departments ORDER BY name")
        for dept_id, name in cursor.fetchall():
            self.dept_combo.addItem(name, dept_id)
        conn.close()

    def load_trainers(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.id, t.full_name, d.name, t.email 
            FROM trainers t
            JOIN departments d ON t.department_id = d.id
            ORDER BY t.full_name
        """)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, (tid, name, dept, email) in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(tid)))
            self.table.setItem(i, 1, QTableWidgetItem(name))
            self.table.setItem(i, 2, QTableWidgetItem(dept))
            self.table.setItem(i, 3, QTableWidgetItem(email or ""))

    def add_trainer(self):
        name = self.trainer_name.text().strip()
        email = self.trainer_email.text().strip() or None
        dept_id = self.dept_combo.currentData()

        if not name or not dept_id:
            QMessageBox.warning(self, "Error", "Name and Department are required!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trainers (department_id, full_name, email)
                VALUES (?, ?, ?)
            """, (dept_id, name, email))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Trainer added successfully!")
            self.trainer_name.clear()
            self.trainer_email.clear()
            self.load_trainers()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Email already exists!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def edit_trainer(self, index=None):
        if index is None:  # Called from button
            row = self.table.currentRow()
        else:
            row = index.row()

        if row < 0:
            QMessageBox.warning(self, "Error", "Please select a trainer to edit!")
            return

        trainer_id = int(self.table.item(row, 0).text())
        current_name = self.table.item(row, 1).text()
        current_email = self.table.item(row, 3).text()

        dialog = EditTrainerDialog(trainer_id, current_name, current_email, self)
        if dialog.exec_():
            self.load_trainers()

    def delete_trainer(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Please select a trainer to delete.")
            return

        trainer_id = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()

        # Check if trainer is used in timetable
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM timetable_entries WHERE trainer_id = ?", (trainer_id,))
        count = cursor.fetchone()[0]
        conn.close()

        if count > 0:
            reply = QMessageBox.question(self, "Warning",
                                         f"Trainer '{name}' is assigned to {count} timetable slot(s).\n"
                                         "Deleting will remove those assignments. Continue?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return

        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Delete trainer '{name}'?\nThis cannot be undone.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM timetable_entries WHERE trainer_id = ?", (trainer_id,))
            cursor.execute("DELETE FROM trainers WHERE id = ?", (trainer_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Trainer deleted successfully.")
            self.load_trainers()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_summary(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trainers")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT d.name, COUNT(t.id)
            FROM departments d
            LEFT JOIN trainers t ON t.department_id = d.id
            GROUP BY d.id, d.name
            ORDER BY d.name
        """)
        breakdown = cursor.fetchall()
        conn.close()

        text = f"<b>👨‍🏫 TRAINERS SUMMARY</b><br>Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}<br><br>"
        text += f"Total Trainers: {total}<br><br><b>Department Breakdown:</b><br>"
        for dept, count in breakdown:
            text += f"• {dept} → {count} trainer(s)<br>"

        msg = QMessageBox(self)
        msg.setWindowTitle("Trainers Summary / Log")
        msg.setTextFormat(Qt.RichText)
        msg.setText(text)
        msg.exec_()


# ====================== Edit Trainer Dialog ======================
class EditTrainerDialog(QDialog):
    def __init__(self, trainer_id: int, current_name: str, current_email: str, parent=None):
        super().__init__(parent)
        self.trainer_id = trainer_id
        self.setWindowTitle("Edit Trainer")
        self.resize(500, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()
        self.name_edit = QLineEdit(current_name)
        self.email_edit = QLineEdit(current_email or "")

        form.addRow("Full Name:", self.name_edit)
        form.addRow("Email:", self.email_edit)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.save_changes)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def save_changes(self):
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip() or None

        if not name:
            QMessageBox.warning(self, "Error", "Name cannot be empty!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE trainers SET full_name = ?, email = ? WHERE id = ?",
                           (name, email, self.trainer_id))
            conn.commit()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))