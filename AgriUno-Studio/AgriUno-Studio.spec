# -*- mode: python ; coding: utf-8 -*-
# Spesifikasi pemaketan AgriUno Edisi Studio.
# Jalankan: pyinstaller AgriUno-Studio.spec  ->  dist/AgriUnoStudio.exe
import os

DASAR = os.path.abspath(os.getcwd())

datas = [
    (os.path.join(DASAR, "assets"), "assets"),
    # Mesin MySQL bawaan: diekstrak aplikasi ke folder data pengguna
    # pada pemakaian pertama, sehingga exe ini berdiri sendiri.
    (os.path.join(DASAR, "runtime", "mysql", "bin"), "mysql/bin"),
    (os.path.join(DASAR, "runtime", "mysql", "share", "english"), "mysql/share/english"),
    (os.path.join(DASAR, "runtime", "mysql", "share", "charsets"), "mysql/share/charsets"),
    (os.path.join(DASAR, "database.sql"), "."),
]

a = Analysis(
    ["main.py"],
    pathex=[DASAR],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "customtkinter",
        "mysql.connector",
        # mysql-connector memuat terjemahan pesan galat secara dinamis,
        # sehingga harus disebut eksplisit agar ikut dipaketkan.
        "mysql.connector.locales",
        "mysql.connector.locales.eng",
        "mysql.connector.locales.eng.client_error",
        "mysql.connector.locales.eng.server_error",
        "PIL.ImageTk",
        "PIL.Image",
    ],
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
    name="AgriUnoStudio",
    debug=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    icon=os.path.join(DASAR, "assets", "logo_agriuno.ico"),
)
