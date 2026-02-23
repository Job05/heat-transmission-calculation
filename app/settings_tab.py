"""settings_tab.py – Instellingen-tabblad.

Hiermee kan de gebruiker schakelen tussen het donkere en lichte thema.
Alle voorkeuren worden opgeslagen in ``user_preferences.json`` via de
``Config`` klasse.
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

from . import __version__
from .config import Config


class SettingsTab(QWidget):
    """Derde tabblad – applicatie-instellingen."""

    def __init__(self, config: Config, apply_theme_cb: Callable[[str], None]) -> None:
        super().__init__()
        self.config = config
        self._apply_theme = apply_theme_cb

        root = QVBoxLayout(self)

        # ── Uiterlijk ────────────────────────────────────────────────────────
        appearance_group = QGroupBox("Uiterlijk")
        app_layout = QVBoxLayout(appearance_group)

        row = QHBoxLayout()
        row.addWidget(QLabel("Thema:"))
        self.theme_dd = QComboBox()
        self.theme_dd.addItems(["donker", "licht"])
        self.theme_dd.setCurrentText(config.theme)
        self.theme_dd.currentTextChanged.connect(self._on_theme_change)
        row.addWidget(self.theme_dd)
        row.addStretch()
        app_layout.addLayout(row)

        root.addWidget(appearance_group)

        # ── Over ─────────────────────────────────────────────────────────────
        about_group = QGroupBox("Over deze applicatie")
        about_layout = QVBoxLayout(about_group)
        about_layout.addWidget(
            QLabel(
                f"Warmtetransmissie Rekentool  v{__version__}\n\n"
                "Twee rekentools voor warmtetransmissieberekeningen:\n"
                "• U-waarde calculator – warmtedoorgangscoëfficiënt\n"
                "• Correctiefactoren – f_k, f_ia,k, f_ig,k\n\n"
                "Referentiegegevens staan in JSON-bestanden in de map tables/.\n"
                "Gebruikersvoorkeuren worden opgeslagen in user_preferences.json."
            )
        )
        root.addWidget(about_group)

        root.addStretch()

    def _on_theme_change(self, theme: str) -> None:
        self._apply_theme(theme)
