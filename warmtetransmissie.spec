# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Warmtetransmissie Rekentool.

Build with::

    pyinstaller warmtetransmissie.spec
"""

import os

_ROOT = os.path.dirname(os.path.abspath(SPECPATH))

a = Analysis(
    [os.path.join(_ROOT, "app", "__main__.py")],
    pathex=[_ROOT],
    datas=[
        (os.path.join(_ROOT, "material_properties.json"), "."),
        (os.path.join(_ROOT, "tables"), "tables"),
    ],
    hiddenimports=["heat_calc", "fk_calc"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Warmtetransmissie Rekentool",
    console=False,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="Warmtetransmissie Rekentool",
)
