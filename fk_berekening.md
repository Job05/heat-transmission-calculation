# Berekening van Correctiefactoren f_k en f_ig,k

> **Doel van dit document:** Volledig stappenplan voor de berekening van de correctiefactoren **f_k** (warmteverlies via onverwarmde ruimten) en **f_ig,k** (warmteverlies via de grond), inclusief de grondwaterfactor **f_gw**. Dit document is bedoeld als implementatiegids voor een automatische berekentool.

---

## Inhoudsopgave

### Algemeen
0. [Stap 0 – Keuze: f_k of f_ig,k?](#0-stap-0--keuze-fk-of-figk)

### Deel 1 – f_k (onverwarmde ruimte)
1. [Wat is f_k?](#1-wat-is-fk)
2. [Beslisboom f_k](#2-beslisboom-fk)
3. [Scenario A – Formule (θ_a bekend)](#3-scenario-a--formule-θa-bekend)
4. [Scenario B – Tabel 2.3 (θ_a onbekend, warmteverlies)](#4-scenario-b--tabel-23-θa-onbekend-warmteverlies)
5. [Scenario C – Tabel 2.13 (tijdconstante)](#5-scenario-c--tabel-213-tijdconstante)

### Deel 2 – f_ig,k + f_gw (grond)
6. [Wat is f_ig,k?](#6-wat-is-figk)
7. [Wat is f_gw?](#7-wat-is-fgw)
8. [Beslisboom f_ig,k](#8-beslisboom-figk)
9. [Scenario E – f_ig,k via formule](#9-scenario-e--figk-via-formule)
10. [Scenario F – U_equiv,k (grond, vereenvoudigd)](#10-scenario-f--uequivk-grond-vereenvoudigd)

### Hulptabellen (gedeeld)
11. [Hulptabel 2.12 – Temperatuurcorrecties Δθ](#11-hulptabel-212--temperatuurcorrecties-δθ)
12. [Hulptabel – Ontwerpbinnentemperaturen θ_i](#12-hulptabel--ontwerpbinnentemperaturen-θi)

### Implementatie
13. [Volledige beslisboom](#13-volledige-beslisboom)
14. [Invoervelden per scenario (UX-plan)](#14-invoervelden-per-scenario-ux-plan)
15. [Samenvatting van alle uitkomsten](#15-samenvatting-van-alle-uitkomsten)


---

## 0. Stap 0 – Keuze: f_k of f_ig,k?

Dit is de **eerste vraag** die de gebruiker beantwoordt. De keuze bepaalt welk berekeningspad gevolgd wordt.

| Keuze | Factor | Wanneer toepassen |
|-------|--------|-------------------|
| **f_k** | Correctiefactor onverwarmde ruimte | De constructie grenst aan een **onverwarmde ruimte** (kruipruimte, zolder, garage, kelder, gang, etc.) |
| **f_ig,k** | Correctiefactor grond | De constructie staat in **direct contact met de grond** (kelderbodem, begane grondvloer op grond, kelderMuur) |

> **Vuistregel:**
> - Ligt er grond aan de andere kant van de constructie? → **f_ig,k**
> - Ligt er een (niet-verwarmde) ruimte aan de andere kant? → **f_k**

---

# DEEL 1 – f_k (warmteverlies via onverwarmde ruimte)

---

## 1. Wat is f_k?

De correctiefactor **f_k** corrigeert het temperatuurverschil bij warmteverlies via een scheidingsconstructie die grenst aan een **onverwarmde ruimte** (in plaats van direct aan de buitenlucht).

- **f_k = 1,0** → aangrenzende ruimte gedraagt zich als buitenlucht (maximaal warmteverlies)
- **f_k = 0,0** → geen extra warmteverlies via die constructie
- f_k is dimensieloos: [-]

Toepassing in de warmteverliesberekening:

```
H_T,iue = A · U · f_k   [W/K]
```

---

## 2. Beslisboom f_k

```
Is de temperatuur van de aangrenzende ruimte (θ_a) bekend?
│
├── JA  → Scenario A: Bereken f_k via formule 2.22 / 2.23 / 2.24
│
└── NEE → Wat grenst de constructie aan?
          │
          ├── Onverwarmde ruimte (niet de grond)
          │    ├── Doel: warmteverliesberekening → Scenario B (Tabel 2.3)
          │    └── Doel: tijdconstante            → Scenario C (Tabel 2.13)
          │
          └── Grond → ga naar DEEL 2 (f_ig,k)
```

---

## 3. Scenario A – Formule (θ_a bekend)

Gebruik dit scenario wanneer de binnentemperatuur van de aangrenzende ruimte (**θ_a**) bekend is of berekend kan worden via een warmtebalans (bijlage E).

### Stap A1 – Invoer

| Variabele          | Omschrijving                                                  | Eenheid |
|--------------------|---------------------------------------------------------------|---------|
| `θ_i`             | Ontwerpbinnentemperatuur verwarmde vertrek (zie §12)          | [°C]    |
| `θ_e`             | Ontwerpbuitentemperatuur (standaard -10°C voor NL)            | [°C]    |
| `θ_a`             | Binnentemperatuur aangrenzende onverwarmde ruimte             | [°C]    |
| Bouwdeeltype       | Wand / Vloer / Plafond                                        | –       |
| Verwarmingssysteem | Alleen bij vloer of plafond (voor Δθ_1 / Δθ_2)               | –       |

### Stap A2 – Kies formule op basis van bouwdeeltype

#### Formule 2.22 – Wanden

```
f_k = (θ_i - θ_a) / (θ_i - θ_e)
```

#### Formule 2.23 – Vloeren

```
f_k = ((θ_i + Δθ_2) - θ_a) / (θ_i - θ_e)
```

> Δθ_2 uit Tabel 2.12 op basis van verwarmingssysteem (zie §11)

#### Formule 2.24 – Plafonds

```
f_k = ((θ_i + Δθ_1) - θ_a) / (θ_i - θ_e)
```

> Δθ_1 uit Tabel 2.12 op basis van verwarmingssysteem (zie §11)

### Stap A3 – Bepaal Δθ (indien van toepassing)

| Bouwdeel  | Δθ-kolom in Tabel 2.12 | Formule |
|-----------|------------------------|---------|
| Wand      | Niet van toepassing    | 2.22    |
| Vloer     | Δθ_2                   | 2.23    |
| Plafond   | Δθ_1                   | 2.24    |

### Stap A4 – Bereken f_k

Vul de waarden in. Resultaat is f_k [-].

### Stap A5 – Validatie

- f_k moet liggen tussen **0,0 en 1,0**
- f_k > 1,0 of f_k < 0,0 → controleer invoerwaarden

---

## 4. Scenario B – Tabel 2.3 (θ_a onbekend, warmteverlies)

Gebruik dit scenario voor de **warmteverliesberekening** als θ_a **niet bekend** is.

### Stap B1 – Bepaal type onverwarmde ruimte

Kies één van de vier categorieën hieronder.

---

#### Categorie 1: Vertrek / ruimte

**Benodigde invoer:**
- Aantal externe scheidingsconstructies (1 / 2 / 3+)
- Is er een buitendeur? (Ja / Nee) — alleen relevant bij 2 scheidingsconstructies

| Omschrijving                                                        | f_k |
|---------------------------------------------------------------------|-----|
| 1 externe scheidingsconstructie / buitenwand                        | 0,4 |
| 2 externe scheidingsconstructies – **zonder** buitendeur            | 0,5 |
| 2 externe scheidingsconstructies – **met** buitendeur               | 0,6 |
| 3 of meer externe scheidingsconstructies                            | 0,8 |

---

#### Categorie 2: Ruimte onder het dak

**Benodigde invoer:**
- Daktype en isolatiestatus

| Omschrijving                                                  | f_k |
|---------------------------------------------------------------|-----|
| Hoog infiltratievoud; bijv. pannendak **zonder** folielaag    | 1,0 |
| Overige **niet-geïsoleerde** daken                            | 0,9 |
| **Geïsoleerde** daken                                         | 0,7 |

---

#### Categorie 3: Gemeenschappelijke verkeersruimte

**Benodigde invoer:**
- Heeft de ruimte buitenwanden? (Ja / Nee)
- Ventilatievoud van de ruimte (< 0,5 of ≥ 0,5)
- Verhouding A_opening / V (indien relevant)

| Omschrijving                                                       | f_k |
|--------------------------------------------------------------------|-----|
| Interne ruimte **zonder** buitenwanden en ventilatievoud < 0,5     | 0,0 |
| Vrij geventileerd (A_opening / V > 0,005)                          | 1,0 |
| Overige gevallen                                                   | 0,5 |

---

#### Categorie 4: Vloer boven kruipruimte

**Benodigde invoer:**
- Openingsgrootte in de gevel van de kruipruimte [mm²/m²]

| Ventilatiegraad kruipruimte | Definitie                                     | f_k |
|-----------------------------|-----------------------------------------------|-----|
| **Zwak** geventileerd       | Openingen ≤ 1.000 mm²/m²                     | 0,6 |
| **Matig** geventileerd      | Openingen > 1.000 en ≤ 1.500 mm²/m²          | 0,8 |
| **Sterk** geventileerd      | Openingen > 1.500 mm²/m²                     | 1,0 |

---

### Stap B2 – Resultaat

De tabelwaarde is direct de **f_k** voor de warmteverliesberekening. Geen verdere berekening nodig.

---

## 5. Scenario C – Tabel 2.13 (tijdconstante)

Gebruik dit scenario **uitsluitend** bij het bepalen van de **tijdconstante** van een gebouw.

### Stap C1 – Bepaal type aangrenzende onverwarmde ruimte

### Stap C2 – Zoek f_k op in Tabel 2.13

| Aangrenzende onverwarmde ruimte         | f_k [-] |
|-----------------------------------------|---------|
| Kelder                                  | 0,5     |
| Stallingsruimte                         | 1,0     |
| Kruipruimte, serre, trappenhuis         | 0,8     |

### Stap C3 – Resultaat

De tabelwaarde is direct te gebruiken in de tijdconstante formule. Geen verdere berekening nodig.

---

# DEEL 2 – f_ig,k + f_gw (warmteverlies via de grond)

---

## 6. Wat is f_ig,k?

De correctiefactor **f_ig,k** is specifiek voor constructies die in **direct contact met de grond** staan. In plaats van de temperatuur van een aangrenzende ruimte (θ_a) wordt de **jaarlijks gemiddelde buitentemperatuur** (θ_me) als referentie gebruikt.

- **f_ig,k** is het grond-equivalent van f_k
- Voor Nederland geldt: **θ_me = 10,5°C**
- f_ig,k is dimensieloos: [-]

**Speciale regel:**
> f_ig,k = **0** voor het **verwarmde deel** van de wand/vloer/plafond bij wand- of vloerverwarming dat direct in contact staat met de grond. Dit deel levert juist warmte aan de grond en telt niet mee als verlies.

Toepassing in de warmteverliesberekening:

```
H_T,ig = A · U_equiv,k · f_ig,k · f_gw   [W/K]
```

---

## 7. Wat is f_gw?

De **grondwaterfactor f_gw** corrigeert voor de aanwezigheid van grondwater, dat de warmteoverdracht naar de bodem vergroot.

| Situatie                                          | f_gw  |
|---------------------------------------------------|-------|
| Grondwaterspiegel ≥ 1 m **onder** het vloerniveau | 1,00  |
| Overige gevallen (grondwater < 1 m onder vloer)   | 1,15  |

**Benodigde invoer:**
- Diepte grondwaterspiegel ten opzichte van het vloerniveau [m]
  - ≥ 1 m onder vloer → f_gw = 1,00
  - < 1 m onder vloer (of onbekend / worst-case) → f_gw = 1,15

---

## 8. Beslisboom f_ig,k

```
Is het bouwdeel verwarmde wand/vloer bij wand- of vloerverwarming IN CONTACT met grond?
│
├── JA  → f_ig,k = 0  (geen warmteverlies via dit deel)
│          Stop hier voor dit constructiedeel.
│
└── NEE → Bepaal f_ig,k via formule
           │
           ▼
          Bouwdeeltype?
           ├── Wand   → Formule 2.27
           └── Vloer  → Formule 2.28
                         (Bepaal eerst Δθ_2 via Tabel 2.12 – zie §11)
           │
           ▼
          Bepaal f_gw (zie §7)
           │
           ▼
          Eindresultaat: H_T,ig = A · U_equiv,k · f_ig,k · f_gw
```

> **Let op:** Plafonds komen niet voor in de f_ig,k berekening — plafonds staan niet in contact met de grond.

---

## 9. Scenario E – f_ig,k via formule

### Stap E1 – Invoer

| Variabele          | Omschrijving                                                        | Eenheid | Standaard NL |
|--------------------|---------------------------------------------------------------------|---------|--------------|
| `θ_i`             | Ontwerpbinnentemperatuur verwarmde vertrek (zie §12)                | [°C]    | –            |
| `θ_e`             | Ontwerpbuitentemperatuur                                            | [°C]    | -10          |
| `θ_me`            | Jaarlijks gemiddelde buitentemperatuur                              | [°C]    | **10,5**     |
| Bouwdeeltype       | Wand of Vloer                                                       | –       | –            |
| Verwarmingssysteem | Alleen bij vloer (voor Δθ_2)                                       | –       | –            |
| Grondwaterstand    | Diepte grondwaterspiegel t.o.v. vloerniveau                        | [m]     | –            |

### Stap E2 – Controleer de speciale regel

Wordt het bouwdeel direct verwarmd door **wand- of vloerverwarming** en staat het in contact met de grond?
- **Ja** → f_ig,k = **0** voor dat deel; stop hier.
- **Nee** → ga door naar Stap E3.

### Stap E3 – Kies formule op basis van bouwdeeltype

#### Formule 2.27 – Wanden

```
f_ig,k = (θ_i - θ_me) / (θ_i - θ_e)
```

Voorbeeld voor NL (θ_i = 22°C, θ_e = -10°C, θ_me = 10,5°C):

```
f_ig,k = (22 - 10,5) / (22 - (-10)) = 11,5 / 32 ≈ 0,36
```

#### Formule 2.28 – Vloeren

```
f_ig,k = ((θ_i + Δθ_2) - θ_me) / (θ_i - θ_e)
```

> Δθ_2 uit Tabel 2.12 op basis van verwarmingssysteem (zie §11)

### Stap E4 – Bepaal f_gw

Raadpleeg §7:
- Grondwater ≥ 1 m onder vloer → f_gw = 1,00
- Overig → f_gw = 1,15

### Stap E5 – Bereken eindwaarde

Combineer met U_equiv,k (zie §10) en de oppervlakte:

```
H_T,ig = A · U_equiv,k · f_ig,k · f_gw   [W/K]
```

### Stap E6 – Validatie

- f_ig,k ligt voor standaard NL-waarden doorgaans tussen **0,3 en 0,5**
- f_ig,k moet ≥ 0 zijn
- f_gw is altijd 1,00 of 1,15

---

## 10. Scenario F – U_equiv,k (grond, vereenvoudigd)

U_equiv,k is de equivalente warmtedoorgangscoëfficiënt voor constructies in contact met de grond.

> Bron: §2.7.4 – Specifiek warmteverlies naar de grond

### Stap F1 – Bepaal de R_c van de constructie in contact met de grond

### Stap F2 – Zoek U_equiv,k op

| R_c van de constructie       | U_equiv,k [W/(m²·K)] |
|------------------------------|-----------------------|
| R_c ≥ 5 m²·K/W              | 0,13                  |
| 3,5 ≤ R_c < 5 m²·K/W        | 0,18                  |
| 2,5 ≤ R_c < 3,5 m²·K/W      | 0,30                  |
| R_c < 2,5 m²·K/W            | 0,50                  |

### Stap F3 – Toepassing

U_equiv,k wordt gebruikt in combinatie met f_ig,k en f_gw (Stap E5).

```
H_T,ig = A · U_equiv,k · f_ig,k · f_gw   [W/K]
```

---

# DEEL 3 – Hulptabellen (gedeeld)

---

## 11. Hulptabel 2.12 – Temperatuurcorrecties Δθ

Gebruik deze tabel om **Δθ_1** (plafonds bij f_k) en **Δθ_2** (vloeren bij f_k én f_ig,k) te bepalen op basis van het verwarmingssysteem.

Van toepassing op ruimten met een maximale hoogte van 4 m.

| Verwarmingssysteem                                          | Δθ_1 [K] | Δθ_2 [K] |
|-------------------------------------------------------------|----------|----------|
| **Lokale verwarming**                                       |          |          |
| Gashaard, gevelkachel etc.                                  | +4       | -1       |
| IR-panelen wandmontage                                      | +1       | -0,5     |
| IR-panelen plafondmontage                                   | 0        | 0        |
| **Centrale verwarming in ruimten**                          |          |          |
| Radiatoren/convectoren Ht + luchtverwarming                 | +3       | -1       |
| Radiatoren/convectoren Lt                                   | +2       | -1       |
| Plafondverwarming                                           | +3       | 0        |
| Wandverwarming                                              | +2       | -1       |
| Plintverwarming                                             | +1       | 0        |
| Vloerverwarming + Ht-radiatoren/convectoren                 | +3       | 0        |
| Vloerverwarming + Lt-radiatoren/convectoren                 | +2       | -1       |
| Vloerverwarming (θ_vloer ≥ 27°C) als hoofdverwarming       | 0        | -1       |
| Vloerverwarming (θ_vloer < 27°C) als hoofdverwarming       | 0        | -0,5     |
| Vloerverwarming en wandverwarming                           | +1       | -1       |
| Ventilatorgedreven convectoren/radiatoren                   | +0,5     | 0        |

> **Gebruik:**
> - **Δθ_1** → plafonds in f_k (Formule 2.24)
> - **Δθ_2** → vloeren in f_k (Formule 2.23) én in f_ig,k (Formule 2.28)

---

## 12. Hulptabel – Ontwerpbinnentemperaturen θ_i

### Woonfunctie

| Ruimtetype                                                                   | θ_i [°C] |
|------------------------------------------------------------------------------|----------|
| Verblijfsruimte                                                              | 22       |
| Badruimte                                                                    | 22       |
| Verkeersruimte (hal, overloop, gang, trap)                                   | 20       |
| Toiletruimte                                                                 | 18       |
| Technische ruimte (niet zijnde stookruimte)                                  | 15       |
| Bergruimte                                                                   | 15       |
| Onbenoemde ruimte open verbinding met verkeersruimte (bijv. open zolder)     | 20       |
| Inpandige bergruimte (bijv. afgesloten zolder)                               | 15       |

### Seniorenwoningen en verzorgingstehuizen

| Ruimtetype          | θ_i [°C] |
|---------------------|----------|
| Verblijfsruimte     | 22       |
| Badruimte           | 22       |
| Toiletruimte        | 20       |
| Verkeersruimte      | 20       |
| Technische ruimte   | 15       |

### Standaard temperaturen voor Nederland

| Grootheid | Waarde     | Toelichting                              |
|-----------|-----------|------------------------------------------|
| θ_e       | -10 °C    | Ontwerpbuitentemperatuur                 |
| θ_me      | 10,5 °C   | Jaarlijks gemiddelde buitentemperatuur   |

---

# DEEL 4 – Implementatie

---

## 13. Volledige beslisboom

```
START
  │
  ▼
[Stap 0] Wat wil je berekenen?
  │
  ├── f_k  (onverwarmde ruimte)
  │     │
  │     ▼
  │   Is θ_a bekend?
  │     ├── JA  → Scenario A
  │     │           ├── Wand    → Formule 2.22: f_k = (θ_i - θ_a) / (θ_i - θ_e)
  │     │           ├── Vloer   → Δθ_2 via Tabel 2.12 → Formule 2.23
  │     │           └── Plafond → Δθ_1 via Tabel 2.12 → Formule 2.24
  │     │
  │     └── NEE → Doel?
  │                 ├── Warmteverlies → Scenario B (Tabel 2.3)
  │                 │     ├── Vertrek/ruimte            → Aantal gevels + buitendeur
  │                 │     ├── Ruimte onder dak          → Daktype / isolatie
  │                 │     ├── Gemeenschappelijke ruimte → Ventilatie
  │                 │     └── Vloer boven kruipruimte   → Openingsgrootte mm²/m²
  │                 │
  │                 └── Tijdconstante → Scenario C (Tabel 2.13)
  │                           ├── Kelder                          → 0,5
  │                           ├── Stallingsruimte                 → 1,0
  │                           └── Kruipruimte / serre / trappenhuis → 0,8
  │
  └── f_ig,k  (grond)
        │
        ▼
       Is het bouwdeel verwarmde wand/vloer bij wand-/vloerverwarming op grond?
        ├── JA  → f_ig,k = 0  (stop)
        │
        └── NEE → Scenario E
                   ├── Wand   → Formule 2.27: f_ig,k = (θ_i - θ_me) / (θ_i - θ_e)
                   └── Vloer  → Δθ_2 via Tabel 2.12
                                Formule 2.28: f_ig,k = ((θ_i + Δθ_2) - θ_me) / (θ_i - θ_e)
                   │
                   ▼
                  Bepaal f_gw (§7)
                   ├── Grondwater ≥ 1 m onder vloer → f_gw = 1,00
                   └── Overig                        → f_gw = 1,15
                   │
                   ▼
                  Bepaal U_equiv,k via R_c (Scenario F / §10)
                   │
                   ▼
                  H_T,ig = A · U_equiv,k · f_ig,k · f_gw
```

---

## 14. Invoervelden per scenario (UX-plan)

### 14.0 – Stap 0: Keuze berekeningstype (als eerste tonen)

| # | Veld            | Type           | Opties                                              |
|---|-----------------|----------------|-----------------------------------------------------|
| 0 | Berekeningstype | Toggle / Radio | **f_k** (onverwarmde ruimte) / **f_ig,k** (grond)  |

---

### 14.1 – Gemeenschappelijke invoer (beide berekeningen)

| # | Veld    | Type              | Opties / Eenheid                          | Standaard |
|---|---------|-------------------|-------------------------------------------|-----------|
| 1 | `θ_i`  | Getal of dropdown | [°C] of kies ruimtetype → auto-fill (§12) | –         |
| 2 | `θ_e`  | Getal             | [°C]                                      | -10       |

---

### 14.2 – Scenario A (f_k, θ_a bekend) – extra invoer

| # | Veld               | Type     | Opties / Eenheid                                   | Conditie              |
|---|--------------------|-----------|----------------------------------------------------|----------------------|
| 3 | `θ_a`             | Getal    | [°C]                                               | –                    |
| 4 | Bouwdeeltype       | Dropdown | Wand / Vloer / Plafond                             | –                    |
| 5 | Verwarmingssysteem | Dropdown | Lijst uit Tabel 2.12                               | Alleen bij vloer/plafond |

**Output:** f_k via Formule 2.22 / 2.23 / 2.24

---

### 14.3 – Scenario B (f_k, Tabel 2.3) – extra invoer

| #  | Veld                     | Type     | Opties                                              | Conditie                        |
|----|--------------------------|----------|-----------------------------------------------------|---------------------------------|
| 3  | Type onverwarmde ruimte  | Dropdown | Vertrek / Onder dak / Verkeersruimte / Kruipruimte  | –                               |
| 4a | Aantal externe gevels    | Dropdown | 1 / 2 / 3+                                          | Type = Vertrek                  |
| 4b | Buitendeur aanwezig?     | Toggle   | Ja / Nee                                            | Type = Vertrek, gevels = 2      |
| 4c | Daktype                  | Dropdown | Pannendak z. folie / Niet geïsol. / Geïsol.         | Type = Onder dak                |
| 4d | Buitenwanden aanwezig?   | Toggle   | Ja / Nee                                            | Type = Verkeersruimte           |
| 4e | Ventilatievoud           | Getal    | [-]                                                 | Type = Verkeersruimte           |
| 4f | A_opening / V            | Getal    | [-]                                                 | Type = Verkeersruimte           |
| 4g | Openingsgrootte gevel    | Getal of dropdown | [mm²/m²] of zwak / matig / sterk          | Type = Kruipruimte              |

**Output:** f_k als tabelwaarde uit Tabel 2.3

---

### 14.4 – Scenario C (f_k, Tabel 2.13) – extra invoer

| # | Veld                     | Type     | Opties                                                    |
|---|--------------------------|----------|-----------------------------------------------------------|
| 3 | Berekeningsdoel          | Toggle   | Warmteverlies / Tijdconstante                             |
| 4 | Type aangrenzende ruimte | Dropdown | Kelder / Stallingsruimte / Kruipruimte, serre, trappenhuis |

**Output:** f_k als tabelwaarde uit Tabel 2.13

---

### 14.5 – Scenario E (f_ig,k) – extra invoer

| # | Veld                               | Type     | Opties / Eenheid                                              | Standaard NL |
|---|------------------------------------|----------|---------------------------------------------------------------|--------------|
| 3 | `θ_me`                            | Getal    | [°C]                                                          | 10,5         |
| 4 | Bouwdeeltype                       | Dropdown | Wand / Vloer                                                  | –            |
| 5 | Verwarmingssysteem                 | Dropdown | Lijst uit Tabel 2.12                                          | Alleen bij vloer |
| 6 | Wand-/vloerverwarming op grond?    | Toggle   | Ja → f_ig,k = 0 / Nee → ga door                              | –            |
| 7 | Grondwaterstand t.o.v. vloerniveau | Dropdown | ≥ 1 m onder vloer (f_gw = 1,00) / Overig (f_gw = 1,15)      | –            |
| 8 | R_c constructie                    | Getal    | [m²·K/W] → leidt tot U_equiv,k                               | –            |

**Output:**
- f_ig,k [-] via Formule 2.27 of 2.28 (of 0 bij speciale regel)
- f_gw [-] → 1,00 of 1,15
- U_equiv,k [W/(m²·K)] op basis van R_c
- H_T,ig [W/K] indien oppervlakte A bekend is

---

## 15. Samenvatting van alle uitkomsten

| Scenario | Factor     | Methode                                   | Uitkomst / Bereik                        |
|----------|------------|-------------------------------------------|------------------------------------------|
| A        | f_k        | Formule 2.22 (wand)                       | Berekend, 0,0 – 1,0                      |
| A        | f_k        | Formule 2.23 (vloer)                      | Berekend, 0,0 – 1,0                      |
| A        | f_k        | Formule 2.24 (plafond)                    | Berekend, 0,0 – 1,0                      |
| B        | f_k        | Tabel 2.3                                 | 0,0 / 0,4 / 0,5 / 0,6 / 0,7 / 0,8 / 0,9 / 1,0 |
| C        | f_k        | Tabel 2.13                                | 0,5 / 0,8 / 1,0                          |
| E        | f_ig,k     | Formule 2.27 (wand, grond)                | Berekend, typisch 0,3 – 0,5              |
| E        | f_ig,k     | Formule 2.28 (vloer, grond)               | Berekend, typisch 0,3 – 0,5              |
| E        | f_ig,k     | Speciale regel (verwarmde wand/vloer op grond) | 0,0                                |
| E        | f_gw       | Grondwaterstand                           | 1,00 of 1,15                             |
| F        | U_equiv,k  | Tabel op basis van R_c                    | 0,13 / 0,18 / 0,30 / 0,50               |
