# Berekening van Correctiefactoren f_k, f_ia,k en f_ig,k

> **Doel van dit document:** Volledig stappenplan voor de berekening van de correctiefactoren voor warmteverlies via verschillende aangrenzende situaties:
> - **f_k** – buitenlucht of onverwarmde ruimte
> - **f_ia,k** – aangrenzend gebouw of verwarmde ruimte (zelfde woning)
> - **f_ig,k** – grond (inclusief grondwaterfactor **f_gw**)
>
> Dit document is bedoeld als implementatiegids voor een automatische berekentool.

---

## Inhoudsopgave

### Stap 0 – Bepaal aangrenzende situatie
0. [Stap 0 – Keuze: wat grenst de constructie aan?](#0-stap-0--keuze-wat-grenst-de-constructie-aan)

### Deel 1 – Buitenlucht
1. [Buitenlucht – f_k = 1 / Formules 2.7 en 2.8](#1-buitenlucht--fk--1--formules-27-en-28)

### Deel 2 – Aangrenzend gebouw
2. [Gebouwen – f_ia,k via Formules 2.11, 2.12, 2.13](#2-gebouwen--fiak-via-formules-211-212-213)

### Deel 3 – Verwarmde ruimte (zelfde woning)
3. [Verwarmde ruimte – f_ia,k via Formules 2.17, 2.18, 2.19](#3-verwarmde-ruimte-zelfde-woning--fiak-via-formules-217-218-219)

### Deel 4 – Onverwarmde ruimte (zelfde woning)
4. [Onverwarmde ruimte – Bekende temperatuur (Formules 2.22, 2.23, 2.24)](#4-onverwarmde-ruimte-bekende-temperatuur--fk-via-formules-222-223-224)
5. [Onverwarmde ruimte – Onbekende temperatuur (Tabel 2.3 / 2.13)](#5-onverwarmde-ruimte-onbekende-temperatuur--fk-via-tabel-23--213)

### Deel 5 – Grond
6. [Grond – f_gw (grondwaterfactor)](#6-grond--fgw-grondwaterfactor)
7. [Grond – f_ig,k via Formules 2.27 en 2.28](#7-grond--figk-via-formules-227-en-228)

### Hulptabellen (gedeeld)
8. [Hulptabel 2.12 – Temperatuurcorrecties Δθ](#8-hulptabel-212--temperatuurcorrecties-δθ)
9. [Hulptabel – Ontwerpbinnentemperaturen θ_i](#9-hulptabel--ontwerpbinnentemperaturen-θi)

### Implementatie
10. [Volledige beslisboom](#10-volledige-beslisboom)
11. [Invoervelden per scenario (UX-plan)](#11-invoervelden-per-scenario-ux-plan)
12. [Samenvatting van alle uitkomsten](#12-samenvatting-van-alle-uitkomsten)

---

## 0. Stap 0 – Keuze: wat grenst de constructie aan?

Dit is de **eerste vraag** die de gebruiker beantwoordt. De keuze bepaalt welk berekeningspad gevolgd wordt.

| # | Aangrenzende situatie | Factor | Wanneer toepassen |
|---|----------------------|--------|-------------------|
| 1 | **Buitenlucht** | f_k | Constructie grenst direct aan de buitenlucht (buitenwand, schuin dak, vloer boven buitenlucht, plat dak) |
| 2 | **Aangrenzend gebouw** | f_ia,k | Constructie grenst aan een **ander** gebouw of woning (met bekende temperatuur θ_b) |
| 3 | **Verwarmde ruimte (zelfde woning)** | f_ia,k | Constructie scheidt twee **verwarmde** ruimten binnen dezelfde woning (bijv. vloer tussen verdiepingen) |
| 4 | **Onverwarmde ruimte (zelfde woning)** | f_k | Constructie grenst aan een **onverwarmde** ruimte (kruipruimte, zolder, garage, kelder, gang, etc.) |
| 5 | **Grond** | f_ig,k · f_gw | Constructie staat in **direct contact met de grond** (kelderbodem, begane grondvloer, kelderwand) |

> **Vuistregel:**
> - Ligt er grond aan de andere kant? → **f_ig,k** (Deel 5)
> - Ligt er een onverwarmde ruimte aan de andere kant? → **f_k** (Deel 4)
> - Ligt er een verwarmde ruimte (zelfde woning) aan de andere kant? → **f_ia,k** (Deel 3)
> - Ligt er een ander gebouw aan de andere kant? → **f_ia,k** (Deel 2)
> - Grenst de constructie direct aan buiten? → **f_k = 1** of formule (Deel 1)

---

# DEEL 1 – Buitenlucht

---

## 1. Buitenlucht – f_k = 1 / Formules 2.7 en 2.8

Constructies die **direct grenzen aan de buitenlucht** krijgen in principe f_k = 1. Bij vloeren boven buitenlucht en platte daken wordt een correctie toegepast voor temperatuurstratificatie.

### Speciale regel

> - **f_k = 0** voor het **verwarmde deel** van de wand/vloer bij wand-/vloerverwarming
> - **f_k = 1** voor buitenwanden en schuine daken

### Bouwdeeltype en formule

| Bouwdeel | Formule | Omschrijving |
|----------|---------|--------------|
| Buitenwand / schuin dak | – | f_k = 1 (geen correctie) |
| Vloer boven buitenlucht | 2.7 | Correctie via Δθ_2 |
| Plat dak | 2.8 | Correctie via Δθ_1 |

#### Formule 2.7 – Vloer boven buitenlucht

```
f_k = ((θ_i + Δθ_2) - θ_e) / (θ_i - θ_e)
```

> Δθ_2 uit Tabel 2.12 op basis van verwarmingssysteem (zie §8)

#### Formule 2.8 – Plat dak

```
f_k = ((θ_i + Δθ_1) - θ_e) / (θ_i - θ_e)
```

> Δθ_1 uit Tabel 2.12 op basis van verwarmingssysteem (zie §8)

### Invoervariabelen

| Variabele | Omschrijving | Eenheid | Standaard NL |
|-----------|--------------|---------|--------------|
| `θ_i` | Ontwerpbinnentemperatuur verwarmde vertrek (zie §9) | [°C] | – |
| `θ_e` | Ontwerpbuitentemperatuur | [°C] | -10 |
| `Δθ_1` | Temperatuurcorrectie t.g.v. temperatuurgelaagdheid (plafond) uit Tabel 2.12 | [K] | – |
| `Δθ_2` | Temperatuurcorrectie t.g.v. temperatuurgelaagdheid (vloer) uit Tabel 2.12 | [K] | – |

### Toepassing

```
H_T,ie = A · U · f_k   [W/K]
```

---

# DEEL 2 – Aangrenzend gebouw

---

## 2. Gebouwen – f_ia,k via Formules 2.11, 2.12, 2.13

Gebruik dit scenario wanneer de constructie grenst aan een **ander gebouw of woning** met een bekende (ontwerp-)binnentemperatuur **θ_b**.

### Speciale regel

> f_ia,k = **0** voor **verwarmde vlakken** (bijv. wand- of vloerverwarming aan de scheidingswand)

### Bouwdeeltype en formule

| Bouwdeel | Formule |
|----------|---------|
| Wand | 2.11 |
| Vloer (naar onderliggend vertrek) | 2.12 |
| Plafond (naar bovenliggend vertrek) | 2.13 |

#### Formule 2.11 – Wanden

```
f_ia,k = (θ_i - θ_b) / (θ_i - θ_e)
```

#### Formule 2.12 – Vloeren (naar onderliggend vertrek)

```
f_ia,k = ((θ_i + Δθ_2) - θ_b) / (θ_i - θ_e)
```

> Δθ_2 uit Tabel 2.12 op basis van verwarmingssysteem (zie §8)

#### Formule 2.13 – Plafonds (naar bovenliggend vertrek)

```
f_ia,k = ((θ_i + Δθ_1) - θ_b) / (θ_i - θ_e)
```

> Δθ_1 uit Tabel 2.12 op basis van verwarmingssysteem (zie §8)

### Invoervariabelen

| Variabele | Omschrijving | Eenheid | Standaard NL |
|-----------|--------------|---------|--------------|
| `θ_i` | Ontwerpbinnentemperatuur verwarmde vertrek (zie §9) | [°C] | – |
| `θ_e` | Ontwerpbuitentemperatuur | [°C] | -10 |
| `θ_b` | Temperatuur in het aangrenzende gebouw/woning | [°C] | – |
| `Δθ_1` | Temperatuurcorrectie t.g.v. temperatuurgelaagdheid (plafond) uit Tabel 2.12 | [K] | – |
| `Δθ_2` | Temperatuurcorrectie t.g.v. temperatuurgelaagdheid (vloer) uit Tabel 2.12 | [K] | – |

### Validatie

- f_ia,k moet liggen tussen **0,0 en 1,0**
- f_ia,k > 1,0 of f_ia,k < 0,0 → controleer invoerwaarden

### Toepassing

```
H_T,ia = A · U · f_ia,k   [W/K]
```

---

# DEEL 3 – Verwarmde ruimte (zelfde woning)

---

## 3. Verwarmde ruimte (zelfde woning) – f_ia,k via Formules 2.17, 2.18, 2.19

Gebruik dit scenario wanneer de constructie twee **verwarmde** vertrekken binnen **dezelfde woning** scheidt en de binnentemperatuur van het aangrenzende vertrek (**θ_a**) bekend is.

Bij vloeren en plafonds worden de temperatuurcorrecties van **beide** vertrekken meegenomen (Δθ van het eigen vertrek én van het aangrenzende vertrek).

### Speciale regel

> f_ia,k = **0** voor **verwarmde vlakken**. Dit geldt ook voor het plafond als in het bovenliggende vertrek **vloerverwarming** is toegepast.

### Bouwdeeltype en formule

| Bouwdeel | Formule |
|----------|---------|
| Wand | 2.17 |
| Vloer (naar onderliggend vertrek) | 2.18 |
| Plafond (naar bovenliggend vertrek) | 2.19 |

#### Formule 2.17 – Wanden

```
f_ia,k = (θ_i - θ_a) / (θ_i - θ_e)
```

#### Formule 2.18 – Vloeren (naar onderliggend vertrek)

```
f_ia,k = ((θ_i + Δθ_2) - (θ_a + Δθ_a1)) / (θ_i - θ_e)
```

#### Formule 2.19 – Plafonds (naar bovenliggend vertrek)

```
f_ia,k = ((θ_i + Δθ_1) - (θ_a + Δθ_a2)) / (θ_i - θ_e)
```

### Invoervariabelen

| Variabele | Omschrijving | Eenheid |
|-----------|--------------|---------|
| `θ_i` | Ontwerpbinnentemperatuur verwarmde vertrek (zie §9) | [°C] |
| `θ_e` | Ontwerpbuitentemperatuur | [°C] |
| `θ_a` | Ontwerpbinnentemperatuur aangrenzende verwarmde ruimte (zie §9) | [°C] |
| `Δθ_1` | Temperatuurcorrectie in **eigen** vertrek (plafond) uit Tabel 2.12 | [K] |
| `Δθ_2` | Temperatuurcorrectie in **eigen** vertrek (vloer) uit Tabel 2.12 | [K] |
| `Δθ_a1` | Temperatuurcorrectie in het **aangrenzende** vertrek (bovenkant) uit Tabel 2.12 | [K] |
| `Δθ_a2` | Temperatuurcorrectie in het **aangrenzende** vertrek (onderkant) uit Tabel 2.12 | [K] |

### Validatie

- f_ia,k moet liggen tussen **0,0 en 1,0**
- f_ia,k > 1,0 of f_ia,k < 0,0 → controleer invoerwaarden

### Toepassing

```
H_T,ia = A · U · f_ia,k   [W/K]
```

---

# DEEL 4 – Onverwarmde ruimte (zelfde woning)

---

## 4. Onverwarmde ruimte – Bekende temperatuur – f_k via Formules 2.22, 2.23, 2.24

Gebruik dit scenario wanneer de binnentemperatuur van de aangrenzende **onverwarmde** ruimte (**θ_a**) bekend is of berekend kan worden via een warmtebalans (bijlage E).

### Speciale regel

> f_k = **0** voor het **verwarmde deel** van de wand/vloer bij wand-/vloerverwarming

### Bouwdeeltype en formule

| Bouwdeel | Formule |
|----------|---------|
| Wand | 2.22 |
| Vloer | 2.23 |
| Plafond | 2.24 |

#### Formule 2.22 – Wanden

```
f_k = (θ_i - θ_a) / (θ_i - θ_e)
```

#### Formule 2.23 – Vloeren

```
f_k = ((θ_i + Δθ_2) - θ_a) / (θ_i - θ_e)
```

> Δθ_2 uit Tabel 2.12 op basis van verwarmingssysteem (zie §8)

#### Formule 2.24 – Plafonds

```
f_k = ((θ_i + Δθ_1) - θ_a) / (θ_i - θ_e)
```

> Δθ_1 uit Tabel 2.12 op basis van verwarmingssysteem (zie §8)

### Invoervariabelen

| Variabele | Omschrijving | Eenheid | Standaard NL |
|-----------|--------------|---------|--------------|
| `θ_i` | Ontwerpbinnentemperatuur verwarmde vertrek (zie §9) | [°C] | – |
| `θ_e` | Ontwerpbuitentemperatuur | [°C] | -10 |
| `θ_a` | Ontwerpbinnentemperatuur aangrenzende onverwarmde ruimte | [°C] | – |
| `Δθ_1` | Temperatuurcorrectie (plafond) uit Tabel 2.12 | [K] | – |
| `Δθ_2` | Temperatuurcorrectie (vloer) uit Tabel 2.12 | [K] | – |
| Verwarmingssysteem | Alleen bij vloer of plafond (voor Δθ_1 / Δθ_2) | – | – |

### Validatie

- f_k moet liggen tussen **0,0 en 1,0**
- f_k > 1,0 of f_k < 0,0 → controleer invoerwaarden

### Toepassing

```
H_T,iue = A · U · f_k   [W/K]
```

---

## 5. Onverwarmde ruimte – Onbekende temperatuur – f_k via Tabel 2.3 / 2.13

Gebruik dit scenario wanneer de temperatuur van de aangrenzende onverwarmde ruimte **niet bekend** is.

### 5.1 – Warmteverliesberekening: Tabel 2.3

#### Categorie 1: Vertrek / ruimte

**Benodigde invoer:**
- Aantal externe scheidingsconstructies (1 / 2 / 3+)
- Is er een buitendeur? (Ja / Nee) — alleen relevant bij 2 scheidingsconstructies

| Omschrijving | f_k |
|--------------|-----|
| 1 externe scheidingsconstructie / buitenwand | 0,4 |
| 2 externe scheidingsconstructies – **zonder** buitendeur | 0,5 |
| 2 externe scheidingsconstructies – **met** buitendeur | 0,6 |
| 3 of meer externe scheidingsconstructies | 0,8 |

---

#### Categorie 2: Ruimte onder het dak

**Benodigde invoer:**
- Daktype en isolatiestatus

| Omschrijving | f_k |
|--------------|-----|
| Hoog infiltratievoud; bijv. pannendak **zonder** folielaag | 1,0 |
| Overige **niet-geïsoleerde** daken | 0,9 |
| **Geïsoleerde** daken | 0,7 |

---

#### Categorie 3: Gemeenschappelijke verkeersruimte

**Benodigde invoer:**
- Heeft de ruimte buitenwanden? (Ja / Nee)
- Ventilatievoud van de ruimte (< 0,5 of ≥ 0,5)
- Verhouding A_opening / V (indien relevant)

| Omschrijving | f_k |
|--------------|-----|
| Interne ruimte **zonder** buitenwanden en ventilatievoud < 0,5 | 0,0 |
| Vrij geventileerd (A_opening / V > 0,005) | 1,0 |
| Overige gevallen | 0,5 |

---

#### Categorie 4: Vloer boven kruipruimte

**Benodigde invoer:**
- Openingsgrootte in de gevel van de kruipruimte [mm²/m²]

| Ventilatiegraad kruipruimte | Definitie | f_k |
|-----------------------------|-----------|-----|
| **Zwak** geventileerd | Openingen ≤ 1.000 mm²/m² | 0,6 |
| **Matig** geventileerd | Openingen > 1.000 en ≤ 1.500 mm²/m² | 0,8 |
| **Sterk** geventileerd | Openingen > 1.500 mm²/m² | 1,0 |

De tabelwaarde is direct de **f_k** voor de warmteverliesberekening. Geen verdere berekening nodig.

---

### 5.2 – Tijdconstante: Tabel 2.13

Gebruik dit scenario **uitsluitend** bij het bepalen van de **tijdconstante** van een gebouw.

| Aangrenzende onverwarmde ruimte | f_k [-] |
|---------------------------------|---------|
| Kelder | 0,5 |
| Stallingsruimte | 1,0 |
| Kruipruimte, serre, trappenhuis | 0,8 |

De tabelwaarde is direct te gebruiken in de tijdconstante formule. Geen verdere berekening nodig.

---

# DEEL 5 – Grond

---

## 6. Grond – f_gw (grondwaterfactor)

De **grondwaterfactor f_gw** corrigeert voor de aanwezigheid van grondwater, dat de warmteoverdracht naar de bodem vergroot.

**Benodigde invoer:**
- Diepte grondwaterspiegel ten opzichte van het vloerniveau [m]

| Situatie | f_gw |
|----------|------|
| Grondwaterspiegel **≥ 1 m** onder het vloerniveau | 1,00 |
| Overige gevallen (grondwater < 1 m onder vloer of onbekend) | 1,15 |

---

## 7. Grond – f_ig,k via Formules 2.27 en 2.28

De correctiefactor **f_ig,k** is specifiek voor constructies die in **direct contact met de grond** staan. In plaats van de buitentemperatuur (θ_e) wordt de **jaarlijks gemiddelde buitentemperatuur** (θ_me) als referentie gebruikt.

- Voor Nederland geldt: **θ_me = 10,5°C**
- f_ig,k is dimensieloos: [-]

### Speciale regel

> f_ig,k = **0** voor het **verwarmde deel** van de wand/vloer/plafond bij wand-/vloer-/plafondverwarming dat direct in contact staat met de grond. Dit deel levert warmte aan de grond en telt niet mee als verlies.

### Bouwdeeltype en formule

| Bouwdeel | Formule |
|----------|---------|
| Wand | 2.27 |
| Vloer | 2.28 |

> **Let op:** Plafonds komen niet voor in de f_ig,k berekening — plafonds staan niet in contact met de grond.

#### Formule 2.27 – Wanden

```
f_ig,k = (θ_i - θ_me) / (θ_i - θ_e)
```

#### Formule 2.28 – Vloeren

```
f_ig,k = ((θ_i + Δθ_2) - θ_me) / (θ_i - θ_e)
```

> Δθ_2 uit Tabel 2.12 op basis van verwarmingssysteem (zie §8)

### Invoervariabelen

| Variabele | Omschrijving | Eenheid | Standaard NL |
|-----------|--------------|---------|--------------|
| `θ_i` | Ontwerpbinnentemperatuur verwarmde vertrek (zie §9) | [°C] | – |
| `θ_e` | Ontwerpbuitentemperatuur | [°C] | -10 |
| `θ_me` | Jaarlijks gemiddelde buitentemperatuur | [°C] | **10,5** |
| `Δθ_2` | Temperatuurcorrectie (vloer) uit Tabel 2.12 | [K] | – |
| Verwarmingssysteem | Alleen bij vloer (voor Δθ_2) | – | – |

### Validatie

- f_ig,k ligt voor standaard NL-waarden doorgaans tussen **0,3 en 0,5**
- f_ig,k moet ≥ 0 zijn

### U_equiv,k – Equivalente warmtedoorgangscoëfficiënt (grond)

U_equiv,k wordt bepaald op basis van de R_c waarde van de constructie in contact met de grond:

| R_c van de constructie | U_equiv,k [W/(m²·K)] |
|------------------------|----------------------|
| R_c ≥ 5 m²·K/W | 0,13 |
| 3,5 ≤ R_c < 5 m²·K/W | 0,18 |
| 2,5 ≤ R_c < 3,5 m²·K/W | 0,30 |
| R_c < 2,5 m²·K/W | 0,50 |

### Toepassing

```
H_T,ig = A · U_equiv,k · f_ig,k · f_gw   [W/K]
```

Voorbeeld voor NL (wand, θ_i = 22°C, θ_e = -10°C, θ_me = 10,5°C):

```
f_ig,k = (22 - 10,5) / (22 - (-10)) = 11,5 / 32 ≈ 0,36
```

---

# DEEL 6 – Hulptabellen (gedeeld)

---

## 8. Hulptabel 2.12 – Temperatuurcorrecties Δθ

Gebruik deze tabel om **Δθ_1** en **Δθ_2** te bepalen op basis van het verwarmingssysteem.
Van toepassing op ruimten met een maximale hoogte van 4 m.

| Verwarmingssysteem | Δθ_1 [K] | Δθ_2 [K] |
|--------------------|----------|----------|
| **Lokale verwarming** | | |
| Gashaard, gevelkachel etc. | +4 | -1 |
| IR-panelen wandmontage | +1 | -0,5 |
| IR-panelen plafondmontage | 0 | 0 |
| **Centrale verwarming in ruimten** | | |
| Radiatoren/convectoren Ht + luchtverwarming | +3 | -1 |
| Radiatoren/convectoren Lt | +2 | -1 |
| Plafondverwarming | +3 | 0 |
| Wandverwarming | +2 | -1 |
| Plintverwarming | +1 | 0 |
| Vloerverwarming + Ht-radiatoren/convectoren | +3 | 0 |
| Vloerverwarming + Lt-radiatoren/convectoren | +2 | -1 |
| Vloerverwarming (θ_vloer ≥ 27°C) als hoofdverwarming | 0 | -1 |
| Vloerverwarming (θ_vloer < 27°C) als hoofdverwarming | 0 | -0,5 |
| Vloerverwarming en wandverwarming | +1 | -1 |
| Ventilatorgedreven convectoren/radiatoren | +0,5 | 0 |

> **Gebruik:**
> - **Δθ_1** → plafonds (Formules 2.8, 2.13, 2.19, 2.24)
> - **Δθ_2** → vloeren (Formules 2.7, 2.12, 2.18, 2.23, 2.28)

---

## 9. Hulptabel – Ontwerpbinnentemperaturen θ_i

### Woonfunctie

| Ruimtetype | θ_i [°C] |
|------------|----------|
| Verblijfsruimte | 22 |
| Badruimte | 22 |
| Verkeersruimte (hal, overloop, gang, trap) | 20 |
| Toiletruimte | 18 |
| Technische ruimte (niet zijnde stookruimte) | 15 |
| Bergruimte | 15 |
| Onbenoemde ruimte open verbinding met verkeersruimte (bijv. open zolder) | 20 |
| Inpandige bergruimte (bijv. afgesloten zolder) | 15 |

### Seniorenwoningen en verzorgingstehuizen

| Ruimtetype | θ_i [°C] |
|------------|----------|
| Verblijfsruimte | 22 |
| Badruimte | 22 |
| Toiletruimte | 20 |
| Verkeersruimte | 20 |
| Technische ruimte | 15 |

### Standaard temperaturen voor Nederland

| Grootheid | Waarde | Toelichting |
|-----------|--------|-------------|
| θ_e | -10 °C | Ontwerpbuitentemperatuur |
| θ_me | 10,5 °C | Jaarlijks gemiddelde buitentemperatuur (voor grondberekeningen) |

---

# DEEL 7 – Implementatie

---

## 10. Volledige beslisboom

```
START
  │
  ▼
[Stap 0] Wat grenst de constructie aan?
  │
  ├─ 1. BUITENLUCHT
  │       ├── Buitenwand / schuin dak     → f_k = 1
  │       ├── Vloer boven buitenlucht     → Δθ_2 via Tabel 2.12 → Formule 2.7
  │       └── Plat dak                    → Δθ_1 via Tabel 2.12 → Formule 2.8
  │
  ├─ 2. AANGRENZEND GEBOUW (θ_b bekend)
  │       ├── Wand    → Formule 2.11: f_ia,k = (θ_i - θ_b) / (θ_i - θ_e)
  │       ├── Vloer   → Δθ_2 via Tabel 2.12 → Formule 2.12
  │       └── Plafond → Δθ_1 via Tabel 2.12 → Formule 2.13
  │
  ├─ 3. VERWARMDE RUIMTE – zelfde woning (θ_a bekend)
  │       ├── Wand    → Formule 2.17: f_ia,k = (θ_i - θ_a) / (θ_i - θ_e)
  │       ├── Vloer   → Δθ_2 (eigen) + Δθ_a1 (aangrenzend) → Formule 2.18
  │       └── Plafond → Δθ_1 (eigen) + Δθ_a2 (aangrenzend) → Formule 2.19
  │
  ├─ 4. ONVERWARMDE RUIMTE – zelfde woning
  │       ├── θ_a BEKEND
  │       │     ├── Wand    → Formule 2.22: f_k = (θ_i - θ_a) / (θ_i - θ_e)
  │       │     ├── Vloer   → Δθ_2 via Tabel 2.12 → Formule 2.23
  │       │     └── Plafond → Δθ_1 via Tabel 2.12 → Formule 2.24
  │       │
  │       └── θ_a ONBEKEND
  │             ├── Warmteverlies → Tabel 2.3
  │             │     ├── Vertrek/ruimte          → Aantal gevels + buitendeur
  │             │     ├── Ruimte onder dak        → Daktype / isolatie
  │             │     ├── Verkeersruimte          → Ventilatie
  │             │     └── Vloer boven kruipruimte → Openingsgrootte [mm²/m²]
  │             │
  │             └── Tijdconstante → Tabel 2.13
  │                   ├── Kelder                            → 0,5
  │                   ├── Stallingsruimte                   → 1,0
  │                   └── Kruipruimte / serre / trappenhuis → 0,8
  │
  └─ 5. GROND
          │
          ├── Is het bouwdeel verwarmde wand/vloer bij wand-/vloerverwarming op grond?
          │     └── JA → f_ig,k = 0 (stop)
          │
          ├── Bepaal f_gw (§6)
          │     ├── Grondwater ≥ 1 m onder vloer → f_gw = 1,00
          │     └── Overig                        → f_gw = 1,15
          │
          ├── Bepaal f_ig,k
          │     ├── Wand  → Formule 2.27: f_ig,k = (θ_i - θ_me) / (θ_i - θ_e)
          │     └── Vloer → Δθ_2 via Tabel 2.12 → Formule 2.28
          │
          ├── Bepaal U_equiv,k via R_c (§7)
          │
          └── H_T,ig = A · U_equiv,k · f_ig,k · f_gw
```

---

## 11. Invoervelden per scenario (UX-plan)

### 11.0 – Stap 0: Keuze aangrenzende situatie (als eerste tonen)

| # | Veld | Type | Opties |
|---|------|------|--------|
| 0 | Aangrenzende situatie | Radio / Dropdown | Buitenlucht / Aangrenzend gebouw / Verwarmde ruimte (zelfde woning) / Onverwarmde ruimte / Grond |

---

### 11.1 – Gemeenschappelijke invoer (alle scenario's)

| # | Veld | Type | Eenheid | Standaard |
|---|------|------|---------|-----------|
| 1 | `θ_i` | Getal of dropdown | [°C] of kies ruimtetype → auto-fill (§9) | – |
| 2 | `θ_e` | Getal | [°C] | -10 |

---

### 11.2 – Buitenlucht – extra invoer

| # | Veld | Type | Opties / Eenheid | Conditie |
|---|------|------|------------------|----------|
| 3 | Bouwdeeltype | Dropdown | Buitenwand / Schuin dak / Vloer boven buitenlucht / Plat dak | – |
| 4 | Verwarmingssysteem | Dropdown | Lijst uit Tabel 2.12 | Alleen vloer / dak |

**Output:** f_k = 1 (wand / schuin dak) of via Formule 2.7 / 2.8

---

### 11.3 – Aangrenzend gebouw – extra invoer

| # | Veld | Type | Eenheid | Conditie |
|---|------|------|---------|----------|
| 3 | `θ_b` | Getal | [°C] | – |
| 4 | Bouwdeeltype | Dropdown | Wand / Vloer / Plafond | – |
| 5 | Verwarmingssysteem | Dropdown | Lijst uit Tabel 2.12 | Alleen vloer / plafond |

**Output:** f_ia,k via Formule 2.11 / 2.12 / 2.13

---

### 11.4 – Verwarmde ruimte (zelfde woning) – extra invoer

| # | Veld | Type | Eenheid | Conditie |
|---|------|------|---------|----------|
| 3 | `θ_a` | Getal of dropdown | [°C] of kies ruimtetype → auto-fill (§9) | – |
| 4 | Bouwdeeltype | Dropdown | Wand / Vloer / Plafond | – |
| 5 | Verwarmingssysteem (eigen vertrek) | Dropdown | Lijst uit Tabel 2.12 | Alleen vloer / plafond |
| 6 | Verwarmingssysteem (aangrenzend vertrek) | Dropdown | Lijst uit Tabel 2.12 | Alleen vloer / plafond |

**Output:** f_ia,k via Formule 2.17 / 2.18 / 2.19

---

### 11.5 – Onverwarmde ruimte – Bekende temperatuur – extra invoer

| # | Veld | Type | Eenheid | Conditie |
|---|------|------|---------|----------|
| 3 | `θ_a` | Getal | [°C] | – |
| 4 | Bouwdeeltype | Dropdown | Wand / Vloer / Plafond | – |
| 5 | Verwarmingssysteem | Dropdown | Lijst uit Tabel 2.12 | Alleen vloer / plafond |

**Output:** f_k via Formule 2.22 / 2.23 / 2.24

---

### 11.6 – Onverwarmde ruimte – Onbekende temperatuur – extra invoer

| # | Veld | Type | Opties | Conditie |
|---|------|------|--------|----------|
| 3 | Berekeningsdoel | Toggle | Warmteverlies / Tijdconstante | – |
| 4 | Type onverwarmde ruimte | Dropdown | Vertrek / Onder dak / Verkeersruimte / Kruipruimte | Warmteverlies |
| 4a | Aantal externe gevels | Dropdown | 1 / 2 / 3+ | Type = Vertrek |
| 4b | Buitendeur aanwezig? | Toggle | Ja / Nee | Type = Vertrek, gevels = 2 |
| 4c | Daktype | Dropdown | Pannendak z. folie / Niet geïsol. / Geïsol. | Type = Onder dak |
| 4d | Buitenwanden aanwezig? | Toggle | Ja / Nee | Type = Verkeersruimte |
| 4e | Ventilatievoud | Getal | [-] | Type = Verkeersruimte |
| 4f | A_opening / V | Getal | [-] | Type = Verkeersruimte |
| 4g | Openingsgrootte gevel | Getal of dropdown | [mm²/m²] | Type = Kruipruimte |
| 4h | Type aangrenzende ruimte | Dropdown | Kelder / Stallingsruimte / Kruipruimte, serre, trappenhuis | Tijdconstante |

**Output:** f_k als tabelwaarde uit Tabel 2.3 of Tabel 2.13

---

### 11.7 – Grond – extra invoer

| # | Veld | Type | Opties / Eenheid | Standaard NL |
|---|------|------|------------------|--------------|
| 3 | `θ_me` | Getal | [°C] | 10,5 |
| 4 | Wand-/vloerverwarming op grond? | Toggle | Ja → f_ig,k = 0 / Nee → ga door | – |
| 5 | Bouwdeeltype | Dropdown | Wand / Vloer | – |
| 6 | Verwarmingssysteem | Dropdown | Lijst uit Tabel 2.12 | Alleen vloer |
| 7 | Grondwaterstand t.o.v. vloerniveau | Dropdown | ≥ 1 m onder vloer (f_gw = 1,00) / Overig (f_gw = 1,15) | – |
| 8 | R_c constructie | Getal | [m²·K/W] → leidt tot U_equiv,k | – |

**Output:**
- f_ig,k [-] via Formule 2.27 of 2.28 (of 0 bij speciale regel)
- f_gw [-] → 1,00 of 1,15
- U_equiv,k [W/(m²·K)] op basis van R_c
- H_T,ig [W/K] indien oppervlakte A bekend is

---

## 12. Samenvatting van alle uitkomsten

| Situatie | Factor | Formule / Methode | Bouwdeel | Uitkomst / Bereik |
|----------|--------|-------------------|----------|-------------------|
| Buitenlucht | f_k = 1 | – | Wand / Schuin dak | 1,0 |
| Buitenlucht | f_k | Formule 2.7 | Vloer boven buitenlucht | Berekend |
| Buitenlucht | f_k | Formule 2.8 | Plat dak | Berekend |
| Aangrenzend gebouw | f_ia,k | Formule 2.11 | Wand | 0,0 – 1,0 |
| Aangrenzend gebouw | f_ia,k | Formule 2.12 | Vloer | 0,0 – 1,0 |
| Aangrenzend gebouw | f_ia,k | Formule 2.13 | Plafond | 0,0 – 1,0 |
| Verwarmde ruimte (zelfde woning) | f_ia,k | Formule 2.17 | Wand | 0,0 – 1,0 |
| Verwarmde ruimte (zelfde woning) | f_ia,k | Formule 2.18 | Vloer | 0,0 – 1,0 |
| Verwarmde ruimte (zelfde woning) | f_ia,k | Formule 2.19 | Plafond | 0,0 – 1,0 |
| Onverwarmde ruimte – bekende temp | f_k | Formule 2.22 | Wand | 0,0 – 1,0 |
| Onverwarmde ruimte – bekende temp | f_k | Formule 2.23 | Vloer | 0,0 – 1,0 |
| Onverwarmde ruimte – bekende temp | f_k | Formule 2.24 | Plafond | 0,0 – 1,0 |
| Onverwarmde ruimte – onbekende temp | f_k | Tabel 2.3 | – | 0,0 / 0,4 – 1,0 |
| Onverwarmde ruimte – tijdconstante | f_k | Tabel 2.13 | – | 0,5 / 0,8 / 1,0 |
| Grond | f_ig,k | Formule 2.27 | Wand | 0,0 – 1,0 (typisch 0,3–0,5) |
| Grond | f_ig,k | Formule 2.28 | Vloer | 0,0 – 1,0 (typisch 0,3–0,5) |
| Grond | f_ig,k | Speciale regel | Wand/vloer bij vloerverw. | 0,0 |
| Grond | f_gw | Grondwaterstand | – | 1,00 of 1,15 |
| Grond | U_equiv,k | Tabel op basis van R_c | – | 0,13 / 0,18 / 0,30 / 0,50 |
