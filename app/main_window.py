"""main_window.py – Top-level application window with three tabs.

Provides the ``MainWindow`` class that owns the tab bar and applies the
dark / light theme globally via Qt style sheets.
"""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
)

from .config import Config
from .u_value_tab import UValueTab
from .fk_calc_tab import FkCalcTab
from .settings_tab import SettingsTab

# ── Dark / Light style sheets ────────────────────────────────────────────────

_DARK_STYLE = """
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #45475a;
    background: #1e1e2e;
}
QTabBar::tab {
    background: #313244;
    color: #cdd6f4;
    padding: 8px 20px;
    border: 1px solid #45475a;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #1e1e2e;
    color: #89b4fa;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background: #45475a;
}
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 14px;
    font-weight: bold;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QLabel {
    color: #cdd6f4;
}
QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit {
    background: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 22px;
}
QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus, QLineEdit:focus {
    border: 1px solid #89b4fa;
}
QComboBox::drop-down {
    border: none;
    width: 22px;
}
QComboBox QAbstractItemView {
    background: #313244;
    color: #cdd6f4;
    selection-background-color: #45475a;
}
QPushButton {
    background: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 4px;
    padding: 6px 16px;
    font-weight: bold;
    min-height: 24px;
}
QPushButton:hover {
    background: #74c7ec;
}
QPushButton:pressed {
    background: #585b70;
    color: #cdd6f4;
}
QPushButton[danger="true"] {
    background: #f38ba8;
    color: #1e1e2e;
}
QPushButton[danger="true"]:hover {
    background: #eba0ac;
}
QCheckBox {
    spacing: 6px;
    color: #cdd6f4;
}
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #45475a;
    border-radius: 3px;
    background: #313244;
}
QCheckBox::indicator:checked {
    background: #89b4fa;
    border-color: #89b4fa;
}
QScrollArea {
    border: none;
}
QTableWidget {
    background: #1e1e2e;
    color: #cdd6f4;
    gridline-color: #45475a;
    border: 1px solid #45475a;
    border-radius: 4px;
}
QTableWidget::item {
    padding: 4px 8px;
}
QHeaderView::section {
    background: #313244;
    color: #89b4fa;
    padding: 6px 8px;
    border: 1px solid #45475a;
    font-weight: bold;
}
QRadioButton {
    color: #cdd6f4;
    spacing: 6px;
}
QRadioButton::indicator {
    width: 14px; height: 14px;
    border: 1px solid #45475a;
    border-radius: 7px;
    background: #313244;
}
QRadioButton::indicator:checked {
    background: #89b4fa;
    border-color: #89b4fa;
}
"""

_LIGHT_STYLE = """
QWidget {
    background-color: #eff1f5;
    color: #4c4f69;
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #bcc0cc;
    background: #eff1f5;
}
QTabBar::tab {
    background: #ccd0da;
    color: #4c4f69;
    padding: 8px 20px;
    border: 1px solid #bcc0cc;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #eff1f5;
    color: #1e66f5;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background: #bcc0cc;
}
QGroupBox {
    border: 1px solid #bcc0cc;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 14px;
    font-weight: bold;
    color: #1e66f5;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QLabel {
    color: #4c4f69;
}
QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit {
    background: #ffffff;
    color: #4c4f69;
    border: 1px solid #bcc0cc;
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 22px;
}
QComboBox:focus, QDoubleSpinBox:focus, QSpinBox:focus, QLineEdit:focus {
    border: 1px solid #1e66f5;
}
QComboBox::drop-down {
    border: none;
    width: 22px;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    color: #4c4f69;
    selection-background-color: #ccd0da;
}
QPushButton {
    background: #1e66f5;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 6px 16px;
    font-weight: bold;
    min-height: 24px;
}
QPushButton:hover {
    background: #2a7bff;
}
QPushButton:pressed {
    background: #6c6f85;
    color: #ffffff;
}
QPushButton[danger="true"] {
    background: #d20f39;
    color: #ffffff;
}
QPushButton[danger="true"]:hover {
    background: #e64553;
}
QCheckBox {
    spacing: 6px;
    color: #4c4f69;
}
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 1px solid #bcc0cc;
    border-radius: 3px;
    background: #ffffff;
}
QCheckBox::indicator:checked {
    background: #1e66f5;
    border-color: #1e66f5;
}
QScrollArea {
    border: none;
}
QTableWidget {
    background: #ffffff;
    color: #4c4f69;
    gridline-color: #bcc0cc;
    border: 1px solid #bcc0cc;
    border-radius: 4px;
}
QTableWidget::item {
    padding: 4px 8px;
}
QHeaderView::section {
    background: #ccd0da;
    color: #1e66f5;
    padding: 6px 8px;
    border: 1px solid #bcc0cc;
    font-weight: bold;
}
QRadioButton {
    color: #4c4f69;
    spacing: 6px;
}
QRadioButton::indicator {
    width: 14px; height: 14px;
    border: 1px solid #bcc0cc;
    border-radius: 7px;
    background: #ffffff;
}
QRadioButton::indicator:checked {
    background: #1e66f5;
    border-color: #1e66f5;
}
"""

THEMES = {"dark": _DARK_STYLE, "light": _LIGHT_STYLE}


class MainWindow(QMainWindow):
    """Application main window containing the three-tab interface."""

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        self.setWindowTitle("Heat Transmission Calculator")
        self.resize(config.window_width, config.window_height)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create tabs
        self.u_value_tab = UValueTab(config)
        self.fk_calc_tab = FkCalcTab(config)
        self.settings_tab = SettingsTab(config, self._apply_theme)

        self.tabs.addTab(self.u_value_tab, "U-waarde Calculator")
        self.tabs.addTab(self.fk_calc_tab, "Correctiefactoren")
        self.tabs.addTab(self.settings_tab, "Instellingen")

        # Apply stored theme
        self._apply_theme(config.theme)

    # ── theming ──────────────────────────────────────────────────────────────

    def _apply_theme(self, theme_name: str) -> None:
        """Apply a named theme to the entire application."""
        sheet = THEMES.get(theme_name, THEMES["dark"])
        self.setStyleSheet(sheet)
        self.config.theme = theme_name
        self.config.save()

    # ── window lifecycle ─────────────────────────────────────────────────────

    def closeEvent(self, event: "QCloseEvent") -> None:  # noqa: N802
        """Persist window dimensions on close."""
        self.config.set("window_width", self.width())
        self.config.set("window_height", self.height())
        self.config.save()
        super().closeEvent(event)
