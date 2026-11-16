"""
Konstanta aplikasi AgriUno Edisi Studio.

Pusat konfigurasi yang tidak bergantung pada basis data: identitas
aplikasi, palet warna, status pengiriman, peran pengguna beserta
matriks hak aksesnya, dan lokasi aset.
"""

import os

# ------------------------------------------------------------
# 1. IDENTITAS APLIKASI
# ------------------------------------------------------------
APP_NAME = "AgriUno"
APP_TAGLINE = "Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal"
APP_VERSION = "2.0.0"
APP_RELEASE = "UAS RPL 2026"

# ------------------------------------------------------------
# 2. LOKASI ASET
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = os.path.join(BASE_DIR, "assets", "logo_agriuno.png")
IKON = os.path.join(BASE_DIR, "assets", "logo_agriuno.ico")
ANIM = os.path.join(BASE_DIR, "assets", "anim")
WORDMARK = os.path.join(BASE_DIR, "assets", "logo_agriuno_wordmark_small.png")

# ------------------------------------------------------------
# 3. PALET WARNA (BRAND)
# ------------------------------------------------------------
FONT = "Segoe UI"

HIJAU = "#1b4332"  # primer - rail, tombol utama
HIJAU_HOVER = "#2d6a4f"
HIJAU_LEMBUT = "#e6f2ea"  # latar aksen hijau muda
HIJAU_TEKS = "#2f7d4f"

AMBER = "#b45309"
AMBER_LEMBUT = "#fef3c7"

BIRU = "#1d4ed8"
BIRU_LEMBUT = "#dbeafe"

MERAH = "#b91c1c"
MERAH_LEMBUT = "#fee2e2"

LATAR = "#f1f4f2"  # latar konten
KARTU = "#ffffff"
GARIS = "#e3e9e5"
TEKS = "#1f2d25"
REDUP = "#6b7a71"

ZEBRA = "#f7faf8"
TERPILIH = "#dcebe2"
KEPALA_TABEL = "#eef4f0"

STATUS_WARNA = {
    "Diproses": (AMBER_LEMBUT, AMBER),
    "Dalam Pengiriman": (BIRU_LEMBUT, BIRU),
    "Terkirim": (HIJAU_LEMBUT, HIJAU_TEKS),
}

# ------------------------------------------------------------
# 4. STATUS PENGIRIMAN (BR-05)
# ------------------------------------------------------------
STATUS_DIPROSES = "Diproses"
STATUS_KIRIM = "Dalam Pengiriman"
STATUS_TERKIRIM = "Terkirim"
STATUS_DAFTAR = (STATUS_DIPROSES, STATUS_KIRIM, STATUS_TERKIRIM)

#: Alur status satu arah: langkah berikutnya dari tiap status.
ALUR_STATUS = {STATUS_DIPROSES: STATUS_KIRIM, STATUS_KIRIM: STATUS_TERKIRIM}

# ------------------------------------------------------------
# 5. PERAN DAN HAK AKSES
# ------------------------------------------------------------
ROLE_ADMIN = "admin"
ROLE_OPERATOR = "operator"
ROLE_PETANI = "petani"

#: Matriks hak akses Studio.
HAK_AKSES = {
    ROLE_ADMIN: {"kelola": True, "hapus": True},
    ROLE_OPERATOR: {"kelola": True, "hapus": False},
    ROLE_PETANI: {"kelola": False, "hapus": False},
}

LABEL_PERAN = {
    ROLE_ADMIN: "Administrator",
    ROLE_OPERATOR: "Operator Gudang",
    ROLE_PETANI: "Petani",
}


def label_peran(role):
    """Label tampilan untuk sebuah peran."""
    return LABEL_PERAN.get(role, "Pengguna")


def boleh(user, kemampuan):
    """Memeriksa hak akses peran untuk kemampuan 'kelola'/'hapus'."""
    if not user:
        return False
    return bool(HAK_AKSES.get(user["role"], {}).get(kemampuan, False))
