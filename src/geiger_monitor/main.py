"""Entry point for Geiger Monitor application."""

import sys
from PyQt6.QtWidgets import QApplication

from geiger_monitor.main_window import MainWindow


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
