# ui/main_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Import all management windows
from ui.departments_window import DepartmentsWindow
from ui.trainers_window import TrainersWindow
from ui.units_window import UnitsWindow
from ui.timetable_window import TimetableWindow
# We'll create intakes_window next


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Timetable Management System")
        self.resize(1150, 720)
        self.setMinimumSize(1050, 650)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(25)
        central.setLayout(main_layout)

        # Title
        title = QLabel("📅 Timetable Management System")
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Welcome message
        welcome = QLabel(
            "✅ Database initialized successfully!\n\n"
            "Welcome to the Timetable System.\n"
            "Choose an action below to get started."
        )
        welcome.setFont(QFont("Segoe UI", 13))
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setWordWrap(True)
        main_layout.addWidget(welcome)

        main_layout.addSpacing(20)

        # Buttons in a horizontal row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(18)

        self.btn_departments = QPushButton("🏢 Manage Departments")
        self.btn_trainers    = QPushButton("👨‍🏫 Manage Trainers")
        self.btn_units       = QPushButton("📚 Manage Units")
        self.btn_intakes     = QPushButton("👥 Manage Intakes")
        self.btn_timetable   = QPushButton("🗓️ View / Generate Timetable")

        buttons = [
            self.btn_departments, self.btn_trainers, self.btn_units,
            self.btn_intakes, self.btn_timetable
        ]

        for btn in buttons:
            btn.setMinimumHeight(75)
            btn.setFont(QFont("Segoe UI", 11))
            btn.setStyleSheet("""
                QPushButton {
                    padding: 12px;
                    border: 2px solid #0078d4;
                    border-radius: 8px;
                    background-color: #f0f8ff;
                }
                QPushButton:hover {
                    background-color: #d1e7ff;
                }
            """)
            btn_layout.addWidget(btn)

        main_layout.addLayout(btn_layout)
        main_layout.addStretch(1)

        # Status bar
        self.statusBar().showMessage("Ready • All management features enabled")

        # Button connections
        self.btn_departments.clicked.connect(self.open_departments)
        self.btn_trainers.clicked.connect(self.open_trainers)
        self.btn_units.clicked.connect(self.open_units)
        self.btn_intakes.clicked.connect(self.open_intakes)
        self.btn_timetable.clicked.connect(self.open_timetable)

    # ==================== Window Openers ====================

    def open_departments(self):
        self.dept_window = DepartmentsWindow()
        self.dept_window.show()

    def open_trainers(self):
        self.trainer_window = TrainersWindow()
        self.trainer_window.show()

    def open_units(self):
        self.units_window = UnitsWindow()
        self.units_window.show()

    def open_intakes(self):
        """New dedicated Intakes window"""
        self.intake_window = IntakesWindow()   # Defined in intakes_window.py
        self.intake_window.show()

    def open_timetable(self):
        self.timetable_window = TimetableWindow()
        self.timetable_window.show()