"""Tests for fk_calc – correction-factor calculator."""

import math
import pytest

import fk_calc


# ── Helper lookup tests ──────────────────────────────────────────────────────


class TestListHeatingSystems:
    def test_returns_list(self):
        systems = fk_calc.list_heating_systems()
        assert isinstance(systems, list)
        assert len(systems) > 0

    def test_entry_structure(self):
        entry = fk_calc.list_heating_systems()[0]
        assert "id" in entry
        assert "delta_theta_1" in entry
        assert "delta_theta_2" in entry


class TestGetDeltaTheta:
    def test_known_system(self):
        d1, d2 = fk_calc.get_delta_theta("gashaard_gevelkachel")
        assert d1 == 4
        assert d2 == -1

    def test_floor_heating_low(self):
        d1, d2 = fk_calc.get_delta_theta("vloerverwarming_laag_hoofd")
        assert d1 == 0
        assert d2 == -0.5

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            fk_calc.get_delta_theta("nonexistent_system")


class TestGetThetaI:
    def test_verblijfsruimte(self):
        assert fk_calc.get_theta_i("verblijfsruimte") == 22.0

    def test_toiletruimte(self):
        assert fk_calc.get_theta_i("toiletruimte") == 18.0

    def test_senioren(self):
        assert (
            fk_calc.get_theta_i(
                "toiletruimte", "seniorenwoningen_verzorgingstehuizen"
            )
            == 20.0
        )

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            fk_calc.get_theta_i("xxx")


# ── Scenario 1: Buitenlucht ──────────────────────────────────────────────────


class TestBuitenlucht:
    def test_buitenwand(self):
        assert fk_calc.calc_f_k_buitenlucht("buitenwand", 22, -10) == 1.0

    def test_schuin_dak(self):
        assert fk_calc.calc_f_k_buitenlucht("schuin_dak", 22, -10) == 1.0

    def test_heated_surface(self):
        assert (
            fk_calc.calc_f_k_buitenlucht(
                "buitenwand", 22, -10, is_heated_surface=True
            )
            == 0.0
        )

    def test_vloer_boven_buitenlucht(self):
        # θ_i=22, θ_e=-10, Δθ_2=-1 (gashaard) → (22-1-(-10))/(22-(-10))=31/32
        f = fk_calc.calc_f_k_buitenlucht(
            "vloer_boven_buitenlucht", 22, -10, "gashaard_gevelkachel"
        )
        assert math.isclose(f, 31 / 32, rel_tol=1e-9)

    def test_plat_dak(self):
        # θ_i=22, θ_e=-10, Δθ_1=4 (gashaard) → (22+4-(-10))/(22-(-10))=36/32
        f = fk_calc.calc_f_k_buitenlucht(
            "plat_dak", 22, -10, "gashaard_gevelkachel"
        )
        assert math.isclose(f, 36 / 32, rel_tol=1e-9)

    def test_missing_heating_system_raises(self):
        with pytest.raises(ValueError):
            fk_calc.calc_f_k_buitenlucht("vloer_boven_buitenlucht", 22, -10)

    def test_equal_temps_raises(self):
        with pytest.raises(ValueError):
            fk_calc.calc_f_k_buitenlucht("plat_dak", 10, 10, "radiatoren_lt")

    def test_unknown_bouwdeel_raises(self):
        with pytest.raises(ValueError):
            fk_calc.calc_f_k_buitenlucht("kelder", 22, -10)


# ── Scenario 2: Aangrenzend gebouw ────────────────────────────────────────────


