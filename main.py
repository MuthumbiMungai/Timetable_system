import sys
from PyQt5.QtWidgets import QApplication

from database.db import init_db, sync_from_google_sheets
from ui.main_window import MainWindow


def main():
    init_db()

    print("🔄 Syncing latest data from Google Sheets...")
    success = sync_from_google_sheets()

    if success:
        print("✅ Google Sheets sync completed successfully!")
    else:
        print("⚠️ Sync failed - check your internet or Google Sheet sharing.")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()