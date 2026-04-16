from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QMessageBox, QTabWidget, QInputDialog
)
from PyQt5.QtCore import Qt

from ui.departments_window import DepartmentsWindow
from ui.trainers_window import TrainersWindow
from ui.units_window import UnitsWindow
from ui.timetable_window import TimetableWindow


class PlaceholderWindow(QWidget):
    def __init__(self, title="Coming Soon"):
        super().__init__()
        self.setWindowTitle(title)
        layout = QVBoxLayout()
        label = QLabel(f"<h2>{title}</h2><p>This section is under development.</p>")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("College Timetable System - Live from Google Sheets")
        self.setGeometry(100, 100, 1300, 850)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        header = QLabel("🎓 TIMETABLE MANAGEMENT SYSTEM")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 15px; background: #2c3e50; color: white;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tabs.addTab(DepartmentsWindow(), "Departments & Courses")
        self.tabs.addTab(TrainersWindow(), "Trainers")
        self.tabs.addTab(UnitsWindow(), "Units / Subjects")
        self.tabs.addTab(TimetableWindow(), "Timetable")
        self.tabs.addTab(PlaceholderWindow("Intakes"), "Intakes")
        self.tabs.addTab(PlaceholderWindow("Reports"), "Reports")

        # Bottom Action Buttons
        btn_layout = QHBoxLayout()

        sync_btn = QPushButton("🔄 Sync Latest Data from Google Sheets")
        sync_btn.setStyleSheet("background: #27ae60; color: white; font-weight: bold; padding: 10px;")
        sync_btn.clicked.connect(self.sync_google_sheets)
        btn_layout.addWidget(sync_btn)

        export_btn = QPushButton("📄 Export Timetable to Word")
        export_btn.clicked.connect(self.export_to_word)
        btn_layout.addWidget(export_btn)

        refresh_btn = QPushButton("Refresh Views")
        refresh_btn.clicked.connect(self.refresh_views)
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)

    def sync_google_sheets(self):
        try:
            from database.db import sync_from_google_sheets
            success = sync_from_google_sheets()
            if success:
                QMessageBox.information(self, "Success", 
                    "Data successfully synced from Google Sheets!\n\n"
                    "Departments, Courses, Intakes & Trainers are now up to date.")
                self.refresh_views()
            else:
                QMessageBox.warning(self, "Sync Incomplete", "Some data could not be synced.")
        except Exception as e:
            QMessageBox.critical(self, "Sync Error", f"Failed to sync:\n{str(e)}")

    def export_to_word(self):
        dept_code, ok = QInputDialog.getText(self, "Export", "Enter Department Code (e.g. APPLIED):")
        if ok and dept_code.strip():
            try:
                from services.export_to_word import export_department_timetable
                export_department_timetable(dept_code.strip().upper())
                QMessageBox.information(self, "Exported", f"Timetable exported for {dept_code.upper()}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def refresh_views(self):
        # You can add refresh logic for each tab later
        QMessageBox.information(self, "Refresh", "Views refreshed (full refresh coming soon).")


from PyQt5.QtWidgets import QInputDialog