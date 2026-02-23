# Warmtetransmissie Rekentool

Rekentools voor warmtetransmissiecoëfficiënten en correctiefactoren
voor bouwconstructies, gebaseerd op Nederlandse bouwregelgeving.

## Desktop applicatie

Een PyQt5-applicatie met donker/licht thema, bestaande uit:

* **U-waarde Calculator** – warmtedoorgangscoëfficiënt (meerlaagse constructie)
* **Correctiefactoren** – f_k, f_ia,k, f_ig,k
* **Instellingen** – thema wisselen en voorkeuren

## Snel starten (vanuit broncode)

```bash
pip install -r requirements.txt
python -m app
```

Zie [`app/README.md`](app/README.md) voor volledige documentatie over het
project en de tabbladen.

## Windows .exe bouwen

Je kunt een standalone Windows-executable maken met
[PyInstaller](https://pyinstaller.org):

```bash
pip install pyinstaller
python build_exe.py
```

Na het bouwen staat de distributie in:

```
dist/Warmtetransmissie Rekentool/
├── Warmtetransmissie Rekentool.exe
├── material_properties.json
├── tables/
│   └── ... (referentietabellen)
└── ... (Python runtime bestanden)
```

Kopieer de hele map **`dist/Warmtetransmissie Rekentool/`** naar de gewenste
locatie en start het programma door dubbelklikken op het `.exe`-bestand.
Gebruikersvoorkeuren worden automatisch opgeslagen als
`user_preferences.json` naast de executable.

## Een release maken

De repository bevat een GitHub Actions-workflow
(`.github/workflows/build-exe.yml`) die automatisch een Windows `.exe`
bouwt wanneer je een release publiceert.

### Stappen

1. Ga naar de repository op GitHub.
2. Klik op **Releases** → **Draft a new release**.
3. Maak een nieuwe tag aan, bijvoorbeeld `v1.0.0`.
4. Geef de release een titel (bijv. *Warmtetransmissie Rekentool v1.0.0*) en
   een beschrijving.
5. Klik op **Publish release**.
6. De workflow bouwt automatisch de `.exe` op een Windows-runner en voegt een
   zip-bestand (`Warmtetransmissie-Rekentool-Windows.zip`) toe aan de release.

Gebruikers kunnen het zip-bestand downloaden, uitpakken en het programma
direct starten – er is geen Python-installatie nodig.

> **Tip:** Je kunt de workflow ook handmatig starten via de **Actions**-tab →
> **Build Windows Executable** → **Run workflow** om een testbuild te maken
> zonder een release te publiceren. Het resultaat is dan beschikbaar als
> *artifact* op de workflow-run pagina.

## Projectstructuur

```
├── app/                     # PyQt5 desktop applicatie
│   ├── __init__.py
│   ├── __main__.py          # Startpunt (python -m app)
│   ├── main_window.py       # Hoofdvenster en thema-engine
│   ├── u_value_tab.py       # Tool 1 – U-waarde calculator
│   ├── fk_calc_tab.py       # Tool 2 – Correctiefactoren
│   ├── settings_tab.py      # Instellingen (thema, schaal)
│   ├── config.py            # Gebruikersvoorkeuren (JSON)
│   └── README.md            # Gedetailleerde app-documentatie
├── heat_calc.py             # Berekeningslogica U-waarde
├── fk_calc.py               # Correctiefactor-formules
├── material_properties.json # Materiaal-database (λ-waarden)
├── tables/                  # Referentietabellen (JSON)
├── test_fk_calc.py          # Pytest tests
├── requirements.txt         # Python afhankelijkheden
├── warmtetransmissie.spec   # PyInstaller spec-bestand
├── build_exe.py             # Bouwscript voor .exe
└── fk_berekening.md         # Wiskundige specificatie correctiefactoren
```

## Afhankelijkheden

* Python ≥ 3.10
* PyQt5 ≥ 5.15
* PyInstaller (alleen voor het bouwen van de `.exe`)

## Licentie

Zie de repository voor licentie-informatie.
