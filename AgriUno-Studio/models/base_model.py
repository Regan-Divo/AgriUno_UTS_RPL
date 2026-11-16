"""
==========================================================
HELPER BAWAAN MODEL - AGRIUNO EDISI STUDIO
==========================================================
Modul ini memuat:

1. Fungsi ``ke_decimal()`` dan ``normalkan()`` yang dipakai
   bersama seluruh kelas model (penormalan isian BR-11).

2. Kelas ``BaseModel`` sebagai kelas induk seluruh model data.
   Kelas ini menyediakan helper eksekusi kueri, konversi nilai,
   dan penanganan galat basis data sesuai katalog kelas pada
   dokumentasi teknis.
"""

import logging
from decimal import Decimal, InvalidOperation

import mysql.connector

from config.database import DatabaseTidakTersedia, kursor

logger = logging.getLogger(__name__)


def ke_decimal(value, bawaan=Decimal("0")):
    """Konversi aman ke Decimal."""
    if value is None or value == "":
        return bawaan
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return bawaan


def normalkan(teks):
    """Menormalkan teks isian (spasi rapat + kapitalisasi judul, BR-11)."""
    return " ".join(str(teks or "").split()).title()


class BaseModel:
    """Kelas dasar seluruh model data AgriUno Studio.

    Seluruh metode bersifat statis sehingga model dapat dipakai
    tanpa harus membuat objek.
    """

    # --------------------------------------------------------
    # Helper eksekusi kueri
    # --------------------------------------------------------
    @staticmethod
    def _execute_write(sql, params=None, commit=True):
        """Menjalankan kueri tulis dan mengembalikan jumlah baris."""
        try:
            with kursor(dictionary=True, commit=commit) as cur:
                cur.execute(sql, params or ())
                return cur.rowcount
        except DatabaseTidakTersedia as exc:
            logger.error("eksekusi tulis gagal: %s", exc)
            raise

    @staticmethod
    def _fetch_all(sql, params=None):
        """Menjalankan kueri baca dan mengembalikan seluruh baris."""
        try:
            with kursor(dictionary=True, commit=False) as cur:
                cur.execute(sql, params or ())
                return cur.fetchall()
        except DatabaseTidakTersedia as exc:
            logger.error("eksekusi baca gagal: %s", exc)
            raise

    @staticmethod
    def _fetch_one(sql, params=None):
        """Menjalankan kueri baca dan mengembalikan baris pertama."""
        try:
            with kursor(dictionary=True, commit=False) as cur:
                cur.execute(sql, params or ())
                return cur.fetchone()
        except DatabaseTidakTersedia as exc:
            logger.error("eksekusi baca gagal: %s", exc)
            raise

    # --------------------------------------------------------
    # Helper konversi dan penanganan galat
    # --------------------------------------------------------
    @staticmethod
    def to_decimal(value, bawaan=Decimal("0")):
        """Konversi aman ke Decimal."""
        return ke_decimal(value, bawaan)

    @staticmethod
    def format_berat(value, desimal=2):
        """Meny_format nilai berat menjadi teks dengan satuan Kilogram."""
        return ("%." + str(int(desimal)) + "f Kg") % float(ke_decimal(value))

    @staticmethod
    def _is_foreign_key_violation(exc):
        """True bila galat berasal dari pelanggaran foreign key (errno 1451)."""
        if isinstance(exc, mysql.connector.Error):
            return getattr(exc, "errno", None) == 1451
        return False
