"""Tests for the f_k and f_ig,k correction-factor calculations in heat_calc.py."""

import pytest
from heat_calc import (
    HEATING_SYSTEMS,
    THETA_E_DEFAULT,
    THETA_ME_DEFAULT,
    get_delta_theta,
    calculate_fk_formula,
    lookup_fk_table_2_3,
    lookup_fk_table_2_13,
    get_f_gw,
    calculate_fig_k,
    get_u_equiv_k,
    calculate_h_t_ig,
    validate_fk,
)


# ── get_delta_theta ───────────────────────────────────────────────────────────

class TestGetDeltaTheta:
    def test_wand_always_zero(self):
        for hs in HEATING_SYSTEMS:
            assert get_delta_theta(hs, 'wand') == 0.0

    def test_plafond_returns_dth1(self):
        assert get_delta_theta('Gashaard, gevelkachel etc.', 'plafond') == 4.0
        assert get_delta_theta('IR-panelen plafondmontage', 'plafond') == 0.0

    def test_vloer_returns_dth2(self):
        assert get_delta_theta('Gashaard, gevelkachel etc.', 'vloer') == -1.0
        assert get_delta_theta('IR-panelen wandmontage', 'vloer') == -0.5

    def test_unknown_system_raises(self):
        with pytest.raises(ValueError, match="Onbekend verwarmingssysteem"):
            get_delta_theta('Niet bestaand systeem', 'vloer')

    def test_invalid_component_raises(self):
        with pytest.raises(ValueError, match="Ongeldig bouwdeeltype"):
            get_delta_theta('Plafondverwarming', 'dak')


# ── Scenario A – calculate_fk_formula ─────────────────────────────────────────

class TestCalculateFkFormula:
    def test_wand_basic(self):
        # f_k = (20 - 5) / (20 - (-10)) = 15 / 30 = 0.5
        assert calculate_fk_formula(20, -10, 5, 'wand') == pytest.approx(0.5)

    def test_wand_equal_temps(self):
        # θ_a == θ_i → f_k = 0
        assert calculate_fk_formula(20, -10, 20, 'wand') == pytest.approx(0.0)

    def test_vloer_with_heating(self):
        # Radiatoren/convectoren Lt: Δθ_2 = -1
        # f_k = ((20 + (-1)) - 5) / (20 - (-10)) = 14/30
        fk = calculate_fk_formula(20, -10, 5, 'vloer',
                                  heating_system='Radiatoren/convectoren Lt')
        assert fk == pytest.approx(14.0 / 30.0)

    def test_plafond_with_heating(self):
        # Gashaard: Δθ_1 = 4
        # f_k = ((20 + 4) - 5) / (20 - (-10)) = 19/30
        fk = calculate_fk_formula(20, -10, 5, 'plafond',
                                  heating_system='Gashaard, gevelkachel etc.')
        assert fk == pytest.approx(19.0 / 30.0)

    def test_zero_denominator_raises(self):
        with pytest.raises(ValueError, match="deler = 0"):
            calculate_fk_formula(10, 10, 5, 'wand')


# ── Scenario B – lookup_fk_table_2_3 ─────────────────────────────────────────

class TestLookupFkTable23:
    # Vertrek
    def test_vertrek_1_wall(self):
        assert lookup_fk_table_2_3('vertrek', external_walls=1) == 0.4

    def test_vertrek_2_walls_no_door(self):
        assert lookup_fk_table_2_3('vertrek', external_walls=2,
                                   exterior_door=False) == 0.5

    def test_vertrek_2_walls_with_door(self):
        assert lookup_fk_table_2_3('vertrek', external_walls=2,
                                   exterior_door=True) == 0.6

    def test_vertrek_3plus_walls(self):
        assert lookup_fk_table_2_3('vertrek', external_walls=3) == 0.8
        assert lookup_fk_table_2_3('vertrek', external_walls=5) == 0.8

    # Dak
    def test_dak_pannendak(self):
        assert lookup_fk_table_2_3('dak',
                                   roof_type='pannendak_zonder_folie') == 1.0

    def test_dak_niet_geisoleerd(self):
        assert lookup_fk_table_2_3('dak',
                                   roof_type='niet_geisoleerd') == 0.9

    def test_dak_geisoleerd(self):
        assert lookup_fk_table_2_3('dak', roof_type='geisoleerd') == 0.7

    def test_dak_invalid_raises(self):
        with pytest.raises(ValueError, match="Ongeldig daktype"):
            lookup_fk_table_2_3('dak', roof_type='onbekend')

    # Verkeersruimte
    def test_verkeersruimte_internal_low_vent(self):
        assert lookup_fk_table_2_3('verkeersruimte',
                                   has_exterior_walls=False,
                                   ventilation_rate=0.3) == 0.0

    def test_verkeersruimte_free_ventilated(self):
        assert lookup_fk_table_2_3('verkeersruimte',
                                   has_exterior_walls=True,
                                   a_opening_v=0.006) == 1.0

    def test_verkeersruimte_other(self):
        assert lookup_fk_table_2_3('verkeersruimte',
                                   has_exterior_walls=True,
                                   ventilation_rate=0.6,
                                   a_opening_v=0.003) == 0.5

    # Kruipruimte
    def test_kruipruimte_zwak_string(self):
        assert lookup_fk_table_2_3('kruipruimte',
                                   opening_size='zwak') == 0.6

    def test_kruipruimte_matig_string(self):
        assert lookup_fk_table_2_3('kruipruimte',
                                   opening_size='matig') == 0.8

    def test_kruipruimte_sterk_string(self):
        assert lookup_fk_table_2_3('kruipruimte',
                                   opening_size='sterk') == 1.0

    def test_kruipruimte_numeric_low(self):
        assert lookup_fk_table_2_3('kruipruimte', opening_size=800) == 0.6

    def test_kruipruimte_numeric_mid(self):
        assert lookup_fk_table_2_3('kruipruimte', opening_size=1200) == 0.8

    def test_kruipruimte_numeric_high(self):
        assert lookup_fk_table_2_3('kruipruimte', opening_size=2000) == 1.0

    def test_kruipruimte_boundary_1000(self):
        assert lookup_fk_table_2_3('kruipruimte', opening_size=1000) == 0.6

    def test_kruipruimte_boundary_1500(self):
        assert lookup_fk_table_2_3('kruipruimte', opening_size=1500) == 0.8

    # Invalid category
    def test_invalid_category_raises(self):
        with pytest.raises(ValueError, match="Onbekende categorie"):
            lookup_fk_table_2_3('onbekend')


