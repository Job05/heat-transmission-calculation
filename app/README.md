# Heat Transmission Calculator – Desktop Application

A PyQt5-based desktop application that provides two interactive calculation
tools originally developed as Jupyter Notebook widgets.

![Dark mode – U-value calculator](https://github.com/user-attachments/assets/44b27a66-59c0-46a8-b362-90f5cba0ec4c)

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application (from the repository root)
python -m app
```

## Project structure

```
app/
├── __init__.py        # Package docstring
├── __main__.py        # Entry point (python -m app)
├── main_window.py     # QMainWindow with three tabs and theme engine
├── u_value_tab.py     # Tool 1 – U-value / heat-transmission calculator
├── fk_calc_tab.py     # Tool 2 – Correction-factor calculator (f_k, f_ia,k, f_ig,k)
├── settings_tab.py    # Settings tab (theme switching, about info)
├── config.py          # JSON-backed user preferences
└── README.md          # This file
```

### Supporting files (repository root)

| File / folder               | Purpose |
|-----------------------------|---------|
| `heat_calc.py`              | Pure-Python helpers & constants for U-value calculations |
| `fk_calc.py`                | Pure-Python correction-factor formulas |
| `material_properties.json`  | Material thermal-conductivity database |
| `tables/`                   | Reference data tables (JSON) used by `fk_calc.py` |
| `requirements.txt`          | Python dependencies for the desktop app |
| `user_preferences.json`     | Auto-generated at runtime – stores appearance settings |

## Tabs

### 1. U-waarde Calculator (Tool 1)

Calculates the thermal transmittance (U-value) of a multi-layer building
construction.

* Add / remove construction layers dynamically.
* Each layer can use a material from the JSON database **or** a manually
  entered R-value (e.g. for air gaps).
* Categories include concrete, wood, insulation, glass, doors, floors, etc.
* The result table and U-value update live as inputs change.

### 2. Correctiefactoren (Tool 2)

Computes heat-loss correction factors based on the adjacent boundary
condition.  Six scenarios are supported:

| # | Scenario | Output factor |
|---|----------|---------------|
| 1 | Buitenlucht (exterior air) | f_k |
| 2 | Aangrenzend gebouw (adjacent building) | f_ia,k |
| 3 | Verwarmde ruimte (heated room, same dwelling) | f_ia,k |
| 4a | Onverwarmde ruimte – bekende temperatuur | f_k |
| 4b | Onverwarmde ruimte – onbekende temperatuur | f_k (Tabel 2.3 / 2.13) |
| 5 | Grond (ground contact) | f_ig,k · f_gw |

Dynamic input fields appear based on the selected scenario.

### 3. Instellingen (Settings)

* **Theme switching** – toggle between dark and light mode (Catppuccin
  colour palette).
* Preferences are saved automatically to `user_preferences.json`.

## How to add a new tool / tab

1. Create a new module in `app/`, e.g. `app/my_tool_tab.py`.
2. Define a `QWidget` subclass with the tool's UI and logic.
3. Import it in `app/main_window.py` and add a tab:

   ```python
   from .my_tool_tab import MyToolTab

   # inside MainWindow.__init__:
   self.my_tool_tab = MyToolTab(config)
   self.tabs.addTab(self.my_tool_tab, "My Tool")
   ```

4. If the tool needs persistent data, load/save JSON files from the
   repository root (like `material_properties.json`).

## How to add a new setting

1. Add a default value in `config.py` → `_DEFAULTS` dictionary.
2. Optionally add a typed property on the `Config` class.
3. Add a UI control in `app/settings_tab.py` and wire it to
   `config.set(key, value)` + `config.save()`.

## Data storage

* **Reference tables** – read-only JSON files in `tables/` (loaded by
  `fk_calc.py` at import time).
* **Material database** – `material_properties.json` (loaded by
  `u_value_tab.py` at import time).
* **User preferences** – `user_preferences.json` (read/written by
  `app/config.py`; git-ignored).

## Dependencies

* Python ≥ 3.10
* PyQt5 ≥ 5.15

Install with:

```bash
pip install -r requirements.txt
```
