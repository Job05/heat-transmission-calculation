"""fk_calc.py – Correction-factor calculator for heat-transmission losses.

Implements the decision process and formulas from fk_berekening.md:

  f_k      – exterior air or unheated space
  f_ia,k   – adjacent building or heated space (same dwelling)
  f_ig,k   – ground contact (with groundwater factor f_gw)

All reference data is loaded from the JSON files in the ``tables/`` folder.
"""

from __future__ import annotations

import json
import os
from typing import Optional

# ── Table loading ─────────────────────────────────────────────────────────────

_TABLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tables")


def _load_json(filename: str) -> dict:
    with open(os.path.join(_TABLES_DIR, filename), "r", encoding="utf-8") as fh:
        return json.load(fh)


_tabel_2_12: dict = _load_json("tabel_2_12.json")
_tabel_2_13: dict = _load_json("tabel_2_13.json")
_tabel_2_3: dict = _load_json("tabel_2_3.json")
_tabel_binnentemperaturen: dict = _load_json("tabel_binnentemperaturen.json")
_tabel_f_gw: dict = _load_json("tabel_f_gw.json")
_tabel_u_equiv_k: dict = _load_json("tabel_u_equiv_k.json")

# ── Constants ─────────────────────────────────────────────────────────────────

DEFAULT_THETA_E: float = _tabel_binnentemperaturen["standaard_nl"]["theta_e_C"]
DEFAULT_THETA_ME: float = _tabel_binnentemperaturen["standaard_nl"]["theta_me_C"]

# ── Helper: heating-system delta-theta lookup ─────────────────────────────────


def list_heating_systems() -> list[dict]:
    """Return a flat list of all heating systems with id, description, Δθ₁, Δθ₂."""
    systems: list[dict] = []
    for cat in _tabel_2_12["categorieen"]:
        for s in cat["systemen"]:
            systems.append(
                {
                    "id": s["id"],
                    "omschrijving": s["omschrijving"],
                    "delta_theta_1": s["delta_theta_1_K"],
                    "delta_theta_2": s["delta_theta_2_K"],
                }
            )
    return systems


def get_delta_theta(heating_system_id: str) -> tuple[float, float]:
    """Return ``(Δθ₁, Δθ₂)`` for a given heating-system *id*.

    Raises ``ValueError`` when the id is not found.
    """
    for cat in _tabel_2_12["categorieen"]:
        for s in cat["systemen"]:
            if s["id"] == heating_system_id:
                return (s["delta_theta_1_K"], s["delta_theta_2_K"])
    raise ValueError(f"Unknown heating system id: {heating_system_id!r}")


# ── Helper: indoor design-temperature lookup ──────────────────────────────────


def list_room_types(
    building_type: str = "woonfunctie",
) -> list[dict]:
    """Return the room-type entries for a building category."""
    data = _tabel_binnentemperaturen.get(building_type, [])
    return [{"id": r["id"], "omschrijving": r["omschrijving"], "theta_i": r["theta_i_C"]} for r in data]


def get_theta_i(room_type_id: str, building_type: str = "woonfunctie") -> float:
    """Return θ_i for a *room_type_id* in the given *building_type*.

    Raises ``ValueError`` when the id is not found.
    """
    for r in _tabel_binnentemperaturen.get(building_type, []):
        if r["id"] == room_type_id:
            return float(r["theta_i_C"])
    raise ValueError(
        f"Unknown room type {room_type_id!r} in building type {building_type!r}"
    )


# ── Scenario 1: Buitenlucht ──────────────────────────────────────────────────


