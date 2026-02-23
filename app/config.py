"""config.py – Gebruikersvoorkeuren en configuratie.

Alle instellingen worden opgeslagen als JSON-bestand zodat ze
bewaard blijven tussen sessies.  De ``Config`` klasse biedt getypte
toegang tot elke opgeslagen sleutel met standaardwaarden.
"""

from __future__ import annotations

import json
import os
from typing import Any

_DEFAULT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "user_preferences.json",
)

_DEFAULTS: dict[str, Any] = {
    "theme": "donker",
    "app_scale": "Normaal",
    "window_width": 1100,
    "window_height": 750,
}

# Lettergrootte in pixels per schaaloptie (voor de instellingen)
SCALE_FONT_SIZES: dict[str, int] = {
    "Klein": 13,
    "Normaal": 15,
    "Groot": 17,
    "Extra groot": 20,
}


class Config:
    """Read / write user preferences backed by a JSON file."""

    def __init__(self, path: str = _DEFAULT_PATH) -> None:
        self._path = path
        self._data: dict[str, Any] = dict(_DEFAULTS)
        self._load()

    # ── persistence ──────────────────────────────────────────────────────────

    def _load(self) -> None:
        """Load preferences from disk (silently keep defaults on error)."""
        if os.path.isfile(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as fh:
                    stored = json.load(fh)
                if isinstance(stored, dict):
                    self._data.update(stored)
            except (json.JSONDecodeError, OSError):
                pass

    def save(self) -> None:
        """Write current preferences to disk."""
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2, ensure_ascii=False)

    # ── generic access ───────────────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    # ── typed convenience properties ─────────────────────────────────────────

    @property
    def theme(self) -> str:
        return self._data.get("theme", "donker")

    @theme.setter
    def theme(self, value: str) -> None:
        self._data["theme"] = value

    @property
    def window_width(self) -> int:
        return int(self._data.get("window_width", 1100))

    @property
    def window_height(self) -> int:
        return int(self._data.get("window_height", 750))

    @property
    def app_scale(self) -> str:
        return self._data.get("app_scale", "Normaal")

    @app_scale.setter
    def app_scale(self, value: str) -> None:
        self._data["app_scale"] = value
