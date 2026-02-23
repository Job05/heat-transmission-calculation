"""fk_calc_tab.py – Tool 2: Correction-factor calculator.

Replicates the scenario-based correction-factor form from the Jupyter
notebook using PyQt5.  Dynamic fields are shown/hidden depending on the
selected scenario.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# ── Import calculation back-end from repo root ───────────────────────────────
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import fk_calc  # noqa: E402

# Pre-compute lookup data for dropdowns
_HEATING_SYSTEMS = fk_calc.list_heating_systems()
_HS_OPTIONS: dict[str, str] = {s["omschrijving"]: s["id"] for s in _HEATING_SYSTEMS}
_HS_LIST = list(_HS_OPTIONS.keys())

_ROOM_TYPES_WOON = fk_calc.list_room_types("woonfunctie")

# Mapping from UI labels to internal keys
_BUITENLUCHT_BD = {
    "Buitenwand": "buitenwand",
    "Schuin dak": "schuin_dak",
    "Vloer boven buitenlucht": "vloer_boven_buitenlucht",
    "Plat dak": "plat_dak",
}

_RUIMTE_MAP = {
    "Vertrek": "vertrek",
    "Ruimte onder dak": "dak",
    "Verkeersruimte": "verkeersruimte",
    "Kruipruimte": "kruipruimte",
}

_DAKTYPE_MAP = {
    "Pannendak zonder folie (hoog infiltratievoud)": "pannendak_zonder_folie",
    "Overige niet-geïsoleerde daken": "niet_geisoleerd",
    "Geïsoleerde daken": "geisoleerd",
}

_GEVEL_OPTIONS = [
    ("1 externe scheidingsconstructie / buitenwand", 1, None),
    ("2 externe scheidingsconstructies – zonder buitendeur", 2, False),
    ("2 externe scheidingsconstructies – met buitendeur", 2, True),
    ("3 of meer externe scheidingsconstructies", 3, None),
]

_TIJDCONST_MAP = {
    "Kelder": "kelder",
    "Stallingsruimte": "stallingsruimte",
    "Kruipruimte / serre / trappenhuis": "kruipruimte_serre_trappenhuis",
}

_GW_OPTIONS = [
    ("Grondwater ≥ 1 m onder vloer  →  f_gw = 1,00", 1.00),
    ("Grondwater < 1 m onder vloer of onbekend  →  f_gw = 1,15", 1.15),
]

# ── Scenarios ────────────────────────────────────────────────────────────────
SCENARIOS = [
    "Buitenlucht",
    "Aangrenzend gebouw",
    "Verwarmde ruimte (zelfde woning)",
    "Onverwarmde ruimte – bekende temperatuur",
    "Onverwarmde ruimte – onbekende temperatuur",
    "Grond",
]


def _make_hs_combo() -> QComboBox:
    """Create a heating-system combo box."""
    cb = QComboBox()
    cb.addItems(_HS_LIST)
    return cb


def _make_float(value: float, lo: float, hi: float, step: float, decimals: int = 1) -> QDoubleSpinBox:
    sb = QDoubleSpinBox()
    sb.setRange(lo, hi)
    sb.setDecimals(decimals)
    sb.setSingleStep(step)
    sb.setValue(value)
    return sb


# ── Tab widget ───────────────────────────────────────────────────────────────


class FkCalcTab(QWidget):
    """Second tool tab – correction-factor calculator."""

    def __init__(self, config) -> None:
        super().__init__()
        self.config = config

        root = QVBoxLayout(self)

        # ── Scenario selector ────────────────────────────────────────────────
        scenario_group = QGroupBox("Kies aangrenzende situatie")
        sg_layout = QHBoxLayout(scenario_group)
        sg_layout.addWidget(QLabel("Situatie:"))
        self.scenario_dd = QComboBox()
        self.scenario_dd.addItems(SCENARIOS)
        sg_layout.addWidget(self.scenario_dd, 1)
        root.addWidget(scenario_group)

        # ── Shared temperature inputs ────────────────────────────────────────
        temp_group = QGroupBox("Temperaturen")
        temp_layout = QHBoxLayout(temp_group)
        temp_layout.addWidget(QLabel("θ_i (binnen) [°C]:"))
        self.theta_i = _make_float(22, -50, 50, 0.5)
        temp_layout.addWidget(self.theta_i)
        temp_layout.addWidget(QLabel("θ_e (buiten) [°C]:"))
        self.theta_e = _make_float(-10, -50, 50, 0.5)
        temp_layout.addWidget(self.theta_e)
        temp_layout.addStretch()
        root.addWidget(temp_group)
        self.temp_group = temp_group

        # ── Dynamic fields container ─────────────────────────────────────────
        self.fields_group = QGroupBox("Invoervelden")
        self.fields_layout = QVBoxLayout(self.fields_group)
        root.addWidget(self.fields_group)

        # ── Result table ─────────────────────────────────────────────────────
        res_group = QGroupBox("Resultaat")
        res_layout = QVBoxLayout(res_group)
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(2)
        self.result_table.setHorizontalHeaderLabels(["Factor", "Waarde"])
        hdr = self.result_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        res_layout.addWidget(self.result_table)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #f38ba8; font-weight: bold;")
        res_layout.addWidget(self.error_label)
        root.addWidget(res_group)

        # ── Create all scenario-specific widgets (once) ──────────────────────
        self._create_scenario_widgets()

        # ── Connect signals ──────────────────────────────────────────────────
        self.scenario_dd.currentTextChanged.connect(self._on_scenario_change)
        self.theta_i.valueChanged.connect(self._compute)
        self.theta_e.valueChanged.connect(self._compute)

        # Initialise
        self._on_scenario_change()

    # ── widget creation ──────────────────────────────────────────────────────

    def _create_scenario_widgets(self) -> None:
        """Instantiate all scenario-specific widgets (hidden initially)."""

        # -- Scenario 1: Buitenlucht --
        self.bl_bouwdeel = QComboBox()
        self.bl_bouwdeel.addItems(list(_BUITENLUCHT_BD.keys()))
        self.bl_hs = _make_hs_combo()
        self.bl_heated = QCheckBox("Verwarmd vlak (wand-/vloerverwarming)")
        for w in (self.bl_bouwdeel, self.bl_hs, self.bl_heated):
            w.setVisible(False)

        # -- Scenario 2: Aangrenzend gebouw --
        self.ag_bouwdeel = QComboBox()
        self.ag_bouwdeel.addItems(["Wand", "Vloer", "Plafond"])
        self.ag_theta_b = _make_float(20, -50, 50, 0.5)
        self.ag_hs = _make_hs_combo()
        self.ag_heated = QCheckBox("Verwarmd vlak")
        for w in (self.ag_bouwdeel, self.ag_theta_b, self.ag_hs, self.ag_heated):
            w.setVisible(False)

        # -- Scenario 3: Verwarmde ruimte --
        self.vr_bouwdeel = QComboBox()
        self.vr_bouwdeel.addItems(["Wand", "Vloer", "Plafond"])
        self.vr_theta_a = QComboBox()
        for r in _ROOM_TYPES_WOON:
            self.vr_theta_a.addItem(
                f'{r["omschrijving"]} ({r["theta_i"]} °C)', r["theta_i"]
            )
        self.vr_override = QCheckBox("Temperatuur handmatig invoeren")
        self.vr_theta_manual = _make_float(20, -50, 50, 0.5)
        self.vr_hs_own = _make_hs_combo()
        self.vr_hs_adj = _make_hs_combo()
        self.vr_heated = QCheckBox("Verwarmd vlak")
        for w in (
            self.vr_bouwdeel, self.vr_theta_a, self.vr_override,
            self.vr_theta_manual, self.vr_hs_own, self.vr_hs_adj, self.vr_heated,
        ):
            w.setVisible(False)

        # -- Scenario 4a: Onverwarmd – bekende temperatuur --
        self.ob_bouwdeel = QComboBox()
        self.ob_bouwdeel.addItems(["Wand", "Vloer", "Plafond"])
        self.ob_theta_a = _make_float(5, -50, 50, 0.5)
        self.ob_hs = _make_hs_combo()
        self.ob_heated = QCheckBox("Verwarmd vlak")
        for w in (self.ob_bouwdeel, self.ob_theta_a, self.ob_hs, self.ob_heated):
            w.setVisible(False)

        # -- Scenario 4b: Onverwarmd – onbekende temperatuur --
        self.oo_doel = QComboBox()
        self.oo_doel.addItems(["Warmteverlies", "Tijdconstante"])
        self.oo_ruimte = QComboBox()
        self.oo_ruimte.addItems(list(_RUIMTE_MAP.keys()))
        self.oo_gevels = QComboBox()
        for label, n, door in _GEVEL_OPTIONS:
            self.oo_gevels.addItem(label, (n, door))
        self.oo_daktype = QComboBox()
        self.oo_daktype.addItems(list(_DAKTYPE_MAP.keys()))
        self.oo_buitenwanden = QCheckBox("Buitenwanden aanwezig")
        self.oo_buitenwanden.setChecked(True)
        self.oo_ventilatievoud = _make_float(0.3, 0, 50, 0.1)
        self.oo_a_opening = _make_float(0.003, 0, 1, 0.001, 3)
        self.oo_opening_mm2 = _make_float(800, 0, 10000, 50, 0)
        self.oo_tijdconst = QComboBox()
        self.oo_tijdconst.addItems(list(_TIJDCONST_MAP.keys()))
        for w in (
            self.oo_doel, self.oo_ruimte, self.oo_gevels, self.oo_daktype,
            self.oo_buitenwanden, self.oo_ventilatievoud, self.oo_a_opening,
            self.oo_opening_mm2, self.oo_tijdconst,
        ):
            w.setVisible(False)

        # -- Scenario 5: Grond --
        self.gr_bouwdeel = QComboBox()
        self.gr_bouwdeel.addItems(["Wand", "Vloer"])
        self.gr_theta_me = _make_float(10.5, -20, 30, 0.1)
        self.gr_hs = _make_hs_combo()
        self.gr_heated = QCheckBox("Verwarmd vlak op grond")
        self.gr_grondwater = QComboBox()
        self.gr_grondwater.addItems(["Nee", "Ja"])
        self.gr_gwdiepte = QComboBox()
        for label, val in _GW_OPTIONS:
            self.gr_gwdiepte.addItem(label, val)
        self.gr_rc = _make_float(3.5, 0.01, 20, 0.1)
        self.gr_area = _make_float(10, 0, 10000, 0.5)
        for w in (
            self.gr_bouwdeel, self.gr_theta_me, self.gr_hs, self.gr_heated,
            self.gr_grondwater, self.gr_gwdiepte, self.gr_rc, self.gr_area,
        ):
            w.setVisible(False)

        # Connect all value-changed signals to _compute
        self._connect_all_signals()

    def _connect_all_signals(self) -> None:
        """Wire every input widget to recompute on change."""
        combos = [
            self.bl_bouwdeel, self.bl_hs,
            self.ag_bouwdeel, self.ag_hs,
            self.vr_bouwdeel, self.vr_theta_a, self.vr_hs_own, self.vr_hs_adj,
            self.ob_bouwdeel, self.ob_hs,
            self.oo_doel, self.oo_ruimte, self.oo_gevels, self.oo_daktype,
            self.oo_tijdconst,
            self.gr_bouwdeel, self.gr_hs, self.gr_grondwater, self.gr_gwdiepte,
        ]
        for cb in combos:
            cb.currentIndexChanged.connect(self._compute)

        spins = [
            self.ag_theta_b, self.vr_theta_manual, self.ob_theta_a,
            self.oo_ventilatievoud, self.oo_a_opening, self.oo_opening_mm2,
            self.gr_theta_me, self.gr_rc, self.gr_area,
        ]
        for sb in spins:
            sb.valueChanged.connect(self._compute)

        checks = [
            self.bl_heated, self.ag_heated, self.vr_override, self.vr_heated,
            self.ob_heated, self.oo_buitenwanden, self.gr_heated,
        ]
        for ck in checks:
            ck.stateChanged.connect(self._compute)

        # Scenario 4b toggles visibility based on doel / ruimte
        self.oo_doel.currentTextChanged.connect(self._on_scenario_change)
        self.oo_ruimte.currentTextChanged.connect(self._on_scenario_change)
        self.gr_grondwater.currentTextChanged.connect(self._on_scenario_change)

    # ── scenario switching ───────────────────────────────────────────────────

    def _on_scenario_change(self, _=None) -> None:
        """Rebuild the dynamic fields panel for the selected scenario."""
        # Clear the layout
        while self.fields_layout.count():
            child = self.fields_layout.takeAt(0)
            if child.widget():
                child.widget().setVisible(False)
                child.widget().setParent(None)

        s = self.scenario_dd.currentText()

        # Show/hide shared temperature group
        show_temps = s != "Onverwarmde ruimte – onbekende temperatuur"
        self.temp_group.setVisible(show_temps)

        if s == "Buitenlucht":
            self._add_row("Bouwdeel:", self.bl_bouwdeel)
            self._add_widget(self.bl_heated)
            self._add_row("Verwarmingssysteem:", self.bl_hs)

        elif s == "Aangrenzend gebouw":
            self._add_row("Bouwdeel:", self.ag_bouwdeel)
            self._add_widget(self.ag_heated)
            self._add_row("Temperatuur aangrenzend [°C]:", self.ag_theta_b)
            self._add_row("Verwarmingssysteem:", self.ag_hs)

        elif s == "Verwarmde ruimte (zelfde woning)":
            self._add_row("Bouwdeel:", self.vr_bouwdeel)
            self._add_widget(self.vr_heated)
            self._add_row("Aangrenzende ruimte:", self.vr_theta_a)
            self._add_widget(self.vr_override)
            self._add_row("Handmatige temperatuur [°C]:", self.vr_theta_manual)
            self._add_row("Verw. eigen ruimte:", self.vr_hs_own)
            self._add_row("Verw. aangrenzende ruimte:", self.vr_hs_adj)

        elif s == "Onverwarmde ruimte – bekende temperatuur":
            self._add_row("Bouwdeel:", self.ob_bouwdeel)
            self._add_widget(self.ob_heated)
            self._add_row("Temperatuur onverwarmd [°C]:", self.ob_theta_a)
            self._add_row("Verwarmingssysteem:", self.ob_hs)

        elif s == "Onverwarmde ruimte – onbekende temperatuur":
            self._add_row("Doel:", self.oo_doel)
            if self.oo_doel.currentText() == "Warmteverlies":
                self._add_row("Type ruimte:", self.oo_ruimte)
                rt = self.oo_ruimte.currentText()
                if rt == "Vertrek":
                    self._add_row("Wat voor gevel:", self.oo_gevels)
                elif rt == "Ruimte onder dak":
                    self._add_row("Daktype:", self.oo_daktype)
                elif rt == "Verkeersruimte":
                    self._add_widget(self.oo_buitenwanden)
                    self._add_row("Ventilatievoud:", self.oo_ventilatievoud)
                    self._add_row("A_opening / V:", self.oo_a_opening)
                elif rt == "Kruipruimte":
                    self._add_row("Opening [mm²/m²]:", self.oo_opening_mm2)
            else:
                self._add_row("Type ruimte:", self.oo_tijdconst)

        elif s == "Grond":
            self._add_row("Bouwdeel:", self.gr_bouwdeel)
            self._add_widget(self.gr_heated)
            self._add_row("Jaarl. gem. buitentemp. [°C]:", self.gr_theta_me)
            self._add_row("Verwarmingssysteem:", self.gr_hs)
            self._add_row("Grondwater aanwezig:", self.gr_grondwater)
            if self.gr_grondwater.currentText() == "Ja":
                self._add_row("Grondwaterdiepte:", self.gr_gwdiepte)
            self._add_row("R_c [m²·K/W]:", self.gr_rc)
            self._add_row("Oppervlak A [m²]:", self.gr_area)

        self._compute()

    def _add_row(self, label: str, widget: QWidget) -> None:
        """Add a labelled widget row to the dynamic fields panel."""
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setMinimumWidth(220)
        row.addWidget(lbl)
        widget.setVisible(True)
        row.addWidget(widget, 1)
        wrapper = QWidget()
        wrapper.setLayout(row)
        self.fields_layout.addWidget(wrapper)

    def _add_widget(self, widget: QWidget) -> None:
        """Add a standalone widget (checkbox) to the dynamic fields panel."""
        widget.setVisible(True)
        self.fields_layout.addWidget(widget)

    # ── computation ──────────────────────────────────────────────────────────

    def _compute(self, _=None) -> None:
        """Run the appropriate fk_calc function and display results."""
        self.error_label.setText("")
        s = self.scenario_dd.currentText()

        try:
            rows: list[tuple[str, str]] = []

            if s == "Buitenlucht":
                bd = _BUITENLUCHT_BD[self.bl_bouwdeel.currentText()]
                hs_id = (
                    _HS_OPTIONS[self.bl_hs.currentText()]
                    if bd in ("vloer_boven_buitenlucht", "plat_dak")
                    else None
                )
                f = fk_calc.calc_f_k_buitenlucht(
                    bd,
                    self.theta_i.value(),
                    self.theta_e.value(),
                    hs_id,
                    self.bl_heated.isChecked(),
                )
                rows.append(("f_k", f"{f:.4f}"))

            elif s == "Aangrenzend gebouw":
                bd = self.ag_bouwdeel.currentText().lower()
                hs_id = (
                    _HS_OPTIONS[self.ag_hs.currentText()]
                    if bd in ("vloer", "plafond")
                    else None
                )
                f = fk_calc.calc_f_ia_k_aangrenzend_gebouw(
                    bd,
                    self.theta_i.value(),
                    self.theta_e.value(),
                    self.ag_theta_b.value(),
                    hs_id,
                    self.ag_heated.isChecked(),
                )
                rows.append(("f_ia,k", f"{f:.4f}"))

            elif s == "Verwarmde ruimte (zelfde woning)":
                bd = self.vr_bouwdeel.currentText().lower()
                theta_a = (
                    self.vr_theta_manual.value()
                    if self.vr_override.isChecked()
                    else self.vr_theta_a.currentData()
                )
                hs_own = (
                    _HS_OPTIONS[self.vr_hs_own.currentText()]
                    if bd != "wand"
                    else None
                )
                hs_adj = (
                    _HS_OPTIONS[self.vr_hs_adj.currentText()]
                    if bd != "wand"
                    else None
                )
                f = fk_calc.calc_f_ia_k_verwarmde_ruimte(
                    bd,
                    self.theta_i.value(),
                    self.theta_e.value(),
                    theta_a,
                    hs_own,
                    hs_adj,
                    self.vr_heated.isChecked(),
                )
                rows.append(("f_ia,k", f"{f:.4f}"))

            elif s == "Onverwarmde ruimte – bekende temperatuur":
                bd = self.ob_bouwdeel.currentText().lower()
                hs_id = (
                    _HS_OPTIONS[self.ob_hs.currentText()]
                    if bd in ("vloer", "plafond")
                    else None
                )
                f = fk_calc.calc_f_k_onverwarmd_bekend(
                    bd,
                    self.theta_i.value(),
                    self.theta_e.value(),
                    self.ob_theta_a.value(),
                    hs_id,
                    self.ob_heated.isChecked(),
                )
                rows.append(("f_k", f"{f:.4f}"))

            elif s == "Onverwarmde ruimte – onbekende temperatuur":
                if self.oo_doel.currentText() == "Warmteverlies":
                    rt = _RUIMTE_MAP[self.oo_ruimte.currentText()]
                    kwargs: dict = {}
                    if rt == "vertrek":
                        n_gevels, buitendeur = self.oo_gevels.currentData()
                        kwargs["aantal_externe_gevels"] = n_gevels
                        if buitendeur is not None:
                            kwargs["buitendeur_aanwezig"] = buitendeur
                    elif rt == "dak":
                        kwargs["daktype"] = _DAKTYPE_MAP[self.oo_daktype.currentText()]
                    elif rt == "verkeersruimte":
                        kwargs["heeft_buitenwanden"] = self.oo_buitenwanden.isChecked()
                        kwargs["ventilatievoud"] = self.oo_ventilatievoud.value()
                        kwargs["a_opening_per_v"] = self.oo_a_opening.value()
                    elif rt == "kruipruimte":
                        kwargs["openingsgrootte_mm2_per_m2"] = self.oo_opening_mm2.value()
                    f = fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(rt, **kwargs)
                    rows.append(("f_k (Tabel 2.3)", f"{f:.2f}"))
                else:
                    f = fk_calc.calc_f_k_onverwarmd_onbekend_tijdconstante(
                        _TIJDCONST_MAP[self.oo_tijdconst.currentText()]
                    )
                    rows.append(("f_k (Tabel 2.13)", f"{f:.2f}"))

            elif s == "Grond":
                bd = self.gr_bouwdeel.currentText().lower()
                hs_id = (
                    _HS_OPTIONS[self.gr_hs.currentText()]
                    if bd == "vloer"
                    else None
                )
                f_ig = fk_calc.calc_f_ig_k(
                    bd,
                    self.theta_i.value(),
                    self.theta_e.value(),
                    self.gr_theta_me.value(),
                    hs_id,
                    self.gr_heated.isChecked(),
                )
                if self.gr_grondwater.currentText() == "Nee":
                    f_gw = 1.00
                else:
                    f_gw = self.gr_gwdiepte.currentData()
                rows.append(("f_ig,k (formule)", f"{f_ig:.4f}"))
                rows.append(("f_gw", f"{f_gw:.2f}"))

            # Populate result table
            self.result_table.setRowCount(len(rows))
            for r_idx, (lbl, val) in enumerate(rows):
                self.result_table.setItem(r_idx, 0, QTableWidgetItem(lbl))
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.result_table.setItem(r_idx, 1, item)

        except Exception as exc:
            self.error_label.setText(f"⚠ {exc}")
            self.result_table.setRowCount(0)
