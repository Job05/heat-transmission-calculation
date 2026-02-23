"""fk_calc_tab.py – Tool 2: Correctiefactoren calculator.

Berekent correctiefactoren voor warmtetransmissieverlies op basis van
de aangrenzende situatie.  Dynamische invoervelden worden getoond/verborgen
afhankelijk van het gekozen scenario.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import fk_calc  # noqa: E402

_HEATING_SYSTEMS = fk_calc.list_heating_systems()
_HS_OPTIONS: dict[str, str] = {s["omschrijving"]: s["id"] for s in _HEATING_SYSTEMS}
_HS_LIST = list(_HS_OPTIONS.keys())

_ROOM_TYPES_WOON = fk_calc.list_room_types("woonfunctie")

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

SCENARIOS = [
    "Buitenlucht",
    "Aangrenzend gebouw",
    "Verwarmde ruimte (zelfde woning)",
    "Onverwarmde ruimte – bekende temperatuur",
    "Onverwarmde ruimte – onbekende temperatuur",
    "Grond",
]


def _make_hs_combo() -> QComboBox:
    """Maak een verwarmingssysteem keuzelijst."""
    cb = QComboBox()
    cb.addItems(_HS_LIST)
    cb.setMinimumWidth(300)
    return cb


def _make_float(value: float, lo: float, hi: float, step: float = 0.1, decimals: int = 1) -> QDoubleSpinBox:
    """Maak een ``QDoubleSpinBox`` met het opgegeven bereik en standaardwaarden."""
    sb = QDoubleSpinBox()
    sb.setRange(lo, hi)
    sb.setDecimals(decimals)
    sb.setSingleStep(step)
    sb.setValue(value)
    sb.setMinimumWidth(100)
    return sb


class FkCalcTab(QWidget):
    """Tweede tabblad – correctiefactoren calculator."""

    def __init__(self, config) -> None:
        super().__init__()
        self.config = config

        root = QVBoxLayout(self)

        # Scenariokeuze
        scenario_group = QGroupBox("Kies aangrenzende situatie")
        sg_layout = QHBoxLayout(scenario_group)
        sg_layout.addWidget(QLabel("Situatie:"))
        self.scenario_dd = QComboBox()
        self.scenario_dd.addItems(SCENARIOS)
        self.scenario_dd.setMinimumWidth(350)
        sg_layout.addWidget(self.scenario_dd, 1)
        root.addWidget(scenario_group)

        # Temperaturen
        temp_group = QGroupBox("Temperaturen")
        temp_layout = QHBoxLayout(temp_group)
        temp_layout.addWidget(QLabel("θ_i (binnen) [°C]:"))
        self.theta_i = _make_float(22, -50, 50, 0.1)
        temp_layout.addWidget(self.theta_i)
        temp_layout.addWidget(QLabel("θ_e (buiten) [°C]:"))
        self.theta_e = _make_float(-10, -50, 50, 0.1)
        temp_layout.addWidget(self.theta_e)
        temp_layout.addStretch()
        root.addWidget(temp_group)
        self.temp_group = temp_group

        # Dynamische invoervelden
        self.fields_group = QGroupBox("Invoervelden")
        self.fields_layout = QVBoxLayout(self.fields_group)
        root.addWidget(self.fields_group)

        # Resultaat
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
        self.error_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        self.error_label.setWordWrap(True)
        res_layout.addWidget(self.error_label)
        root.addWidget(res_group)

        # Opslaan / Laden knoppen
        io_row = QHBoxLayout()
        save_btn = QPushButton("💾 Opslaan")
        save_btn.setProperty("secondary", True)
        save_btn.clicked.connect(self._save_to_file)
        io_row.addWidget(save_btn)
        load_btn = QPushButton("📂 Laden")
        load_btn.setProperty("secondary", True)
        load_btn.clicked.connect(self._load_from_file)
        io_row.addWidget(load_btn)
        io_row.addStretch()
        root.addLayout(io_row)

        # Scenariospecifieke widgets aanmaken
        self._create_scenario_widgets()

        # Signalen
        self.scenario_dd.currentTextChanged.connect(self._on_scenario_change)
        self.theta_i.valueChanged.connect(self._compute)
        self.theta_e.valueChanged.connect(self._compute)

        self._on_scenario_change()

    def _create_scenario_widgets(self) -> None:
        """Maak alle scenariospecifieke widgets aan (aanvankelijk verborgen)."""

        # Scenario 1: Buitenlucht
        self.bl_bouwdeel = QComboBox()
        self.bl_bouwdeel.addItems(list(_BUITENLUCHT_BD.keys()))
        self.bl_bouwdeel.setMinimumWidth(250)
        self.bl_hs = _make_hs_combo()
        self.bl_heated = QCheckBox("Verwarmd vlak (wand-/vloerverwarming)")
        for w in (self.bl_bouwdeel, self.bl_hs, self.bl_heated):
            w.setVisible(False)

        # Scenario 2: Aangrenzend gebouw
        self.ag_bouwdeel = QComboBox()
        self.ag_bouwdeel.addItems(["Wand", "Vloer", "Plafond"])
        self.ag_bouwdeel.setMinimumWidth(150)
        self.ag_theta_b = _make_float(20, -50, 50, 0.1)
        self.ag_hs = _make_hs_combo()
        self.ag_heated = QCheckBox("Verwarmd vlak")
        for w in (self.ag_bouwdeel, self.ag_theta_b, self.ag_hs, self.ag_heated):
            w.setVisible(False)

        # Scenario 3: Verwarmde ruimte
        self.vr_bouwdeel = QComboBox()
        self.vr_bouwdeel.addItems(["Wand", "Vloer", "Plafond"])
        self.vr_bouwdeel.setMinimumWidth(150)
        self.vr_theta_a = QComboBox()
        self.vr_theta_a.setMinimumWidth(300)
        for r in _ROOM_TYPES_WOON:
            self.vr_theta_a.addItem(
                f'{r["omschrijving"]} ({r["theta_i"]} °C)', r["theta_i"]
            )
        self.vr_override = QCheckBox("Temperatuur handmatig invoeren")
        self.vr_theta_manual = _make_float(20, -50, 50, 0.1)
        self.vr_hs_own = _make_hs_combo()
        self.vr_hs_adj = _make_hs_combo()
        self.vr_heated = QCheckBox("Verwarmd vlak")
        for w in (
            self.vr_bouwdeel, self.vr_theta_a, self.vr_override,
            self.vr_theta_manual, self.vr_hs_own, self.vr_hs_adj, self.vr_heated,
        ):
            w.setVisible(False)

        # Scenario 4a: Onverwarmd – bekende temperatuur
        self.ob_bouwdeel = QComboBox()
        self.ob_bouwdeel.addItems(["Wand", "Vloer", "Plafond"])
        self.ob_bouwdeel.setMinimumWidth(150)
        self.ob_theta_a = _make_float(5, -50, 50, 0.1)
        self.ob_hs = _make_hs_combo()
        self.ob_heated = QCheckBox("Verwarmd vlak")
        for w in (self.ob_bouwdeel, self.ob_theta_a, self.ob_hs, self.ob_heated):
            w.setVisible(False)

        # Scenario 4b: Onverwarmd – onbekende temperatuur
        self.oo_doel = QComboBox()
        self.oo_doel.addItems(["Warmteverlies", "Tijdconstante"])
        self.oo_doel.setMinimumWidth(200)
        self.oo_ruimte = QComboBox()
        self.oo_ruimte.addItems(list(_RUIMTE_MAP.keys()))
        self.oo_ruimte.setMinimumWidth(200)
        self.oo_gevels = QComboBox()
        self.oo_gevels.setMinimumWidth(400)
        for label, n, door in _GEVEL_OPTIONS:
            self.oo_gevels.addItem(label, (n, door))
        self.oo_daktype = QComboBox()
        self.oo_daktype.addItems(list(_DAKTYPE_MAP.keys()))
        self.oo_daktype.setMinimumWidth(350)
        self.oo_buitenwanden = QCheckBox("Buitenwanden aanwezig")
        self.oo_buitenwanden.setChecked(True)
        self.oo_ventilatievoud = _make_float(0.3, 0, 50, 0.1)
        self.oo_a_opening = _make_float(0.003, 0, 1, 0.1, 3)
        self.oo_opening_mm2 = _make_float(800, 0, 10000, 0.1, 0)
        self.oo_tijdconst = QComboBox()
        self.oo_tijdconst.addItems(list(_TIJDCONST_MAP.keys()))
        self.oo_tijdconst.setMinimumWidth(300)
        for w in (
            self.oo_doel, self.oo_ruimte, self.oo_gevels, self.oo_daktype,
            self.oo_buitenwanden, self.oo_ventilatievoud, self.oo_a_opening,
            self.oo_opening_mm2, self.oo_tijdconst,
        ):
            w.setVisible(False)

        # Scenario 5: Grond
        self.gr_bouwdeel = QComboBox()
        self.gr_bouwdeel.addItems(["Wand", "Vloer"])
        self.gr_bouwdeel.setMinimumWidth(150)
        self.gr_theta_me = _make_float(10.5, -20, 30, 0.1)
        self.gr_hs = _make_hs_combo()
        self.gr_heated = QCheckBox("Verwarmd vlak op grond")
        self.gr_grondwater = QComboBox()
        self.gr_grondwater.addItems(["Nee", "Ja"])
        self.gr_grondwater.setMinimumWidth(100)
        self.gr_gwdiepte = QComboBox()
        self.gr_gwdiepte.setMinimumWidth(400)
        for label, val in _GW_OPTIONS:
            self.gr_gwdiepte.addItem(label, val)
        self.gr_rc = _make_float(3.5, 0.01, 20, 0.1)
        self.gr_area = _make_float(10, 0, 10000, 0.1)
        for w in (
            self.gr_bouwdeel, self.gr_theta_me, self.gr_hs, self.gr_heated,
            self.gr_grondwater, self.gr_gwdiepte, self.gr_rc, self.gr_area,
        ):
            w.setVisible(False)

        self._connect_all_signals()

    def _connect_all_signals(self) -> None:
        """Koppel alle invoerwidgets aan herberekening."""
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

        self.oo_doel.currentTextChanged.connect(self._on_scenario_change)
        self.oo_ruimte.currentTextChanged.connect(self._on_scenario_change)
        self.gr_grondwater.currentTextChanged.connect(self._on_scenario_change)

    def _on_scenario_change(self, _=None) -> None:
        """Bouw het dynamische veldenpaneel opnieuw op."""
        while self.fields_layout.count():
            child = self.fields_layout.takeAt(0)
            if child.widget():
                child.widget().setVisible(False)
                child.widget().setParent(None)

        s = self.scenario_dd.currentText()

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
        """Voeg een gelabelde widgetrij toe aan het dynamische veld."""
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setMinimumWidth(240)
        row.addWidget(lbl)
        widget.setVisible(True)
        row.addWidget(widget, 1)
        wrapper = QWidget()
        wrapper.setLayout(row)
        self.fields_layout.addWidget(wrapper)

    def _add_widget(self, widget: QWidget) -> None:
        """Voeg een losstaand widget (checkbox) toe aan het dynamische veld."""
        widget.setVisible(True)
        self.fields_layout.addWidget(widget)

    def _compute(self, _=None) -> None:
        """Voer de juiste fk_calc-functie uit en toon de resultaten."""
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

            self.result_table.setRowCount(len(rows))
            for r_idx, (lbl, val) in enumerate(rows):
                self.result_table.setItem(r_idx, 0, QTableWidgetItem(lbl))
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.result_table.setItem(r_idx, 1, item)

        except Exception as exc:
            self.error_label.setText(f"⚠ {exc}")
            self.result_table.setRowCount(0)

    # ── Opslaan / Laden ──────────────────────────────────────────────────────

    def _get_state(self) -> dict:
        """Verzamel de huidige invoerstatus als dict."""
        return {
            "scenario": self.scenario_dd.currentText(),
            "theta_i": self.theta_i.value(),
            "theta_e": self.theta_e.value(),
            "bl_bouwdeel": self.bl_bouwdeel.currentText(),
            "bl_hs": self.bl_hs.currentText(),
            "bl_heated": self.bl_heated.isChecked(),
            "ag_bouwdeel": self.ag_bouwdeel.currentText(),
            "ag_theta_b": self.ag_theta_b.value(),
            "ag_hs": self.ag_hs.currentText(),
            "ag_heated": self.ag_heated.isChecked(),
            "vr_bouwdeel": self.vr_bouwdeel.currentText(),
            "vr_theta_a_idx": self.vr_theta_a.currentIndex(),
            "vr_override": self.vr_override.isChecked(),
            "vr_theta_manual": self.vr_theta_manual.value(),
            "vr_hs_own": self.vr_hs_own.currentText(),
            "vr_hs_adj": self.vr_hs_adj.currentText(),
            "vr_heated": self.vr_heated.isChecked(),
            "ob_bouwdeel": self.ob_bouwdeel.currentText(),
            "ob_theta_a": self.ob_theta_a.value(),
            "ob_hs": self.ob_hs.currentText(),
            "ob_heated": self.ob_heated.isChecked(),
            "oo_doel": self.oo_doel.currentText(),
            "oo_ruimte": self.oo_ruimte.currentText(),
            "oo_gevels_idx": self.oo_gevels.currentIndex(),
            "oo_daktype": self.oo_daktype.currentText(),
            "oo_buitenwanden": self.oo_buitenwanden.isChecked(),
            "oo_ventilatievoud": self.oo_ventilatievoud.value(),
            "oo_a_opening": self.oo_a_opening.value(),
            "oo_opening_mm2": self.oo_opening_mm2.value(),
            "oo_tijdconst": self.oo_tijdconst.currentText(),
            "gr_bouwdeel": self.gr_bouwdeel.currentText(),
            "gr_theta_me": self.gr_theta_me.value(),
            "gr_hs": self.gr_hs.currentText(),
            "gr_heated": self.gr_heated.isChecked(),
            "gr_grondwater": self.gr_grondwater.currentText(),
            "gr_gwdiepte_idx": self.gr_gwdiepte.currentIndex(),
            "gr_rc": self.gr_rc.value(),
            "gr_area": self.gr_area.value(),
        }

    def _set_state(self, d: dict) -> None:
        """Herstel invoerstatus vanuit een dict."""
        def _set_combo(cb: QComboBox, key: str) -> None:
            if key in d:
                idx = cb.findText(d[key])
                if idx >= 0:
                    cb.setCurrentIndex(idx)

        def _set_combo_idx(cb: QComboBox, key: str) -> None:
            if key in d and 0 <= d[key] < cb.count():
                cb.setCurrentIndex(d[key])

        def _set_spin(sb: QDoubleSpinBox, key: str) -> None:
            if key in d:
                sb.setValue(d[key])

        def _set_check(ck: QCheckBox, key: str) -> None:
            if key in d:
                ck.setChecked(d[key])

        _set_combo(self.scenario_dd, "scenario")
        _set_spin(self.theta_i, "theta_i")
        _set_spin(self.theta_e, "theta_e")

        _set_combo(self.bl_bouwdeel, "bl_bouwdeel")
        _set_combo(self.bl_hs, "bl_hs")
        _set_check(self.bl_heated, "bl_heated")

        _set_combo(self.ag_bouwdeel, "ag_bouwdeel")
        _set_spin(self.ag_theta_b, "ag_theta_b")
        _set_combo(self.ag_hs, "ag_hs")
        _set_check(self.ag_heated, "ag_heated")

        _set_combo(self.vr_bouwdeel, "vr_bouwdeel")
        _set_combo_idx(self.vr_theta_a, "vr_theta_a_idx")
        _set_check(self.vr_override, "vr_override")
        _set_spin(self.vr_theta_manual, "vr_theta_manual")
        _set_combo(self.vr_hs_own, "vr_hs_own")
        _set_combo(self.vr_hs_adj, "vr_hs_adj")
        _set_check(self.vr_heated, "vr_heated")

        _set_combo(self.ob_bouwdeel, "ob_bouwdeel")
        _set_spin(self.ob_theta_a, "ob_theta_a")
        _set_combo(self.ob_hs, "ob_hs")
        _set_check(self.ob_heated, "ob_heated")

        _set_combo(self.oo_doel, "oo_doel")
        _set_combo(self.oo_ruimte, "oo_ruimte")
        _set_combo_idx(self.oo_gevels, "oo_gevels_idx")
        _set_combo(self.oo_daktype, "oo_daktype")
        _set_check(self.oo_buitenwanden, "oo_buitenwanden")
        _set_spin(self.oo_ventilatievoud, "oo_ventilatievoud")
        _set_spin(self.oo_a_opening, "oo_a_opening")
        _set_spin(self.oo_opening_mm2, "oo_opening_mm2")
        _set_combo(self.oo_tijdconst, "oo_tijdconst")

        _set_combo(self.gr_bouwdeel, "gr_bouwdeel")
        _set_spin(self.gr_theta_me, "gr_theta_me")
        _set_combo(self.gr_hs, "gr_hs")
        _set_check(self.gr_heated, "gr_heated")
        _set_combo(self.gr_grondwater, "gr_grondwater")
        _set_combo_idx(self.gr_gwdiepte, "gr_gwdiepte_idx")
        _set_spin(self.gr_rc, "gr_rc")
        _set_spin(self.gr_area, "gr_area")

        self._on_scenario_change()

    def _save_to_file(self) -> None:
        """Sla de huidige invoer op naar een bestand."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Configuratie opslaan", "",
            "Correctiefactoren configuratie (*.cfr)"
        )
        if not path:
            return
        if not path.endswith(".cfr"):
            path += ".cfr"
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self._get_state(), fh, indent=2, ensure_ascii=False)

    def _load_from_file(self) -> None:
        """Laad invoer uit een bestand."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Configuratie laden", "",
            "Correctiefactoren configuratie (*.cfr)"
        )
        if not path:
            return
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self._set_state(data)
