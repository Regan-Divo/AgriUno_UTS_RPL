"""
==========================================================
KONSTANTA APLIKASI - AGRIUNO
Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal
==========================================================
Pusat konfigurasi yang tidak bergantung pada basis data.
Seluruh nilai yang dipakai bersama (warna merek, nama berkas
aset, daftar peran pengguna) dikumpulkan di sini agar mudah
diaudit dan tidak tersebar di seluruh berkas.

Praktikum : Rekayasa Perangkat Lunak (UAS) 2026
DBMS      : MySQL 8.0 (Laragon)
"""

import os
import sys

# ------------------------------------------------------------
# 1. IDENTITAS APLIKASI
# ------------------------------------------------------------
APP_NAME = "AgriUno"
APP_TAGLINE = "Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal"
APP_VERSION = "2.0.0"
APP_RELEASE = "UAS RPL 2026"

# ------------------------------------------------------------
# 2. PALET WARNA (BRAND)
# ------------------------------------------------------------
COLOR_PRIMARY = "#1b4332"  # Hijau tua - sidebar, judul utama
COLOR_PRIMARY_HOVER = "#2d6a4f"  # Hijau terang - hover
COLOR_ACCENT = "#d97706"  # Oranye - kartu panen / tombol Ubah
COLOR_ACCENT_HOVER = "#b45309"
COLOR_DANGER = "#dc2626"  # Merah - tombol Hapus / Keluar
COLOR_DANGER_HOVER = "#b91c1c"
COLOR_INFO = "#1d4ed8"  # Biru - kartu petani
COLOR_BG = "#f8f9fa"  # Latar konten
COLOR_SURFACE = "#ffffff"  # Latar kartu/panel
COLOR_TEXT = "#1f2937"
COLOR_MUTED = "#6b7280"
COLOR_BORDER = "#d1d5db"

FONT_FAMILY = "Segoe UI"

# ------------------------------------------------------------
# 3. UKURAN JENDELA
# ------------------------------------------------------------
WIN_MAIN = (1280, 740)
WIN_LOGIN = (980, 620)
WIN_REGISTER = (980, 690)
WIN_SPLASH = (520, 480)

# ------------------------------------------------------------
# 4. ASET
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def akar_aset():
    """Mengembalikan akar folder aset.

    Saat aplikasi dijalankan dari berkas .exe (PyInstaller), aset
    diekstrak ke folder sementara sehingga penanamannya harus
    mengikuti ``sys._MEIPASS``.
    """
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return BASE_DIR


ASSETS_DIR = os.path.join(akar_aset(), "assets")
ANIM_DIR = os.path.join(ASSETS_DIR, "anim")
LOGO_EMBLEM = os.path.join(ASSETS_DIR, "logo_agriuno.png")
LOGO_WORDMARK = os.path.join(ASSETS_DIR, "logo_agriuno_wordmark.png")
LOGO_WORDMARK_SMALL = os.path.join(ASSETS_DIR, "logo_agriuno_wordmark_small.png")
LOGO_ICON = os.path.join(ASSETS_DIR, "logo_agriuno.ico")


# ------------------------------------------------------------
# 5. PERAN PENGGUNA (RBAC) - BR-06 s.d. BR-08
# ------------------------------------------------------------
ROLE_ADMIN = "admin"
ROLE_OPERATOR = "operator"
ROLE_PETANI = "petani"

#: Seluruh peran yang dikenali oleh sistem.
ALL_ROLES = (ROLE_ADMIN, ROLE_OPERATOR, ROLE_PETANI)

#: Peran yang boleh dipilih sendiri oleh pengguna saat Registrasi.
#: Peran 'admin' TIDAK dapat didaftarkan sendiri (hanya dibuat oleh DBA
#: melalui skrip seed pada database.sql) - lihat BR-07.
REGISTRABLE_ROLES = (ROLE_OPERATOR, ROLE_PETANI)

#: Ringkasan hak akses tiap peran.
ROLE_CAPABILITIES = {
    ROLE_ADMIN: {
        "label": "Administrator",
        "deskripsi": "Akses penuh: mengelola seluruh modul dan menghapus data.",
        "bisa_masuk_dashboard": True,
        "bisa_kelola_petani": True,
        "bisa_kelola_panen": True,
        "bisa_kelola_distribusi": True,
        "bisa_hapus_data": True,
        "bisa_kelola_pengguna": True,
    },
    ROLE_OPERATOR: {
        "label": "Operator Gudang",
        "deskripsi": "Mencatat dan memperbarui data operasional; penghapusan "
        "data hanya dapat dilakukan Administrator.",
        "bisa_masuk_dashboard": True,
        "bisa_kelola_petani": True,
        "bisa_kelola_panen": True,
        "bisa_kelola_distribusi": True,
        "bisa_hapus_data": False,
        "bisa_kelola_pengguna": False,
    },
    ROLE_PETANI: {
        "label": "Petani",
        "deskripsi": "Hanya dapat melihat rekapitulasi data yang sudah tercatat.",
        "bisa_masuk_dashboard": True,
        "bisa_kelola_petani": False,
        "bisa_kelola_panen": False,
        "bisa_kelola_distribusi": False,
        "bisa_hapus_data": False,
        "bisa_kelola_pengguna": False,
    },
}

# ------------------------------------------------------------
# 6. NILAI BAKU STATUS PENGIRIMAN - BR-05
# ------------------------------------------------------------
STATUS_DIPROSES = "Diproses"
STATUS_DALAM_PENGIRIMAN = "Dalam Pengiriman"
STATUS_TERKIRIM = "Terkirim"

STATUS_PENGIRIMAN = (STATUS_DIPROSES, STATUS_DALAM_PENGIRIMAN, STATUS_TERKIRIM)

#: Status yang sudah final dan tidak boleh diubah/dihapus (BR-09).
STATUS_TERKUNCI = (STATUS_TERKIRIM,)
