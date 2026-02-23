"""main_window.py – Hoofdvenster met drie tabbladen.

Bevat de ``MainWindow`` klasse met de tabbladbalk en past het donkere of
lichte thema toe via Qt-stylesheets.  Kleurenpalet: brandweer
(oranje / rood / blauw).
"""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
)

from . import __version__
from .config import Config
from .u_value_tab import UValueTab
from .fk_calc_tab import FkCalcTab
from .settings_tab import SettingsTab

# ── Donker thema (brandweer) ─────────────────────────────────────────────────

_DARK_STYLE = """
QWidget {
    background-color: #1a1d2e;
    color: #ffffff;
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 14px;
}
QTabWidget::pane {
    border: 1px solid #3a3d5c;
    background: #1a1d2e;
}
QTabBar::tab {
    background: #252840;
    color: #ffffff;
    padding: 10px 22px;
    border: 1px solid #3a3d5c;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    font-size: 14px;
}
QTabBar::tab:selected {
    background: #1a1d2e;
    color: #ff6d00;
    font-weight: bold;
    border-bottom: 2px solid #ff6d00;
}
QTabBar::tab:hover:!selected {
    background: #2e3150;
}
QGroupBox {
    border: 1px solid #3a3d5c;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: #ff6d00;
    font-size: 14px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QLabel {
    color: #ffffff;
    font-size: 14px;
}
QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit {
    background: #252840;
    color: #ffffff;
    border: 1px solid #3a3d5c;
    border-radius: 4px;
    padding: 6px 10px;
    min-height: 30px;
    font-size: 14px;
}
QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus, QLineEdit:focus {
    border: 1px solid #ff6d00;
}
QComboBox::drop-down {
    border: none;
    width: 26px;
}
QComboBox QAbstractItemView {
    background: #252840;
    color: #ffffff;
    selection-background-color: #3a3d5c;
    font-size: 14px;
    min-height: 28px;
}
QComboBox QAbstractItemView::item {
    min-height: 28px;
    padding: 4px 8px;
}
QPushButton {
    background: #ff6d00;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 14px;
}
QPushButton:hover {
    background: #ff8f00;
}
QPushButton:pressed {
    background: #e65100;
}
QPushButton[danger="true"] {
    background: #d32f2f;
    color: #ffffff;
}
QPushButton[danger="true"]:hover {
    background: #e53935;
}
QPushButton[secondary="true"] {
    background: #1565c0;
    color: #ffffff;
}
QPushButton[secondary="true"]:hover {
    background: #1976d2;
}
QCheckBox {
    spacing: 8px;
    color: #ffffff;
    font-size: 14px;
}
QCheckBox::indicator {
    width: 18px; height: 18px;
    border: 2px solid #3a3d5c;
    border-radius: 3px;
    background: #252840;
}
QCheckBox::indicator:checked {
    background: #ff6d00;
    border-color: #ff6d00;
}
QScrollArea {
    border: none;
}
QTableWidget {
    background: #1a1d2e;
    color: #ffffff;
    gridline-color: #3a3d5c;
    border: 1px solid #3a3d5c;
    border-radius: 4px;
    font-size: 14px;
}
QTableWidget::item {
    padding: 6px 10px;
}
QHeaderView::section {
    background: #252840;
    color: #ff6d00;
    padding: 8px 10px;
    border: 1px solid #3a3d5c;
    font-weight: bold;
    font-size: 14px;
}
QRadioButton {
    color: #ffffff;
    spacing: 8px;
    font-size: 14px;
}
QRadioButton::indicator {
    width: 16px; height: 16px;
    border: 2px solid #3a3d5c;
    border-radius: 8px;
    background: #252840;
}
QRadioButton::indicator:checked {
    background: #ff6d00;
    border-color: #ff6d00;
}
QFrame[frameShape="6"] {
    border: 1px solid #3a3d5c;
    border-radius: 6px;
    background: #20233a;
}
"""

