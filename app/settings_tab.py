"""settings_tab.py – Instellingen-tabblad.

Hiermee kan de gebruiker schakelen tussen het donkere en lichte thema
en de applicatiegrootte aanpassen.  Alle voorkeuren worden opgeslagen
in ``user_preferences.json`` via de ``Config`` klasse.
"""

from __future__ import annotations

from typing import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from . import __version__
from .config import Config, SCALE_FONT_SIZES


class SettingsTab(QWidget):
    """Derde tabblad – applicatie-instellingen."""

    def __init__(
        self,
        config: Config,
        apply_theme_cb: Callable[[str], None],
        apply_scale_cb: Callable[[str], None],
    ) -> None:
        super().__init__()
        self.config = config
        self._apply_theme = apply_theme_cb
        self._apply_scale = apply_scale_cb

        root = QVBoxLayout(self)

        # ── Thema ─────────────────────────────────────────────────────────────
        theme_group = QGroupBox("Thema")
        form = QFormLayout(theme_group)

        self.theme_dd = QComboBox()
        self.theme_dd.addItems(["donker", "licht"])
        self.theme_dd.setCurrentText(config.theme)
        self.theme_dd.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.theme_dd.currentTextChanged.connect(self._on_theme_change)
        form.addRow("Kleurenschema:", self.theme_dd)

        self.scale_dd = QComboBox()
        self.scale_dd.addItems(list(SCALE_FONT_SIZES.keys()))
        self.scale_dd.setCurrentText(config.app_scale)
        self.scale_dd.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.scale_dd.currentTextChanged.connect(self._on_scale_change)
        form.addRow("Applicatiegrootte:", self.scale_dd)

        root.addWidget(theme_group)

        # ── Over ─────────────────────────────────────────────────────────────
        about_group = QGroupBox("Over deze applicatie")
        about_layout = QVBoxLayout(about_group)
        about_label = QLabel(
            f"Warmtetransmissie Rekentool  v{__version__}\n\n"
            "Twee rekentools voor warmtetransmissieberekeningen:\n"
            "• U-waarde calculator – warmtedoorgangscoëfficiënt\n"
            "• Correctiefactoren – f_k, f_ia,k, f_ig,k\n\n"
            "Referentiegegevens staan in JSON-bestanden in de map tables/.\n"
            "Gebruikersvoorkeuren worden opgeslagen in user_preferences.json."
        )
        about_label.setWordWrap(True)
        about_layout.addWidget(about_label)
        root.addWidget(about_group)

        root.addStretch()

    def _on_theme_change(self, theme: str) -> None:
        self._apply_theme(theme)

    def _on_scale_change(self, scale: str) -> None:
        self._apply_scale(scale)