def calc_f_k_buitenlucht(
    bouwdeel: str,
    theta_i: float,
    theta_e: float = DEFAULT_THETA_E,
    heating_system_id: Optional[str] = None,
    is_heated_surface: bool = False,
) -> float:
    """Calculate *f_k* for an exterior-air boundary.

    Parameters
    ----------
    bouwdeel :
        ``"buitenwand"``, ``"schuin_dak"``, ``"vloer_boven_buitenlucht"``, or
        ``"plat_dak"``.
    theta_i : design indoor temperature [°C].
    theta_e : design outdoor temperature [°C].
    heating_system_id :
        Required when *bouwdeel* is ``"vloer_boven_buitenlucht"`` or
        ``"plat_dak"`` (used to look up Δθ).
    is_heated_surface :
        If ``True`` the surface is a heated panel → f_k = 0.
    """
    if is_heated_surface:
        return 0.0

    bouwdeel = bouwdeel.lower()
    if bouwdeel in ("buitenwand", "schuin_dak"):
        return 1.0

    if theta_i == theta_e:
        raise ValueError("theta_i must not equal theta_e")

    if heating_system_id is None:
        raise ValueError(
            "heating_system_id is required for vloer_boven_buitenlucht and plat_dak"
        )

    d1, d2 = get_delta_theta(heating_system_id)

    if bouwdeel == "vloer_boven_buitenlucht":
        # Formula 2.7
        return ((theta_i + d2) - theta_e) / (theta_i - theta_e)
    if bouwdeel == "plat_dak":
        # Formula 2.8
        return ((theta_i + d1) - theta_e) / (theta_i - theta_e)

    raise ValueError(f"Unknown bouwdeel for buitenlucht: {bouwdeel!r}")


# ── Scenario 2: Aangrenzend gebouw ────────────────────────────────────────────


def calc_f_ia_k_aangrenzend_gebouw(
    bouwdeel: str,
    theta_i: float,
    theta_e: float,
    theta_b: float,
    heating_system_id: Optional[str] = None,
    is_heated_surface: bool = False,
) -> float:
    """Calculate *f_ia,k* for an adjacent-building boundary.

    Parameters
    ----------
    bouwdeel : ``"wand"``, ``"vloer"``, or ``"plafond"``.
    theta_b : temperature in the adjacent building [°C].
    """
    if is_heated_surface:
        return 0.0

    if theta_i == theta_e:
        raise ValueError("theta_i must not equal theta_e")

    bouwdeel = bouwdeel.lower()
    d1, d2 = 0.0, 0.0
    if bouwdeel in ("vloer", "plafond"):
        if heating_system_id is None:
            raise ValueError(
                "heating_system_id is required for vloer and plafond"
            )
        d1, d2 = get_delta_theta(heating_system_id)

    if bouwdeel == "wand":
        # Formula 2.11
        return (theta_i - theta_b) / (theta_i - theta_e)
    if bouwdeel == "vloer":
        # Formula 2.12
        return ((theta_i + d2) - theta_b) / (theta_i - theta_e)
    if bouwdeel == "plafond":
        # Formula 2.13
        return ((theta_i + d1) - theta_b) / (theta_i - theta_e)

    raise ValueError(f"Unknown bouwdeel for aangrenzend gebouw: {bouwdeel!r}")


# ── Scenario 3: Verwarmde ruimte (zelfde woning) ─────────────────────────────


def calc_f_ia_k_verwarmde_ruimte(
    bouwdeel: str,
    theta_i: float,
    theta_e: float,
    theta_a: float,
    heating_system_id_own: Optional[str] = None,
    heating_system_id_adjacent: Optional[str] = None,
    is_heated_surface: bool = False,
) -> float:
    """Calculate *f_ia,k* for a heated-room boundary within the same dwelling.

    Parameters
    ----------
    theta_a : design indoor temperature of the adjacent heated room [°C].
    heating_system_id_own : heating system of the current room.
    heating_system_id_adjacent : heating system of the adjacent room.
    """
    if is_heated_surface:
        return 0.0

    if theta_i == theta_e:
        raise ValueError("theta_i must not equal theta_e")

    bouwdeel = bouwdeel.lower()

    if bouwdeel == "wand":
        # Formula 2.17
        return (theta_i - theta_a) / (theta_i - theta_e)

    if bouwdeel in ("vloer", "plafond"):
        if heating_system_id_own is None or heating_system_id_adjacent is None:
            raise ValueError(
                "Both heating_system_id_own and heating_system_id_adjacent are "
                "required for vloer and plafond"
            )
        d1_own, d2_own = get_delta_theta(heating_system_id_own)
        d1_adj, d2_adj = get_delta_theta(heating_system_id_adjacent)

        if bouwdeel == "vloer":
            # Formula 2.18  — own Δθ₂ (floor) vs adjacent Δθ₁ (top/ceiling side)
            return ((theta_i + d2_own) - (theta_a + d1_adj)) / (
                theta_i - theta_e
            )
        # plafond — Formula 2.19
        return ((theta_i + d1_own) - (theta_a + d2_adj)) / (
            theta_i - theta_e
        )

    raise ValueError(f"Unknown bouwdeel for verwarmde ruimte: {bouwdeel!r}")


