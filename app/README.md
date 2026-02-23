# Warmtetransmissie Rekentool – Desktop Applicatie

Een PyQt5-gebaseerde desktop applicatie met twee interactieve rekentools
voor warmtetransmissieberekeningen.

## Snel starten

```bash
# Installeer afhankelijkheden
pip install -r requirements.txt

# Start de applicatie (vanuit de repository-root)
python -m app
```

## Projectstructuur

```
app/
├── __init__.py        # Pakket met versienummer
├── __main__.py        # Startpunt (python -m app)
├── main_window.py     # Hoofdvenster met drie tabbladen en thema-engine
├── u_value_tab.py     # Tool 1 – U-waarde calculator
├── fk_calc_tab.py     # Tool 2 – Correctiefactoren (f_k, f_ia,k, f_ig,k)
├── settings_tab.py    # Instellingen (thema wisselen, over-informatie)
├── config.py          # JSON-gebaseerde gebruikersvoorkeuren
└── README.md          # Dit bestand
```

### Ondersteunende bestanden (repository-root)

| Bestand / map                | Doel |
|------------------------------|------|
| `heat_calc.py`               | Hulpfuncties en constanten voor U-waarde berekeningen |
| `fk_calc.py`                 | Correctiefactor-formules |
| `material_properties.json`   | Materiaal-database (warmtegeleidingscoëfficiënten) |
| `tables/`                    | Referentietabellen (JSON) gebruikt door `fk_calc.py` |
| `requirements.txt`           | Python-afhankelijkheden |
| `user_preferences.json`      | Automatisch gegenereerd – bevat uiterlijk-instellingen |

## Tabbladen

### 1. U-waarde Calculator

Berekent de warmtedoorgangscoëfficiënt (U-waarde) van een meerlaagse
bouwconstructie.

* Voeg constructielagen dynamisch toe of verwijder ze.
* Elke laag kan een materiaal uit de JSON-database gebruiken **of** een
  handmatig ingevoerde R-waarde (bijv. voor luchtspouwen).
* Categorieën omvatten beton, hout, isolatie, glas, deuren, vloeren, enz.
* De resultaattabel en U-waarde worden live bijgewerkt.
* Configuratie kan worden opgeslagen en geladen als JSON-bestand.

### 2. Correctiefactoren

Berekent warmteverlies-correctiefactoren op basis van de aangrenzende
situatie.  Zes scenario's worden ondersteund:

| # | Scenario | Uitvoerfactor |
|---|----------|---------------|
| 1 | Buitenlucht | f_k |
| 2 | Aangrenzend gebouw | f_ia,k |
| 3 | Verwarmde ruimte (zelfde woning) | f_ia,k |
| 4a | Onverwarmde ruimte – bekende temperatuur | f_k |
| 4b | Onverwarmde ruimte – onbekende temperatuur | f_k (Tabel 2.3 / 2.13) |
| 5 | Grond | f_ig,k · f_gw |

Dynamische invoervelden verschijnen op basis van het geselecteerde scenario.
Configuratie kan worden opgeslagen en geladen als JSON-bestand.

### 3. Instellingen

* **Thema wisselen** – schakelen tussen donker en licht modus
  (brandweer-kleurenpalet: oranje / rood / blauw).
* Voorkeuren worden automatisch opgeslagen in `user_preferences.json`.

## Een nieuw tabblad toevoegen

1. Maak een nieuw bestand in `app/`, bijv. `app/mijn_tool_tab.py`.
2. Definieer een `QWidget`-subklasse met de UI en logica van de tool.
3. Importeer het in `app/main_window.py` en voeg een tabblad toe:

   ```python
   from .mijn_tool_tab import MijnToolTab

   # in MainWindow.__init__:
   self.mijn_tool_tab = MijnToolTab(config)
   self.tabs.addTab(self.mijn_tool_tab, "Mijn Tool")
   ```

4. Als de tool persistente gegevens nodig heeft, laad/sla JSON-bestanden
   op vanuit de repository-root (zoals `material_properties.json`).

## Een nieuwe instelling toevoegen

1. Voeg een standaardwaarde toe in `config.py` → `_DEFAULTS` dictionary.
2. Voeg optioneel een getypte eigenschap toe aan de `Config` klasse.
3. Voeg een UI-besturingselement toe in `app/settings_tab.py` en koppel het
   aan `config.set(key, value)` + `config.save()`.

## Gegevensopslag

* **Referentietabellen** – alleen-lezen JSON-bestanden in `tables/`.
* **Materiaal-database** – `material_properties.json`.
* **Gebruikersvoorkeuren** – `user_preferences.json` (git-ignored).

## Afhankelijkheden

* Python ≥ 3.10
* PyQt5 ≥ 5.15

Installeer met:

```bash
pip install -r requirements.txt
```

## Standalone .exe

De applicatie kan als standalone Windows-executable worden gedistribueerd.
Zie [`../README.md`](../README.md) voor bouwinstructies.  In de gebouwde
versie worden `material_properties.json` en `tables/` automatisch
meegeleverd en worden gebruikersvoorkeuren opgeslagen naast de `.exe`.