_LIGHT_STYLE = """
QWidget {
    background-color: #f0f0f0;
    color: #1a1a1a;
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 14px;
}
QTabWidget::pane {
    border: 1px solid #999999;
    background: #f0f0f0;
}
QTabBar::tab {
    background: #d6d6d6;
    color: #1a1a1a;
    padding: 10px 22px;
    border: 1px solid #999999;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    font-size: 14px;
}
QTabBar::tab:selected {
    background: #f0f0f0;
    color: #e65100;
    font-weight: bold;
    border-bottom: 2px solid #e65100;
}
QTabBar::tab:hover:!selected {
    background: #c0c0c0;
}
QGroupBox {
    border: 1px solid #999999;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: #e65100;
    font-size: 14px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QLabel {
    color: #1a1a1a;
    font-size: 14px;
}
QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit {
    background: #ffffff;
    color: #1a1a1a;
    border: 1px solid #999999;
    border-radius: 4px;
    padding: 6px 10px;
    min-height: 30px;
    font-size: 14px;
}
QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus, QLineEdit:focus {
    border: 1px solid #e65100;
}
QComboBox::drop-down {
    border: none;
    width: 26px;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    color: #1a1a1a;
    selection-background-color: #ffe0b2;
    font-size: 14px;
    min-height: 28px;
}
QComboBox QAbstractItemView::item {
    min-height: 28px;
    padding: 4px 8px;
}
QPushButton {
    background: #e65100;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 14px;
}
QPushButton:hover {
    background: #ff6d00;
}
QPushButton:pressed {
    background: #bf360c;
}
QPushButton[danger="true"] {
    background: #c62828;
    color: #ffffff;
}
QPushButton[danger="true"]:hover {
    background: #d32f2f;
}
QPushButton[secondary="true"] {
    background: #0d47a1;
    color: #ffffff;
}
QPushButton[secondary="true"]:hover {
    background: #1565c0;
}
QCheckBox {
    spacing: 8px;
    color: #1a1a1a;
    font-size: 14px;
}
QCheckBox::indicator {
    width: 18px; height: 18px;
    border: 2px solid #999999;
    border-radius: 3px;
    background: #ffffff;
}
QCheckBox::indicator:checked {
    background: #e65100;
    border-color: #e65100;
}
QScrollArea {
    border: none;
}
QTableWidget {
    background: #ffffff;
    color: #1a1a1a;
    gridline-color: #999999;
    border: 1px solid #999999;
    border-radius: 4px;
    font-size: 14px;
}
QTableWidget::item {
    padding: 6px 10px;
}
QHeaderView::section {
    background: #d6d6d6;
    color: #e65100;
    padding: 8px 10px;
    border: 1px solid #999999;
    font-weight: bold;
    font-size: 14px;
}
QRadioButton {
    color: #1a1a1a;
    spacing: 8px;
    font-size: 14px;
}
QRadioButton::indicator {
    width: 16px; height: 16px;
    border: 2px solid #999999;
    border-radius: 8px;
    background: #ffffff;
}
QRadioButton::indicator:checked {
    background: #e65100;
    border-color: #e65100;
}
QFrame[frameShape="6"] {
    border: 1px solid #999999;
    border-radius: 6px;
    background: #e8e8e8;
}
"""

THEMES = {"donker": _DARK_STYLE, "licht": _LIGHT_STYLE}


class MainWindow(QMainWindow):
    """Hoofdvenster met drie tabbladen."""

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        self.setWindowTitle(f"Warmtetransmissie Rekentool  v{__version__}")
        self.resize(config.window_width, config.window_height)

        # Centraal widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)

        # Tabbladen
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.u_value_tab = UValueTab(config)
        self.fk_calc_tab = FkCalcTab(config)
        self.settings_tab = SettingsTab(config, self._apply_theme)

        self.tabs.addTab(self.u_value_tab, "U-waarde Calculator")
        self.tabs.addTab(self.fk_calc_tab, "Correctiefactoren")
        self.tabs.addTab(self.settings_tab, "Instellingen")

        # Sla het thema op en pas toe
        self._apply_theme(config.theme)

    def _apply_theme(self, theme_name: str) -> None:
        """Pas het opgegeven thema toe op de gehele applicatie."""
        sheet = THEMES.get(theme_name, THEMES["donker"])
        self.setStyleSheet(sheet)
        self.config.theme = theme_name
        self.config.save()

    def closeEvent(self, event: "QCloseEvent") -> None:  # noqa: N802
        """Sla vensterafmetingen op bij sluiten."""
        self.config.set("window_width", self.width())
        self.config.set("window_height", self.height())
        self.config.save()
        super().closeEvent(event)
