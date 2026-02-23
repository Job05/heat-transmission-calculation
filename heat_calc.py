"""heat_calc.py – Computation logic for the U-value / heat-transmission calculator.

Contains constants, material look-up helpers, and the LayerWidget class.
Import this module from the notebook to keep the notebook concise and readable.
"""

try:
    import ipywidgets as widgets
except ImportError:  # allow import of helpers without ipywidgets (e.g. desktop app)
    widgets = None

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
