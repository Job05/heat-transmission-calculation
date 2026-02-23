"""settings_tab.py – Settings tab for appearance and configuration.

Allows the user to switch between dark and light themes.  All preferences
are persisted to ``user_preferences.json`` via the ``Config`` helper.
"""

from __future__ import annotations

from typing import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from .config import Config


class SettingsTab(QWidget):
    """Third tab – application settings (theme, future options)."""

    def __init__(self, config: Config, apply_theme_cb: Callable[[str], None]) -> None:
        super().__init__()
        self.config = config
        self._apply_theme = apply_theme_cb

        root = QVBoxLayout(self)

        # ── Appearance ───────────────────────────────────────────────────────
        appearance_group = QGroupBox("Uiterlijk / Appearance")
        app_layout = QVBoxLayout(appearance_group)

        row = QHBoxLayout()
        row.addWidget(QLabel("Thema / Theme:"))
        self.theme_dd = QComboBox()
        self.theme_dd.addItems(["dark", "light"])
        self.theme_dd.setCurrentText(config.theme)
        self.theme_dd.currentTextChanged.connect(self._on_theme_change)
        row.addWidget(self.theme_dd)
        row.addStretch()
        app_layout.addLayout(row)

        root.addWidget(appearance_group)

        # ── About / Info ─────────────────────────────────────────────────────
        about_group = QGroupBox("Over / About")
        about_layout = QVBoxLayout(about_group)
        about_layout.addWidget(
            QLabel(
                "Heat Transmission Calculator\n\n"
                "Desktop application converted from the Jupyter Notebook tools.\n"
                "• Tool 1: U-waarde / warmtedoorgangscoëfficiënt\n"
                "• Tool 2: Correctiefactoren f_k, f_ia,k, f_ig,k\n\n"
                "All reference data is stored in JSON files under the tables/ folder.\n"
                "User preferences are saved to user_preferences.json."
            )
        )
        root.addWidget(about_group)

        # ── Future settings placeholder ──────────────────────────────────────
        future_group = QGroupBox("Overige instellingen / Other settings")
        future_layout = QVBoxLayout(future_group)
        future_layout.addWidget(
            QLabel(
                "Additional settings (e.g. language, custom table paths) can be\n"
                "added here in the future.  See app/README.md for instructions."
            )
        )
        root.addWidget(future_group)

        root.addStretch()

    def _on_theme_change(self, theme: str) -> None:
        self._apply_theme(theme)
