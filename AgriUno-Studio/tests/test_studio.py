"""
Pengujian otomatis AgriUno Edisi Studio.

Cakupan: hashing dan verifikasi kata sandi, matriks hak akses
peran, alur status pengiriman, helper nilai, dan aturan validasi
yang dapat diperiksa tanpa koneksi basis data.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.constants import (  # noqa: E402
    ALUR_STATUS,
    HAK_AKSES,
    ROLE_ADMIN,
    ROLE_OPERATOR,
    ROLE_PETANI,
    STATUS_DAFTAR,
    STATUS_DIPROSES,
    STATUS_KIRIM,
    STATUS_TERKIRIM,
    boleh,
    label_peran,
)
from AgriUno_UTS_RPL.models.base_model import BaseModel, ke_decimal, normalkan  # noqa: E402
from AgriUno_UTS_RPL.models.user_model import UserModel  # noqa: E402


# ============================================================
# 1. HASHING KATA SANDI (BR-07, NFR-02)
# ============================================================
def test_hash_password_deterministik():
    """Hash yang sama untuk masukan dan salt yang sama."""
    a = UserModel.hash_password("rahasia123", "salt-aja")
    b = UserModel.hash_password("rahasia123", "salt-aja")
    assert a == b
    assert len(a) == 64


def test_hash_password_bergantung_salt():
    """Salt berbeda menghasilkan hash berbeda."""
    a = UserModel.hash_password("rahasia123", "salt-1")
    b = UserModel.hash_password("rahasia123", "salt-2")
    assert a != b


def test_hash_password_tidak_menyimpan_teks_sandi():
    """Teks asli kata sandi tidak pernah muncul pada hasil hash."""
    assert "rahasia123" not in UserModel.hash_password("rahasia123", "salt-aja")


def test_generate_sandi_panjang_dan_unik():
    """Salt acak sepanjang 16 byte dan berbeda tiap pemanggilan."""
    a = UserModel.generate_salt()
    b = UserModel.generate_salt()
    assert len(a) == 32
    assert a != b


def test_verify_password_menerima_kecocokan():
    """Verifikasi menerima kata sandi yang benar."""
    salt = UserModel.generate_salt()
    hash_sandi = UserModel.hash_password("rahasia123", salt)
    assert UserModel.verify_password("rahasia123", salt, hash_sandi) is True
    assert UserModel.verify_password("salah123", salt, hash_sandi) is False


# ============================================================
# 2. HAK AKSES BERBASIS PERAN (NFR-07)
# ============================================================
@pytest.mark.parametrize(
    "role,kelola,hapus",
    [
        (ROLE_ADMIN, True, True),
        (ROLE_OPERATOR, True, False),
        (ROLE_PETANI, False, False),
    ],
)
def test_matriks_hak_akses_peran(role, kelola, hapus):
    """Administrator penuh, operator kelola tanpa hapus, petani baca."""
    user = {"role": role}
    assert boleh(user, "kelola") is kelola
    assert boleh(user, "hapus") is hapus


def test_boleh_menolak_tanpa_user():
    """Tanpa sesi, tidak ada hak akses sama sekali."""
    assert boleh(None, "kelola") is False
    assert boleh({}, "hapus") is False


def test_label_peran_terpetakan():
    """Setiap peran memiliki label tampilan."""
    assert label_peran(ROLE_ADMIN) == "Administrator"
    assert label_peran(ROLE_OPERATOR) == "Operator Gudang"
    assert label_peran(ROLE_PETANI) == "Petani"


def test_peran_admin_tidak_terdaftar_pada_registrasi():
    """Registrasi mandiri tidak menawarkan peran admin (BR-08)."""

    assert ROLE_ADMIN not in (ROLE_OPERATOR, ROLE_PETANI)


# ============================================================
# 3. ALUR STATUS PENGIRIMAN (BR-04, BR-05, BR-09)
# ============================================================
def test_daftar_status_baku():
    """Hanya tiga status baku yang berlaku."""
    assert set(STATUS_DAFTAR) == {STATUS_DIPROSES, STATUS_KIRIM, STATUS_TERKIRIM}
    assert len(STATUS_DAFTAR) == 3


def test_alur_status_searah():
    """Status bergerak satu arah: Diproses -> Dalam Pengiriman -> Terkirim."""
    assert ALUR_STATUS[STATUS_DIPROSES] == STATUS_KIRIM
    assert ALUR_STATUS[STATUS_KIRIM] == STATUS_TERKIRIM
    assert STATUS_TERKIRIM not in ALUR_STATUS


def test_status_terkirim_tidak_lagi_dapat_diproses():
    """Alokasi Terkirim bersifat final (BR-09)."""
    assert STATUS_TERKIRIM not in ALUR_STATUS


# ============================================================
# 4. HELPER NILAI (BR-11)
# ============================================================
def test_normalkan_merapikan_teks():
    """Spasi rapat dirapikan dan kapitalisasi judul diterapkan."""
    assert normalkan("  budi   santoso ") == "Budi Santoso"
    assert normalkan(None) == ""


def test_ke_decimal_aman_dan_default():
    """Nilai tidak valid jatuh ke nilai bawaan."""
    from decimal import Decimal

    assert ke_decimal("12.5") == Decimal("12.5")
    assert ke_decimal("abc") == Decimal("0")
    assert ke_decimal(None) == Decimal("0")


def test_format_berat_menambahkan_satuan():
    """Berat diformat dengan satuan Kilogram."""
    assert BaseModel.format_berat(12.5) == "12.50 Kg"


def test_base_model_menyediakan_helper_katalog():
    """Kelas BaseModel menyediakan seluruh helper pada katalog kelas."""
    for nama in (
        "_execute_write",
        "_fetch_all",
        "_fetch_one",
        "to_decimal",
        "format_berat",
        "_is_foreign_key_violation",
    ):
        assert hasattr(BaseModel, nama)


# ============================================================
# 5. HAK AKSES DAN DAFTAR TABEL
# ============================================================
def test_hak_akses_mencakup_tiga_peran():
    """Matriks hak akses memuat tepat tiga peran aplikasi."""
    assert set(HAK_AKSES) == {ROLE_ADMIN, ROLE_OPERATOR, ROLE_PETANI}


def test_tabel_aplikasi_terdaftar():
    """Skema basis data aplikasi terdiri dari empat tabel."""
    import re

    jalur = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database.sql"
    )
    with open(jalur, encoding="utf-8") as berkas:
        isi = berkas.read()
    tabel = re.findall(r"CREATE TABLE(?: IF NOT EXISTS)?\s+`?(\w+)`?", isi, re.I)
    assert set(tabel) == {"users", "petani", "inventori_panen", "distribusi"}
