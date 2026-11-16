# -*- mode: python ; coding: utf-8 -*-
"""
==========================================================
SPESIFIKASI PEMAKETAN - AGRIUNO (PyInstaller)
==========================================================
Berkas ini mengatur proses pemaketan AgriUno menjadi satu berkas
eksekusi mandiri (AgriUno.exe) agar dapat dijalankan pengguna akhir
tanpa memasang Python.

Jalankan:

    pyinstaller AgriUno.spec

Hasil:
    dist/AgriUno.exe
"""
import os

# Akar proyek.
DASAR = os.path.abspath(os.getcwd())

block_assets = [
    (os.path.join(DASAR, "assets"), "assets"),
]

a = Analysis(
    ["main.py"],
    pathex=[DASAR],
    binaries=[],
    datas=block_assets,
    hiddenimports=[
        "customtkinter",
        "mysql.connector",
        "PIL.ImageTk",
        "PIL.Image",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter.test", "test", "unittest"],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="AgriUno",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(DASAR, "assets", "logo_agriuno.ico"),
)
