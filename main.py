import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from database.db import initialize_database


def main():
    initialize_database()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")        # Helps with consistent look on Windows
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()