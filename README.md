# heat-transmission-calculation

Tools for calculating heat-transmission coefficients and correction factors
for building constructions, based on Dutch building-code standards.

## Desktop application

A PyQt5 GUI with dark/light theme support, providing:

* **U-waarde Calculator** – multi-layer thermal transmittance (U-value)
* **Correctiefactoren** – correction factors f_k, f_ia,k, f_ig,k
* **Instellingen** – theme switching and preferences

```bash
pip install -r requirements.txt
python -m app
```

See [`app/README.md`](app/README.md) for full documentation.

## Jupyter Notebook

The original interactive tools are also available in
`heat-transmission-calculation.ipynb`.