# ── Scenario 4a: Onverwarmde ruimte – bekende temperatuur ─────────────────────


def calc_f_k_onverwarmd_bekend(
    bouwdeel: str,
    theta_i: float,
    theta_e: float,
    theta_a: float,
    heating_system_id: Optional[str] = None,
    is_heated_surface: bool = False,
) -> float:
    """Calculate *f_k* for an unheated-room boundary with known temperature.

    Parameters
    ----------
    theta_a : temperature in the adjacent unheated space [°C].
    """
    if is_heated_surface:
        return 0.0

    if theta_i == theta_e:
        raise ValueError("theta_i must not equal theta_e")

    bouwdeel = bouwdeel.lower()
    d1, d2 = 0.0, 0.0
    if bouwdeel in ("vloer", "plafond"):
        if heating_system_id is None:
            raise ValueError(
                "heating_system_id is required for vloer and plafond"
            )
        d1, d2 = get_delta_theta(heating_system_id)

    if bouwdeel == "wand":
        # Formula 2.22
        return (theta_i - theta_a) / (theta_i - theta_e)
    if bouwdeel == "vloer":
        # Formula 2.23
        return ((theta_i + d2) - theta_a) / (theta_i - theta_e)
    if bouwdeel == "plafond":
        # Formula 2.24
        return ((theta_i + d1) - theta_a) / (theta_i - theta_e)

    raise ValueError(f"Unknown bouwdeel for onverwarmd (bekend): {bouwdeel!r}")


# ── Scenario 4b: Onverwarmde ruimte – onbekende temperatuur ───────────────────


def calc_f_k_onverwarmd_onbekend_warmteverlies(
    ruimte_type: str,
    *,
    aantal_externe_gevels: Optional[int] = None,
    buitendeur_aanwezig: Optional[bool] = None,
    daktype: Optional[str] = None,
    heeft_buitenwanden: Optional[bool] = None,
    ventilatievoud: Optional[float] = None,
    a_opening_per_v: Optional[float] = None,
    openingsgrootte_mm2_per_m2: Optional[float] = None,
) -> float:
    """Return *f_k* from **Tabel 2.3** (heat-loss calculation, θ_a unknown).

    Parameters
    ----------
    ruimte_type :
        ``"vertrek"``, ``"dak"``, ``"verkeersruimte"``, or ``"kruipruimte"``.
    """
    ruimte_type = ruimte_type.lower()

    # ── Category 1: Vertrek / ruimte ──
    if ruimte_type == "vertrek":
        if aantal_externe_gevels is None:
            raise ValueError("aantal_externe_gevels is required for vertrek")
        for entry in _tabel_2_3["vertrek"]["waarden"]:
            spec = entry["aantal_externe_scheidingsconstructies"]
            if spec == "3+" and aantal_externe_gevels >= 3:
                return entry["f_k"]
            if isinstance(spec, int) and spec == aantal_externe_gevels:
                if spec == 2:
                    if buitendeur_aanwezig is None:
                        raise ValueError(
                            "buitendeur_aanwezig is required when "
                            "aantal_externe_gevels == 2"
                        )
                    if entry["buitendeur_aanwezig"] == buitendeur_aanwezig:
                        return entry["f_k"]
                else:
                    return entry["f_k"]
        raise ValueError(
            f"No matching entry in Tabel 2.3 vertrek for "
            f"gevels={aantal_externe_gevels}, deur={buitendeur_aanwezig}"
        )

    # ── Category 2: Ruimte onder het dak ──
    if ruimte_type == "dak":
        if daktype is None:
            raise ValueError("daktype is required for dak")
        for entry in _tabel_2_3["dak"]["waarden"]:
            if entry["daktype"] == daktype:
                return entry["f_k"]
        raise ValueError(f"Unknown daktype: {daktype!r}")

    # ── Category 3: Gemeenschappelijke verkeersruimte ──
    if ruimte_type == "verkeersruimte":
        # Check "no exterior walls and low ventilation" first
        if (
            heeft_buitenwanden is False
            and ventilatievoud is not None
            and ventilatievoud < 0.5
        ):
            return 0.0
        # Check "freely ventilated"
        if a_opening_per_v is not None and a_opening_per_v > 0.005:
            return 1.0
        # Remaining cases
        return 0.5

    # ── Category 4: Vloer boven kruipruimte ──
    if ruimte_type == "kruipruimte":
        if openingsgrootte_mm2_per_m2 is None:
            raise ValueError(
                "openingsgrootte_mm2_per_m2 is required for kruipruimte"
            )
        val = openingsgrootte_mm2_per_m2
        if val <= 1000:
            return 0.6
        if val <= 1500:
            return 0.8
        return 1.0

    raise ValueError(f"Unknown ruimte_type: {ruimte_type!r}")


