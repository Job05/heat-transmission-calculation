"""heat_calc.py – Computation logic for the U-value / heat-transmission calculator.

Contains constants, material look-up helpers, the LayerWidget class,
and the f_k / f_ig,k correction-factor calculations.
Import this module from the notebook to keep the notebook concise and readable.
"""

import ipywidgets as widgets

# ── Constants ─────────────────────────────────────────────────────────────────

# For these categories the deepest value is the U-value [W/(m²·K)], not λ
U_VALUE_CATS = {'glas', 'deuren'}

# For these categories the value is already an R-value [m²·K/W]
R_VALUE_CATS = {'vloeren'}

# Standard surface resistances [m²·K/W]
SURFACE_R = {
    'Binnenzijde  —  Ri = 0,13 m²·K/W': 0.13,
    'Buitenzijde  —  Re = 0,04 m²·K/W': 0.04,
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def scalar(val):
    """Return the lowest float from a value that may be a list/range."""
    if isinstance(val, list):
        return float(min(val))
    if isinstance(val, (int, float)):
        return float(val)
    return None


def sub_keys(materials, main):
    """Return the sub-category keys for a main category."""
    v = materials.get(main, {})
    return list(v.keys()) if isinstance(v, dict) else []


def third_keys(materials, main, sub):
    """Return the third-level keys for a main/sub combination."""
    v = materials.get(main, {}).get(sub, None)
    return list(v.keys()) if isinstance(v, dict) else []


def raw_value(materials, main, sub, third=None):
    """Look up the raw λ / U / R value for a material selection."""
    v = materials.get(main, {}).get(sub, None)
    if isinstance(v, dict) and third:
        v = v.get(third, None)
    return v


# ── LayerWidget ───────────────────────────────────────────────────────────────

class LayerWidget:
    """Interactive widget representing one construction layer in the U-value form."""

    def __init__(self, materials, update_cb, remove_cb):
        self.materials = materials
        self.update_cb = update_cb
        self.remove_cb = remove_cb

        # Input mode toggle
        self.mode = widgets.ToggleButtons(
            options=['Materiaallijst', 'Handmatige R'],
            button_style='', layout=widgets.Layout(width='auto')
        )

        # ── Material selectors ──
        self.cat_dd = widgets.Dropdown(
            options=list(materials.keys()), description='Categorie:',
            layout=widgets.Layout(width='220px')
        )
        self.sub_dd = widgets.Dropdown(
            options=sub_keys(materials, self.cat_dd.value), description='Materiaal:',
            layout=widgets.Layout(width='270px')
        )
        self.third_dd = widgets.Dropdown(
            options=[], description='Subtype:',
            layout=widgets.Layout(width='220px', visibility='hidden')
        )
        self.thickness = widgets.BoundedFloatText(
            value=0.10, min=0.0, max=10.0, step=0.001,
            description='Dikte d [m]:', layout=widgets.Layout(width='195px')
        )
        self.lam_lbl = widgets.HTML(value='')

        # ── Manual R ──
        self.manual_r = widgets.BoundedFloatText(
            value=0.10, min=0.0, max=100.0, step=0.01,
            description='R [m²·K/W]:', layout=widgets.Layout(width='195px')
        )

        # Effective-R feedback & remove button
        self.r_lbl   = widgets.HTML(value='')
        self.rem_btn = widgets.Button(
            description='✕ Verwijder', button_style='danger',
            layout=widgets.Layout(width='130px', height='30px')
        )

        # Sub-boxes for each mode
        self.mat_box = widgets.VBox([
            widgets.HBox([self.cat_dd, self.sub_dd, self.third_dd]),
            widgets.HBox([self.thickness, self.lam_lbl]),
        ])
        self.man_box = widgets.VBox([self.manual_r])

        # Wire events
        self.mode.observe(self._on_mode, names='value')
        self.cat_dd.observe(self._on_cat, names='value')
        self.sub_dd.observe(self._on_sub, names='value')
        self.third_dd.observe(self._recalc, names='value')
        self.thickness.observe(self._recalc, names='value')
        self.manual_r.observe(self._recalc, names='value')
        self.rem_btn.on_click(lambda _: self.remove_cb(self))

        self._refresh_sub()
        self._refresh_third()
        self._recalc(None)

        self.box = widgets.VBox(
            [widgets.HBox([self.mode, self.rem_btn]),
             self.mat_box, self.r_lbl],
            layout=widgets.Layout(
                border='1px solid #bbb', padding='6px 10px',
                margin='4px 0', border_radius='4px'
            )
        )

    # ── private ──────────────────────────────────────────────────────────────

    def _on_mode(self, _):
        inner = self.mat_box if self.mode.value == 'Materiaallijst' else self.man_box
        self.box.children = [self.box.children[0], inner, self.r_lbl]
        self._recalc(None)

    def _on_cat(self, _):
        self._refresh_sub()
        self._refresh_third()
        self._recalc(None)

    def _on_sub(self, _):
        self._refresh_third()
        self._recalc(None)

    def _refresh_sub(self):
        opts = sub_keys(self.materials, self.cat_dd.value)
        self.sub_dd.options = opts if opts else ['—']

    def _refresh_third(self):
        sub = self.sub_dd.value if self.sub_dd.options else ''
        opts = third_keys(self.materials, self.cat_dd.value, sub)
        if opts:
            self.third_dd.options = opts
            self.third_dd.layout.visibility = 'visible'
        else:
            self.third_dd.options = ['—']
            self.third_dd.layout.visibility = 'hidden'

    def _recalc(self, _):
        r = self.get_r()
        if r is not None:
            self.r_lbl.value = (
                f'<span style="color:#1a7a1a;font-weight:bold">'
                f'&nbsp;&nbsp;→&nbsp; R = {r:.3f} m²·K/W</span>')
        else:
            self.r_lbl.value = (
                '<span style="color:#c00">'
                '&nbsp;&nbsp;→&nbsp; R kan niet worden bepaald</span>')

        # λ hint label (only relevant for standard materials)
        cat = self.cat_dd.value
        if self.mode.value != 'Materiaallijst' or cat in U_VALUE_CATS or cat in R_VALUE_CATS:
            self.lam_lbl.value = ''
            return
        third = self.third_dd.value if self.third_dd.layout.visibility == 'visible' else None
        val   = raw_value(self.materials, cat, self.sub_dd.value, third)
        if isinstance(val, list):
            self.lam_lbl.value = (
                f'<span style="color:#555">'
                f'&nbsp; λ = {val[0]} – {val[1]} W/(m·K) '
                f'&nbsp;(laagste waarde {min(val):.4f} gebruikt)</span>')
        elif isinstance(val, (int, float)):
            self.lam_lbl.value = (
                f'<span style="color:#555">'
                f'&nbsp; λ = {val} W/(m·K)</span>')
        else:
            self.lam_lbl.value = ''

        self.update_cb()

    # ── public ───────────────────────────────────────────────────────────────

    def get_r(self):
        """Compute and return the thermal resistance [m²·K/W] for this layer."""
        if self.mode.value == 'Handmatige R':
            return self.manual_r.value

        cat   = self.cat_dd.value
        sub   = self.sub_dd.value
        third = self.third_dd.value if self.third_dd.layout.visibility == 'visible' else None
        val   = raw_value(self.materials, cat, sub, third)

        if cat in U_VALUE_CATS:
            u = scalar(val)
            return (1.0 / u) if u else None

        if cat in R_VALUE_CATS:
            return scalar(val)

        lam = scalar(val)
        d   = self.thickness.value
        return (d / lam) if (lam and lam > 0 and d > 0) else None

    def row_info(self):
        """Return a dict with display info for the result table row."""
        cat   = self.cat_dd.value
        sub   = self.sub_dd.value
        third = self.third_dd.value if self.third_dd.layout.visibility == 'visible' else None
        r     = self.get_r()

        if self.mode.value == 'Handmatige R':
            return {'naam': 'Handmatig', 'd': None, 'lam': '—', 'R': r}

        val   = raw_value(self.materials, cat, sub, third)
        label = f'{cat} / {sub}' + (f' / {third}' if third else '')

        if cat in U_VALUE_CATS:
            u = scalar(val)
            return {'naam': label, 'd': None, 'lam': f'(U={u:.2f})', 'R': r}
        if cat in R_VALUE_CATS:
            return {'naam': label, 'd': None, 'lam': '(R-waarde)', 'R': r}

        lam = scalar(val)
        return {
            'naam': label,
            'd':    self.thickness.value,
            'lam':  f'{lam:.4f}' if lam else '—',
            'R':    r,
        }


# ══════════════════════════════════════════════════════════════════════════════
# f_k / f_ig,k  –  Correction-factor calculations
# ══════════════════════════════════════════════════════════════════════════════

# ── Standard temperatures for the Netherlands ─────────────────────────────────

THETA_E_DEFAULT = -10.0    # Ontwerpbuitentemperatuur [°C]
THETA_ME_DEFAULT = 10.5    # Jaarlijks gemiddelde buitentemperatuur [°C]

# ── Table 2.12 – Temperature corrections Δθ ──────────────────────────────────
# Keys are the heating-system descriptions (Dutch).
# Values are (Δθ_1, Δθ_2) in Kelvin.

HEATING_SYSTEMS = {
    'Gashaard, gevelkachel etc.':                           (4.0,  -1.0),
    'IR-panelen wandmontage':                               (1.0,  -0.5),
    'IR-panelen plafondmontage':                            (0.0,   0.0),
    'Radiatoren/convectoren Ht + luchtverwarming':          (3.0,  -1.0),
    'Radiatoren/convectoren Lt':                            (2.0,  -1.0),
    'Plafondverwarming':                                    (3.0,   0.0),
    'Wandverwarming':                                       (2.0,  -1.0),
    'Plintverwarming':                                      (1.0,   0.0),
    'Vloerverwarming + Ht-radiatoren/convectoren':          (3.0,   0.0),
    'Vloerverwarming + Lt-radiatoren/convectoren':          (2.0,  -1.0),
    'Vloerverwarming (θ_vloer ≥ 27°C) als hoofdverwarming': (0.0, -1.0),
    'Vloerverwarming (θ_vloer < 27°C) als hoofdverwarming': (0.0, -0.5),
    'Vloerverwarming en wandverwarming':                    (1.0,  -1.0),
    'Ventilatorgedreven convectoren/radiatoren':             (0.5,  0.0),
}

# ── Table §12 – Design indoor temperatures θ_i ──────────────────────────────

ROOM_TEMPERATURES_WOON = {
    'Verblijfsruimte':                                          22,
    'Badruimte':                                                22,
    'Verkeersruimte (hal, overloop, gang, trap)':               20,
    'Toiletruimte':                                             18,
    'Technische ruimte (niet zijnde stookruimte)':              15,
    'Bergruimte':                                               15,
    'Onbenoemde ruimte open verbinding met verkeersruimte':     20,
    'Inpandige bergruimte (bijv. afgesloten zolder)':           15,
}

ROOM_TEMPERATURES_SENIOREN = {
    'Verblijfsruimte':  22,
    'Badruimte':        22,
    'Toiletruimte':     20,
    'Verkeersruimte':   20,
    'Technische ruimte': 15,
}


# ── Helpers for Δθ lookup ─────────────────────────────────────────────────────

def get_delta_theta(heating_system, component):
    """Return the temperature correction Δθ for a heating system and component.

    Parameters
    ----------
    heating_system : str
        Key in :data:`HEATING_SYSTEMS`.
    component : str
        ``'plafond'`` → Δθ_1, ``'vloer'`` → Δθ_2, ``'wand'`` → 0.

    Returns
    -------
    float
        Temperature correction [K].

    Raises
    ------
    ValueError
        If *heating_system* is not recognised or *component* is invalid.
    """
    component = component.lower()
    if component == 'wand':
        return 0.0
    if heating_system not in HEATING_SYSTEMS:
        raise ValueError(f"Onbekend verwarmingssysteem: {heating_system!r}")
    dth1, dth2 = HEATING_SYSTEMS[heating_system]
    if component == 'plafond':
        return dth1
    if component == 'vloer':
        return dth2
    raise ValueError(f"Ongeldig bouwdeeltype: {component!r} "
                     "(verwacht 'wand', 'vloer' of 'plafond')")


# ── Scenario A – f_k via formula (θ_a known) ─────────────────────────────────

def calculate_fk_formula(theta_i, theta_e, theta_a, component,
                         heating_system=None):
    """Calculate f_k using formula 2.22 / 2.23 / 2.24.

    Parameters
    ----------
    theta_i : float
        Design indoor temperature [°C].
    theta_e : float
        Design outdoor temperature [°C].
    theta_a : float
        Temperature of the adjacent unheated space [°C].
    component : str
        ``'wand'``, ``'vloer'`` or ``'plafond'``.
    heating_system : str or None
        Required when *component* is ``'vloer'`` or ``'plafond'``.

    Returns
    -------
    float
        Correction factor f_k [-].

    Raises
    ------
    ValueError
        If inputs are invalid or the denominator is zero.
    """
    denom = theta_i - theta_e
    if denom == 0:
        raise ValueError("θ_i en θ_e mogen niet gelijk zijn (deler = 0)")

    dth = get_delta_theta(heating_system, component) if component.lower() in (
        'vloer', 'plafond') else 0.0

    fk = ((theta_i + dth) - theta_a) / denom
    return fk


# ── Scenario B – f_k from Table 2.3 (θ_a unknown, heat-loss) ─────────────────

def lookup_fk_table_2_3(category, **kwargs):
    """Look up f_k from Table 2.3 for the heat-loss calculation.

    Parameters
    ----------
    category : str
        One of ``'vertrek'``, ``'dak'``, ``'verkeersruimte'``,
        ``'kruipruimte'``.
    **kwargs
        Extra arguments depending on the category (see below).

    Keyword Arguments
    -----------------
    external_walls : int
        Number of external walls (1 / 2 / 3). For *vertrek*.
    exterior_door : bool
        Whether an exterior door is present (only for *vertrek* with 2 walls).
    roof_type : str
        ``'pannendak_zonder_folie'``, ``'niet_geisoleerd'`` or
        ``'geisoleerd'``. For *dak*.
    has_exterior_walls : bool
        Whether the space has exterior walls. For *verkeersruimte*.
    ventilation_rate : float
        Air-change rate [-]. For *verkeersruimte*.
    a_opening_v : float
        Opening-area / volume ratio [-]. For *verkeersruimte*.
    opening_size : float or str
        Opening size in mm²/m² (float) **or** one of ``'zwak'``,
        ``'matig'``, ``'sterk'``. For *kruipruimte*.

    Returns
    -------
    float
        f_k table value.

    Raises
    ------
    ValueError
        If the category or sub-parameters are not valid.
    """
    cat = category.lower()

    # ── Category 1: Vertrek / ruimte ──
    if cat == 'vertrek':
        walls = kwargs.get('external_walls', 1)
        door  = kwargs.get('exterior_door', False)
        if walls >= 3:
            return 0.8
        if walls == 2:
            return 0.6 if door else 0.5
        return 0.4  # 1 wall

    # ── Category 2: Ruimte onder het dak ──
    if cat == 'dak':
        roof = kwargs.get('roof_type', '')
        if roof == 'pannendak_zonder_folie':
            return 1.0
        if roof == 'niet_geisoleerd':
            return 0.9
        if roof == 'geisoleerd':
            return 0.7
        raise ValueError(f"Ongeldig daktype: {roof!r}")

    # ── Category 3: Gemeenschappelijke verkeersruimte ──
    if cat == 'verkeersruimte':
        has_ext = kwargs.get('has_exterior_walls', True)
        vent    = kwargs.get('ventilation_rate', 0.0)
        a_v     = kwargs.get('a_opening_v', 0.0)

        if not has_ext and vent < 0.5:
            return 0.0
        if a_v > 0.005:
            return 1.0
        return 0.5

    # ── Category 4: Vloer boven kruipruimte ──
    if cat == 'kruipruimte':
        size = kwargs.get('opening_size', 0)
        if isinstance(size, str):
            size = size.lower()
            if size == 'zwak':
                return 0.6
            if size == 'matig':
                return 0.8
            if size == 'sterk':
                return 1.0
            raise ValueError(f"Ongeldige ventilatiegraad: {size!r}")
        # numeric mm²/m²
        if size <= 1000:
            return 0.6
        if size <= 1500:
            return 0.8
        return 1.0

    raise ValueError(f"Onbekende categorie: {category!r}")


# ── Scenario C – f_k from Table 2.13 (time constant) ─────────────────────────

TABLE_2_13 = {
    'kelder':       0.5,
    'stallingsruimte': 1.0,
    'kruipruimte':  0.8,
    'serre':        0.8,
    'trappenhuis':  0.8,
}


def lookup_fk_table_2_13(space_type):
    """Look up f_k from Table 2.13 for the time-constant calculation.

    Parameters
    ----------
    space_type : str
        Type of adjacent unheated space.  Accepted values:
        ``'kelder'``, ``'stallingsruimte'``, ``'kruipruimte'``,
        ``'serre'``, ``'trappenhuis'``.

    Returns
    -------
    float
        f_k table value.
    """
    key = space_type.lower()
    if key not in TABLE_2_13:
        raise ValueError(
            f"Onbekend ruimtetype: {space_type!r}. "
            f"Kies uit: {', '.join(TABLE_2_13)}"
        )
    return TABLE_2_13[key]


# ── f_gw – Groundwater correction factor (§7) ────────────────────────────────

def get_f_gw(groundwater_depth):
    """Return the groundwater correction factor f_gw.

    Parameters
    ----------
    groundwater_depth : float
        Depth of the groundwater table below the floor level [m].

    Returns
    -------
    float
        1.00 if depth ≥ 1 m, otherwise 1.15.
    """
    return 1.0 if groundwater_depth >= 1.0 else 1.15


# ── Scenario E – f_ig,k via formula (§9) ─────────────────────────────────────

def calculate_fig_k(theta_i, theta_e, theta_me, component,
                    heating_system=None, heated_element_on_ground=False):
    """Calculate f_ig,k using formula 2.27 (wall) or 2.28 (floor).

    Parameters
    ----------
    theta_i : float
        Design indoor temperature [°C].
    theta_e : float
        Design outdoor temperature [°C].
    theta_me : float
        Annual mean outdoor temperature [°C].
    component : str
        ``'wand'`` or ``'vloer'``.
    heating_system : str or None
        Required when *component* is ``'vloer'``.
    heated_element_on_ground : bool
        If True the element is heated by floor/wall heating in direct contact
        with the ground → f_ig,k = 0.

    Returns
    -------
    float
        Correction factor f_ig,k [-].
    """
    if heated_element_on_ground:
        return 0.0

    component = component.lower()
    if component not in ('wand', 'vloer'):
        raise ValueError(f"f_ig,k is niet van toepassing op '{component}'. "
                         "Gebruik 'wand' of 'vloer'.")

    denom = theta_i - theta_e
    if denom == 0:
        raise ValueError("θ_i en θ_e mogen niet gelijk zijn (deler = 0)")

    if component == 'wand':
        return (theta_i - theta_me) / denom

    # vloer – needs Δθ_2
    dth2 = get_delta_theta(heating_system, 'vloer')
    return ((theta_i + dth2) - theta_me) / denom


# ── Scenario F – U_equiv,k from R_c (§10) ────────────────────────────────────

def get_u_equiv_k(r_c):
    """Return U_equiv,k based on the construction R_c.

    Parameters
    ----------
    r_c : float
        Thermal resistance of the construction in contact with the ground
        [m²·K/W].

    Returns
    -------
    float
        Equivalent U-value [W/(m²·K)].
    """
    if r_c >= 5.0:
        return 0.13
    if r_c >= 3.5:
        return 0.18
    if r_c >= 2.5:
        return 0.30
    return 0.50


# ── Combined ground heat-loss H_T,ig (§9 step E5) ────────────────────────────

def calculate_h_t_ig(area, u_equiv_k, f_ig_k, f_gw):
    """Calculate the specific heat loss through the ground.

    Parameters
    ----------
    area : float
        Construction area A [m²].
    u_equiv_k : float
        Equivalent U-value [W/(m²·K)].
    f_ig_k : float
        Ground correction factor [-].
    f_gw : float
        Groundwater correction factor [-].

    Returns
    -------
    float
        H_T,ig [W/K].
    """
    return area * u_equiv_k * f_ig_k * f_gw


# ── Validation helpers ────────────────────────────────────────────────────────

def validate_fk(value):
    """Check that f_k is in [0, 1]; return a warning string or None."""
    if value < 0.0 or value > 1.0:
        return (f"f_k = {value:.4f} valt buiten het verwachte bereik "
                "[0,0 – 1,0]. Controleer de invoerwaarden.")
    return None