# ── Scenario C – lookup_fk_table_2_13 ────────────────────────────────────────

class TestLookupFkTable213:
    def test_kelder(self):
        assert lookup_fk_table_2_13('kelder') == 0.5

    def test_stallingsruimte(self):
        assert lookup_fk_table_2_13('stallingsruimte') == 1.0

    def test_kruipruimte(self):
        assert lookup_fk_table_2_13('kruipruimte') == 0.8

    def test_serre(self):
        assert lookup_fk_table_2_13('serre') == 0.8

    def test_trappenhuis(self):
        assert lookup_fk_table_2_13('trappenhuis') == 0.8

    def test_case_insensitive(self):
        assert lookup_fk_table_2_13('Kelder') == 0.5

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Onbekend ruimtetype"):
            lookup_fk_table_2_13('garage')


# ── f_gw – groundwater factor ────────────────────────────────────────────────

class TestGetFgw:
    def test_deep_groundwater(self):
        assert get_f_gw(2.0) == 1.0

    def test_exactly_1m(self):
        assert get_f_gw(1.0) == 1.0

    def test_shallow_groundwater(self):
        assert get_f_gw(0.5) == 1.15

    def test_zero_depth(self):
        assert get_f_gw(0.0) == 1.15


# ── Scenario E – calculate_fig_k ─────────────────────────────────────────────

class TestCalculateFigK:
    def test_heated_element_returns_zero(self):
        assert calculate_fig_k(22, -10, 10.5, 'wand',
                               heated_element_on_ground=True) == 0.0

    def test_wand_standard_nl(self):
        # f_ig,k = (22 - 10.5) / (22 - (-10)) = 11.5 / 32 ≈ 0.359375
        fig = calculate_fig_k(22, -10, 10.5, 'wand')
        assert fig == pytest.approx(11.5 / 32.0)

    def test_vloer_with_heating(self):
        # Radiatoren/convectoren Lt: Δθ_2 = -1
        # f_ig,k = ((22 + (-1)) - 10.5) / (22 - (-10)) = 10.5 / 32
        fig = calculate_fig_k(22, -10, 10.5, 'vloer',
                              heating_system='Radiatoren/convectoren Lt')
        assert fig == pytest.approx(10.5 / 32.0)

    def test_plafond_raises(self):
        with pytest.raises(ValueError, match="niet van toepassing"):
            calculate_fig_k(22, -10, 10.5, 'plafond')

    def test_zero_denominator_raises(self):
        with pytest.raises(ValueError, match="deler = 0"):
            calculate_fig_k(10, 10, 10.5, 'wand')


# ── Scenario F – get_u_equiv_k ───────────────────────────────────────────────

class TestGetUEquivK:
    def test_high_rc(self):
        assert get_u_equiv_k(6.0) == 0.13

    def test_rc_5(self):
        assert get_u_equiv_k(5.0) == 0.13

    def test_mid_high_rc(self):
        assert get_u_equiv_k(4.0) == 0.18

    def test_rc_3_5(self):
        assert get_u_equiv_k(3.5) == 0.18

    def test_mid_rc(self):
        assert get_u_equiv_k(3.0) == 0.30

    def test_rc_2_5(self):
        assert get_u_equiv_k(2.5) == 0.30

    def test_low_rc(self):
        assert get_u_equiv_k(1.0) == 0.50


# ── calculate_h_t_ig ─────────────────────────────────────────────────────────

class TestCalculateHtIg:
    def test_basic(self):
        # 10 * 0.18 * 0.36 * 1.0 = 0.648
        h = calculate_h_t_ig(10.0, 0.18, 0.36, 1.0)
        assert h == pytest.approx(0.648)

    def test_with_groundwater(self):
        h = calculate_h_t_ig(10.0, 0.18, 0.36, 1.15)
        assert h == pytest.approx(10.0 * 0.18 * 0.36 * 1.15)


# ── validate_fk ──────────────────────────────────────────────────────────────

class TestValidateFk:
    def test_in_range(self):
        assert validate_fk(0.5) is None

    def test_zero(self):
        assert validate_fk(0.0) is None

    def test_one(self):
        assert validate_fk(1.0) is None

    def test_above(self):
        assert validate_fk(1.1) is not None

    def test_below(self):
        assert validate_fk(-0.1) is not None