class TestAangrenzendGebouw:
    def test_wand(self):
        # (22 - 20)/(22 - (-10)) = 2/32
        f = fk_calc.calc_f_ia_k_aangrenzend_gebouw("wand", 22, -10, 20)
        assert math.isclose(f, 2 / 32, rel_tol=1e-9)

    def test_vloer(self):
        # Δθ_2=-1 (radiatoren_lt) → (22-1-20)/(22-(-10)) = 1/32
        f = fk_calc.calc_f_ia_k_aangrenzend_gebouw(
            "vloer", 22, -10, 20, "radiatoren_lt"
        )
        assert math.isclose(f, 1 / 32, rel_tol=1e-9)

    def test_plafond(self):
        # Δθ_1=2 (radiatoren_lt) → (22+2-20)/(22-(-10)) = 4/32
        f = fk_calc.calc_f_ia_k_aangrenzend_gebouw(
            "plafond", 22, -10, 20, "radiatoren_lt"
        )
        assert math.isclose(f, 4 / 32, rel_tol=1e-9)

    def test_heated_surface(self):
        f = fk_calc.calc_f_ia_k_aangrenzend_gebouw(
            "wand", 22, -10, 20, is_heated_surface=True
        )
        assert f == 0.0

    def test_missing_system_vloer_raises(self):
        with pytest.raises(ValueError):
            fk_calc.calc_f_ia_k_aangrenzend_gebouw("vloer", 22, -10, 20)


# ── Scenario 3: Verwarmde ruimte (zelfde woning) ─────────────────────────────


class TestVerwarmdeRuimte:
    def test_wand(self):
        # (22 - 18)/(22 - (-10)) = 4/32
        f = fk_calc.calc_f_ia_k_verwarmde_ruimte("wand", 22, -10, 18)
        assert math.isclose(f, 4 / 32, rel_tol=1e-9)

    def test_vloer(self):
        # own Δθ_2=-1, adjacent Δθ_1=2 (radiatoren_lt both)
        # ((22-1) - (18+2)) / (22-(-10)) = (21 - 20) / 32 = 1/32
        f = fk_calc.calc_f_ia_k_verwarmde_ruimte(
            "vloer", 22, -10, 18, "radiatoren_lt", "radiatoren_lt"
        )
        assert math.isclose(f, 1 / 32, rel_tol=1e-9)

    def test_plafond(self):
        # own Δθ_1=2, adjacent Δθ_2=-1 (radiatoren_lt both)
        # ((22+2) - (18-1)) / (22-(-10)) = (24 - 17) / 32 = 7/32
        f = fk_calc.calc_f_ia_k_verwarmde_ruimte(
            "plafond", 22, -10, 18, "radiatoren_lt", "radiatoren_lt"
        )
        assert math.isclose(f, 7 / 32, rel_tol=1e-9)

    def test_heated_surface(self):
        f = fk_calc.calc_f_ia_k_verwarmde_ruimte(
            "wand", 22, -10, 18, is_heated_surface=True
        )
        assert f == 0.0

    def test_missing_systems_raises(self):
        with pytest.raises(ValueError):
            fk_calc.calc_f_ia_k_verwarmde_ruimte("vloer", 22, -10, 18)


# ── Scenario 4a: Onverwarmde ruimte – bekende temperatuur ─────────────────────


class TestOnverwarmBekend:
    def test_wand(self):
        # (22 - 5)/(22 - (-10)) = 17/32
        f = fk_calc.calc_f_k_onverwarmd_bekend("wand", 22, -10, 5)
        assert math.isclose(f, 17 / 32, rel_tol=1e-9)

    def test_vloer(self):
        # Δθ_2=-1 (gashaard) → (22-1-5)/(22-(-10)) = 16/32 = 0.5
        f = fk_calc.calc_f_k_onverwarmd_bekend(
            "vloer", 22, -10, 5, "gashaard_gevelkachel"
        )
        assert math.isclose(f, 0.5, rel_tol=1e-9)

    def test_plafond(self):
        # Δθ_1=4 (gashaard) → (22+4-5)/(22-(-10)) = 21/32
        f = fk_calc.calc_f_k_onverwarmd_bekend(
            "plafond", 22, -10, 5, "gashaard_gevelkachel"
        )
        assert math.isclose(f, 21 / 32, rel_tol=1e-9)

    def test_heated_surface(self):
        f = fk_calc.calc_f_k_onverwarmd_bekend(
            "wand", 22, -10, 5, is_heated_surface=True
        )
        assert f == 0.0


