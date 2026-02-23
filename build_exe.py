"""build_exe.py – Build the Warmtetransmissie Rekentool as a standalone .exe.

Usage::

    python build_exe.py

Requirements:
    pip install pyinstaller

The resulting distributable folder is created at::

    dist/Warmtetransmissie Rekentool/
"""

import subprocess
import sys


def main() -> None:
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "warmtetransmissie.spec",
        "--noconfirm",
        "--clean",
    ]
    print("Building with:", " ".join(cmd))
    subprocess.check_call(cmd)
    print("\nDone!  Distributable folder: dist/Warmtetransmissie Rekentool/")


if __name__ == "__main__":
    main()