def calc_f_k_onverwarmd_onbekend_tijdconstante(
    aangrenzende_ruimte: str,
) -> float:
    """Return *f_k* from **Tabel 2.13** (time-constant calculation).

    Parameters
    ----------
    aangrenzende_ruimte :
        ``"kelder"``, ``"stallingsruimte"``, or
        ``"kruipruimte_serre_trappenhuis"``.
    """
    for entry in _tabel_2_13["waarden"]:
        if entry["aangrenzende_ruimte"] == aangrenzende_ruimte:
            return entry["f_k"]
    raise ValueError(f"Unknown aangrenzende_ruimte: {aangrenzende_ruimte!r}")


# ── Scenario 5: Grond ─────────────────────────────────────────────────────────


def calc_f_gw(grondwaterdiepte_m: Optional[float] = None) -> float:
    """Return the groundwater factor *f_gw*.

    Parameters
    ----------
    grondwaterdiepte_m :
        Depth of groundwater table below floor level [m].
        ``None`` is treated as *unknown* → 1.15.
    """
    if grondwaterdiepte_m is not None and grondwaterdiepte_m >= 1.0:
        return 1.00
    return 1.15


def calc_f_ig_k(
    bouwdeel: str,
    theta_i: float,
    theta_e: float = DEFAULT_THETA_E,
    theta_me: float = DEFAULT_THETA_ME,
    heating_system_id: Optional[str] = None,
    is_heated_surface: bool = False,
) -> float:
    """Calculate *f_ig,k* for a ground-contact boundary.

    Parameters
    ----------
    bouwdeel : ``"wand"`` or ``"vloer"``.
    theta_me : mean annual outdoor temperature [°C] (default 10.5 for NL).
    """
    if is_heated_surface:
        return 0.0

    if theta_i == theta_e:
        raise ValueError("theta_i must not equal theta_e")

    bouwdeel = bouwdeel.lower()

    if bouwdeel == "wand":
        # Formula 2.27
        return (theta_i - theta_me) / (theta_i - theta_e)

    if bouwdeel == "vloer":
        if heating_system_id is None:
            raise ValueError("heating_system_id is required for vloer")
        _d1, d2 = get_delta_theta(heating_system_id)
        # Formula 2.28
        return ((theta_i + d2) - theta_me) / (theta_i - theta_e)

    raise ValueError(f"Unknown bouwdeel for grond: {bouwdeel!r}")


def calc_u_equiv_k(r_c: float) -> float:
    """Return *U_equiv,k* [W/(m²·K)] based on the construction's *R_c*.

    Parameters
    ----------
    r_c : thermal resistance of the ground-contact construction [m²·K/W].
    """
    for entry in _tabel_u_equiv_k["waarden"]:
        r_min = entry["R_c_min_m2KperW"]
        r_max = entry["R_c_max_m2KperW"]
        if r_min is not None and r_c < r_min:
            continue
        if r_max is not None and r_c >= r_max:
            continue
        return entry["U_equiv_k_W_per_m2K"]
    raise ValueError(f"No matching U_equiv_k entry for R_c={r_c}")


def calc_h_t_ig(
    area: float,
    r_c: float,
    f_ig_k: float,
    f_gw: float,
) -> float:
    """Return *H_T,ig* [W/K] — the ground-contact transmission heat loss coefficient.

    ``H_T,ig = A · U_equiv,k · f_ig,k · f_gw``
    """
    u_eq = calc_u_equiv_k(r_c)
    return area * u_eq * f_ig_k * f_gw