# ── Scenario 4b: Onverwarmde ruimte – onbekende temperatuur ───────────────────


class TestOnverwarmOnbekendWarmteverlies:
    """Tabel 2.3 look-ups."""

    # Vertrek
    def test_vertrek_1_gevel(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "vertrek", aantal_externe_gevels=1
            )
            == 0.4
        )

    def test_vertrek_2_gevels_zonder_deur(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "vertrek", aantal_externe_gevels=2, buitendeur_aanwezig=False
            )
            == 0.5
        )

    def test_vertrek_2_gevels_met_deur(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "vertrek", aantal_externe_gevels=2, buitendeur_aanwezig=True
            )
            == 0.6
        )

    def test_vertrek_3plus_gevels(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "vertrek", aantal_externe_gevels=3
            )
            == 0.8
        )

    def test_vertrek_4_gevels(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "vertrek", aantal_externe_gevels=4
            )
            == 0.8
        )

    def test_vertrek_missing_gevels_raises(self):
        with pytest.raises(ValueError):
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies("vertrek")

    def test_vertrek_2_gevels_missing_deur_raises(self):
        with pytest.raises(ValueError):
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "vertrek", aantal_externe_gevels=2
            )

    # Dak
    def test_dak_pannendak(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "dak", daktype="pannendak_zonder_folie"
            )
            == 1.0
        )

    def test_dak_niet_geisoleerd(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "dak", daktype="niet_geisoleerd"
            )
            == 0.9
        )

    def test_dak_geisoleerd(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "dak", daktype="geisoleerd"
            )
            == 0.7
        )

    def test_dak_missing_daktype_raises(self):
        with pytest.raises(ValueError):
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies("dak")

    # Verkeersruimte
    def test_verkeersruimte_intern_laag_ventilatievoud(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "verkeersruimte",
                heeft_buitenwanden=False,
                ventilatievoud=0.3,
            )
            == 0.0
        )

    def test_verkeersruimte_vrij_geventileerd(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "verkeersruimte", a_opening_per_v=0.006
            )
            == 1.0
        )

    def test_verkeersruimte_overig(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "verkeersruimte",
                heeft_buitenwanden=True,
                ventilatievoud=0.3,
            )
            == 0.5
        )

    # Kruipruimte
    def test_kruipruimte_zwak(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "kruipruimte", openingsgrootte_mm2_per_m2=800
            )
            == 0.6
        )

    def test_kruipruimte_matig(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "kruipruimte", openingsgrootte_mm2_per_m2=1200
            )
            == 0.8
        )

    def test_kruipruimte_sterk(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "kruipruimte", openingsgrootte_mm2_per_m2=2000
            )
            == 1.0
        )

    def test_kruipruimte_boundary_1000(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "kruipruimte", openingsgrootte_mm2_per_m2=1000
            )
            == 0.6
        )

    def test_kruipruimte_boundary_1500(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies(
                "kruipruimte", openingsgrootte_mm2_per_m2=1500
            )
            == 0.8
        )

    def test_kruipruimte_missing_raises(self):
        with pytest.raises(ValueError):
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies("kruipruimte")

    # Unknown ruimte_type
    def test_unknown_ruimte_type_raises(self):
        with pytest.raises(ValueError):
            fk_calc.calc_f_k_onverwarmd_onbekend_warmteverlies("onbekend")


class TestOnverwarmOnbekendTijdconstante:
    """Tabel 2.13 look-ups."""

    def test_kelder(self):
        assert fk_calc.calc_f_k_onverwarmd_onbekend_tijdconstante("kelder") == 0.5

    def test_stallingsruimte(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_tijdconstante("stallingsruimte")
            == 1.0
        )

    def test_kruipruimte_serre_trappenhuis(self):
        assert (
            fk_calc.calc_f_k_onverwarmd_onbekend_tijdconstante(
                "kruipruimte_serre_trappenhuis"
            )
            == 0.8
        )

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            fk_calc.calc_f_k_onverwarmd_onbekend_tijdconstante("xxx")


