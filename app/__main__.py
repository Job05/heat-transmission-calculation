"""__main__.py – Startpunt van de applicatie.

Start de desktop applicatie met::

    python -m app
"""

import sys

from PyQt5.QtWidgets import QApplication

from .config import Config
from .main_window import MainWindow


def main() -> None:
    """Create and run the application."""
    config = Config()
    qt_app = QApplication(sys.argv)
    window = MainWindow(config)
    window.show()
    sys.exit(qt_app.exec_())


if __name__ == "__main__":
    main()
