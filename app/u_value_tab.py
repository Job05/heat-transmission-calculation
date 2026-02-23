"""u_value_tab.py – Tool 1: U-value / heat-transmission calculator.

Replicates the interactive layer-based U-value form from the Jupyter
notebook, using PyQt5 widgets instead of ipywidgets.

Each construction layer lets the user either pick a material from the
JSON database or enter a manual R-value.  The result table updates live.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Callable, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# ── Import pure helpers from heat_calc ───────────────────────────────────────
# heat_calc.py sits in the repo root; add it to the path so we can import.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from heat_calc import (  # noqa: E402
    U_VALUE_CATS,
    R_VALUE_CATS,
    SURFACE_R,
    scalar,
    sub_keys,
    third_keys,
    raw_value,
)

# ── Load material database ───────────────────────────────────────────────────
_MATERIALS_PATH = os.path.join(_REPO_ROOT, "material_properties.json")
with open(_MATERIALS_PATH, "r", encoding="utf-8") as _fh:
    _MATERIALS: dict = json.load(_fh)


# ── Single-layer widget ─────────────────────────────────────────────────────


class LayerRow(QFrame):
    """A single construction layer with material selectors or manual R input."""

    def __init__(
        self,
        materials: dict,
        on_change: Callable[[], None],
        on_remove: Callable[["LayerRow"], None],
    ) -> None:
        super().__init__()
        self.materials = materials
        self._on_change = on_change
        self._on_remove = on_remove

        self.setFrameShape(QFrame.StyledPanel)
        self.setLineWidth(1)
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 6, 8, 6)

        # ── Row 1: mode toggle + remove button ──────────────────────────────
        row1 = QHBoxLayout()
        self.mode_cb = QComboBox()
        self.mode_cb.addItems(["Materiaallijst", "Handmatige R"])
        row1.addWidget(QLabel("Invoermodus:"))
        row1.addWidget(self.mode_cb)
        row1.addStretch()
        self.remove_btn = QPushButton("✕ Verwijder")
        self.remove_btn.setProperty("danger", True)
        row1.addWidget(self.remove_btn)
        root.addLayout(row1)

        # ── Material selection widgets ───────────────────────────────────────
        self.mat_box = QWidget()
        mat_layout = QVBoxLayout(self.mat_box)
        mat_layout.setContentsMargins(0, 4, 0, 0)

        sel_row = QHBoxLayout()
        self.cat_dd = QComboBox()
        self.cat_dd.addItems(list(materials.keys()))
        sel_row.addWidget(QLabel("Categorie:"))
        sel_row.addWidget(self.cat_dd)

        self.sub_dd = QComboBox()
        sel_row.addWidget(QLabel("Materiaal:"))
        sel_row.addWidget(self.sub_dd)

        self.third_dd = QComboBox()
        self.third_lbl = QLabel("Subtype:")
        sel_row.addWidget(self.third_lbl)
        sel_row.addWidget(self.third_dd)
        mat_layout.addLayout(sel_row)

        dim_row = QHBoxLayout()
        self.thickness = QDoubleSpinBox()
        self.thickness.setRange(0.0, 10.0)
        self.thickness.setDecimals(3)
        self.thickness.setSingleStep(0.001)
        self.thickness.setValue(0.100)
        dim_row.addWidget(QLabel("Dikte d [m]:"))
        dim_row.addWidget(self.thickness)
        self.lam_lbl = QLabel("")
        dim_row.addWidget(self.lam_lbl)
        dim_row.addStretch()
        mat_layout.addLayout(dim_row)

        root.addWidget(self.mat_box)

        # ── Manual R widget ──────────────────────────────────────────────────
        self.man_box = QWidget()
        man_layout = QHBoxLayout(self.man_box)
        man_layout.setContentsMargins(0, 4, 0, 0)
        self.manual_r = QDoubleSpinBox()
        self.manual_r.setRange(0.0, 100.0)
        self.manual_r.setDecimals(3)
        self.manual_r.setSingleStep(0.01)
        self.manual_r.setValue(0.100)
        man_layout.addWidget(QLabel("R [m²·K/W]:"))
        man_layout.addWidget(self.manual_r)
        man_layout.addStretch()
        root.addWidget(self.man_box)
        self.man_box.setVisible(False)

        # ── R feedback label ─────────────────────────────────────────────────
        self.r_lbl = QLabel("")
        root.addWidget(self.r_lbl)

        # ── Wire signals ─────────────────────────────────────────────────────
        self.mode_cb.currentTextChanged.connect(self._on_mode)
        self.cat_dd.currentTextChanged.connect(self._on_cat)
        self.sub_dd.currentTextChanged.connect(self._on_sub)
        self.third_dd.currentTextChanged.connect(self._recalc)
        self.thickness.valueChanged.connect(self._recalc)
        self.manual_r.valueChanged.connect(self._recalc)
        self.remove_btn.clicked.connect(lambda: self._on_remove(self))

        self._refresh_sub()
        self._refresh_third()
        self._recalc()

    # ── private ──────────────────────────────────────────────────────────────

    def _on_mode(self) -> None:
        is_mat = self.mode_cb.currentText() == "Materiaallijst"
        self.mat_box.setVisible(is_mat)
        self.man_box.setVisible(not is_mat)
        self._recalc()

    def _on_cat(self) -> None:
        self._refresh_sub()
        self._refresh_third()
        self._recalc()

    def _on_sub(self) -> None:
        self._refresh_third()
        self._recalc()

    def _refresh_sub(self) -> None:
        self.sub_dd.blockSignals(True)
        self.sub_dd.clear()
        opts = sub_keys(self.materials, self.cat_dd.currentText())
        self.sub_dd.addItems(opts if opts else ["—"])
        self.sub_dd.blockSignals(False)

    def _refresh_third(self) -> None:
        self.third_dd.blockSignals(True)
        self.third_dd.clear()
        sub = self.sub_dd.currentText() if self.sub_dd.count() else ""
        opts = third_keys(self.materials, self.cat_dd.currentText(), sub)
        if opts:
            self.third_dd.addItems(opts)
            self.third_dd.setVisible(True)
            self.third_lbl.setVisible(True)
        else:
            self.third_dd.addItems(["—"])
            self.third_dd.setVisible(False)
            self.third_lbl.setVisible(False)
        self.third_dd.blockSignals(False)

    def _recalc(self) -> None:
        r = self.get_r()
        if r is not None:
            self.r_lbl.setText(f"  → R = {r:.3f} m²·K/W")
            self.r_lbl.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        else:
            self.r_lbl.setText("  → R kan niet worden bepaald")
            self.r_lbl.setStyleSheet("color: #f38ba8; font-weight: bold;")

        # λ hint
        cat = self.cat_dd.currentText()
        if (
            self.mode_cb.currentText() != "Materiaallijst"
            or cat in U_VALUE_CATS
            or cat in R_VALUE_CATS
        ):
            self.lam_lbl.setText("")
        else:
            third = (
                self.third_dd.currentText()
                if self.third_dd.isVisible()
                else None
            )
            val = raw_value(self.materials, cat, self.sub_dd.currentText(), third)
            if isinstance(val, list):
                self.lam_lbl.setText(
                    f"  λ = {val[0]} – {val[1]} W/(m·K)"
                    f"  (laagste waarde {min(val):.4f} gebruikt)"
                )
            elif isinstance(val, (int, float)):
                self.lam_lbl.setText(f"  λ = {val} W/(m·K)")
            else:
                self.lam_lbl.setText("")

        self._on_change()

    # ── public ───────────────────────────────────────────────────────────────

    def get_r(self) -> Optional[float]:
        """Compute thermal resistance [m²·K/W] for this layer."""
        if self.mode_cb.currentText() == "Handmatige R":
            return self.manual_r.value()

        cat = self.cat_dd.currentText()
        sub = self.sub_dd.currentText()
        third = (
            self.third_dd.currentText() if self.third_dd.isVisible() else None
        )
        val = raw_value(self.materials, cat, sub, third)

        if cat in U_VALUE_CATS:
            u = scalar(val)
            return (1.0 / u) if u else None

        if cat in R_VALUE_CATS:
            return scalar(val)

        lam = scalar(val)
        d = self.thickness.value()
        return (d / lam) if (lam and lam > 0 and d > 0) else None

    def row_info(self) -> dict:
        """Return a dict with display info for the result table row."""
        cat = self.cat_dd.currentText()
        sub = self.sub_dd.currentText()
        third = (
            self.third_dd.currentText() if self.third_dd.isVisible() else None
        )
        r = self.get_r()

        if self.mode_cb.currentText() == "Handmatige R":
            return {"naam": "Handmatig", "d": None, "lam": "—", "R": r}

        val = raw_value(self.materials, cat, sub, third)
        label = f"{cat} / {sub}" + (f" / {third}" if third else "")

        if cat in U_VALUE_CATS:
            u = scalar(val)
            return {"naam": label, "d": None, "lam": f"(U={u:.2f})", "R": r}
        if cat in R_VALUE_CATS:
            return {"naam": label, "d": None, "lam": "(R-waarde)", "R": r}

        lam = scalar(val)
        return {
            "naam": label,
            "d": self.thickness.value(),
            "lam": f"{lam:.4f}" if lam else "—",
            "R": r,
        }


# ── Tab widget ───────────────────────────────────────────────────────────────


class UValueTab(QWidget):
    """First tool tab – U-value calculator with dynamic construction layers."""

    def __init__(self, config) -> None:
        super().__init__()
        self.config = config
        self.layers: list[LayerRow] = []

        root = QVBoxLayout(self)

        # ── Surface resistances ──────────────────────────────────────────────
        sr_group = QGroupBox("Overgangsweerstanden")
        sr_layout = QHBoxLayout(sr_group)

        sr_layout.addWidget(QLabel("Ri (binnen):"))
        self.ri_dd = QComboBox()
        self.ri_dd.addItems(list(SURFACE_R.keys()))
        self.ri_dd.setCurrentIndex(0)
        sr_layout.addWidget(self.ri_dd)

        sr_layout.addWidget(QLabel("Re (buiten):"))
        self.re_dd = QComboBox()
        self.re_dd.addItems(list(SURFACE_R.keys()))
        self.re_dd.setCurrentIndex(1)
        sr_layout.addWidget(self.re_dd)
        sr_layout.addStretch()
        root.addWidget(sr_group)

        # ── Construction layers (scrollable) ─────────────────────────────────
        layers_group = QGroupBox("Constructielagen (Rc)")
        layers_outer = QVBoxLayout(layers_group)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.layers_layout = QVBoxLayout(self.scroll_content)
        self.layers_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        layers_outer.addWidget(self.scroll)

        add_btn = QPushButton("＋ Voeg laag toe")
        add_btn.clicked.connect(self._add_layer)
        layers_outer.addWidget(add_btn)
        root.addWidget(layers_group)

        # ── Result table ─────────────────────────────────────────────────────
        res_group = QGroupBox("Resultaat")
        res_layout = QVBoxLayout(res_group)
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(
            ["Materiaal / Laag", "d [m]", "λ [W/(m·K)]", "R = d/λ [m²·K/W]", "Ri & Re [m²·K/W]"]
        )
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for col in range(1, 5):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        res_layout.addWidget(self.result_table)

        self.u_label = QLabel("")
        self.u_label.setAlignment(Qt.AlignCenter)
        self.u_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        res_layout.addWidget(self.u_label)
        root.addWidget(res_group)

        # Wire surface-resistance dropdowns
        self.ri_dd.currentTextChanged.connect(lambda _: self._refresh())
        self.re_dd.currentTextChanged.connect(lambda _: self._refresh())

        # Start with one empty layer
        self._add_layer()

    # ── layer management ─────────────────────────────────────────────────────

    def _add_layer(self) -> None:
        layer = LayerRow(_MATERIALS, self._refresh, self._remove_layer)
        self.layers.append(layer)
        self.layers_layout.addWidget(layer)
        self._refresh()

    def _remove_layer(self, layer: LayerRow) -> None:
        self.layers.remove(layer)
        self.layers_layout.removeWidget(layer)
        layer.deleteLater()
        self._refresh()

    # ── result table refresh ─────────────────────────────────────────────────

    def _refresh(self) -> None:
        ri = SURFACE_R[self.ri_dd.currentText()]
        re = SURFACE_R[self.re_dd.currentText()]

        # Build rows
        rows: list[list[str]] = []
        total_d = 0.0
        total_rc = 0.0

        # Inner surface
        rows.append(["lucht (binnen)", "—", "—", "—", f"{ri:.2f}"])

        for layer in self.layers:
            info = layer.row_info()
            r = info["R"]
            d = info["d"]
            d_str = f"{d:.3f}" if isinstance(d, float) else "—"
            r_str = f"{r:.3f}" if r is not None else "?"
            if isinstance(d, float):
                total_d += d
            if r is not None:
                total_rc += r
            rows.append([info["naam"], d_str, str(info["lam"]), r_str, "—"])

        # Outer surface
        rows.append(["lucht (buiten)", "—", "—", "—", f"{re:.2f}"])

        # Totals
        total_r = ri + total_rc + re
        u = 1.0 / total_r if total_r > 0 else None
        u_str = f"{u:.3f}" if u is not None else "?"
        d_tot = f"{total_d:.3f}" if total_d > 0 else "—"
        rows.append(["TOTAAL", d_tot, "—", f"{total_rc:.3f}", f"{ri + re:.2f}"])

        # Populate table
        self.result_table.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.result_table.setItem(r_idx, c_idx, item)

        # U-value summary
        self.u_label.setText(
            f"U = 1 / (Ri {ri:.2f} + Rc {total_rc:.3f} + Re {re:.2f})"
            f"  =  {u_str} W/(m²·K)"
        )