# ── Scenario 5: Grond ─────────────────────────────────────────────────────────


class TestGrondwaterfactor:
    def test_deep(self):
        assert fk_calc.calc_f_gw(2.0) == 1.00

    def test_exactly_1m(self):
        assert fk_calc.calc_f_gw(1.0) == 1.00

    def test_shallow(self):
        assert fk_calc.calc_f_gw(0.5) == 1.15

    def test_unknown(self):
        assert fk_calc.calc_f_gw(None) == 1.15


class TestFigk:
    def test_wand_example_from_doc(self):
        # From fk_berekening.md example: (22-10.5)/(22-(-10)) = 11.5/32 ≈ 0.359375
        f = fk_calc.calc_f_ig_k("wand", 22, -10, 10.5)
        assert math.isclose(f, 11.5 / 32, rel_tol=1e-9)

    def test_vloer(self):
        # Δθ_2=-1 (radiatoren_lt) → (22-1-10.5)/(22-(-10)) = 10.5/32
        f = fk_calc.calc_f_ig_k("vloer", 22, -10, 10.5, "radiatoren_lt")
        assert math.isclose(f, 10.5 / 32, rel_tol=1e-9)

    def test_heated_surface(self):
        f = fk_calc.calc_f_ig_k("wand", 22, -10, 10.5, is_heated_surface=True)
        assert f == 0.0

    def test_missing_system_vloer_raises(self):
        with pytest.raises(ValueError):
            fk_calc.calc_f_ig_k("vloer", 22, -10, 10.5)

    def test_defaults(self):
        # Uses DEFAULT_THETA_E=-10 and DEFAULT_THETA_ME=10.5
        f = fk_calc.calc_f_ig_k("wand", 22)
        assert math.isclose(f, 11.5 / 32, rel_tol=1e-9)


class TestUEquivK:
    def test_high_rc(self):
        assert fk_calc.calc_u_equiv_k(6.0) == 0.13

    def test_rc_5(self):
        assert fk_calc.calc_u_equiv_k(5.0) == 0.13

    def test_rc_4(self):
        assert fk_calc.calc_u_equiv_k(4.0) == 0.18

    def test_rc_3(self):
        assert fk_calc.calc_u_equiv_k(3.0) == 0.30

    def test_rc_2(self):
        assert fk_calc.calc_u_equiv_k(2.0) == 0.50

    def test_rc_boundary_35(self):
        assert fk_calc.calc_u_equiv_k(3.5) == 0.18

    def test_rc_boundary_25(self):
        assert fk_calc.calc_u_equiv_k(2.5) == 0.30


class TestHTig:
    def test_basic(self):
        # A=10, R_c=6 → U_eq=0.13, f_ig_k=0.36, f_gw=1.0
        # H_T,ig = 10 * 0.13 * 0.36 * 1.0 = 0.468
        h = fk_calc.calc_h_t_ig(area=10, r_c=6.0, f_ig_k=0.36, f_gw=1.0)
        assert math.isclose(h, 10 * 0.13 * 0.36 * 1.0, rel_tol=1e-9)

    def test_with_groundwater(self):
        h = fk_calc.calc_h_t_ig(area=10, r_c=2.0, f_ig_k=0.36, f_gw=1.15)
        assert math.isclose(h, 10 * 0.50 * 0.36 * 1.15, rel_tol=1e-9)


# ── Constants ─────────────────────────────────────────────────────────────────


class TestConstants:
    def test_default_theta_e(self):
        assert fk_calc.DEFAULT_THETA_E == -10.0

    def test_default_theta_me(self):
        assert fk_calc.DEFAULT_THETA_ME == 10.5
