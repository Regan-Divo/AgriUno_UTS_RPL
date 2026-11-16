"""
==========================================================
MODEL DASAR - AGRIUNO
==========================================================
Berisi utilitas bersama yang dipakai seluruh kelas model:
penanganan galat integritas relasi, normalisasi baris hasil
query, dan pembantu pemformatan angka.

Dengan memusatkan penanganan galat di sini, setiap kelas model
hanya perlu fokus pada logika CRUD masing-masing entitas.
"""

import logging
from decimal import Decimal, InvalidOperation

import mysql.connector

from config.database import DatabaseConnection, DatabaseUnavailable

logger = logging.getLogger(__name__)

#: errno MySQL untuk pelanggaran foreign key constraint.
ERRNO_FOREIGN_KEY = 1451

#: errno MySQL untuk pelanggaran unique constraint.
ERRNO_DUPLICATE = 1062


class ModelError(Exception):
    """Galat bisnis yang Pesan-nya aman ditampilkan ke pengguna."""


class BaseModel:
    """Kelas dasar untuk seluruh kelas model AgriUno."""

    # --------------------------------------------------------
    # Helper khusus MySQL
    # --------------------------------------------------------
    @staticmethod
    def _is_foreign_key_violation(err):
        """Mendeteksi pelanggaran foreign key constraint (errno 1451)."""
        return getattr(err, "errno", None) == ERRNO_FOREIGN_KEY

    @staticmethod
    def _is_duplicate(err):
        """Mendeteksi pelanggaran unique constraint (errno 1062)."""
        return getattr(err, "errno", None) == ERRNO_DUPLICATE

    @staticmethod
    def _describe(err):
        """Mengambil pesan galat yang human-readable dari exception."""
        msg = getattr(err, "msg", None) or str(err)
        return str(msg)

    # --------------------------------------------------------
    # Normalisasi hasil query
    # --------------------------------------------------------
    @staticmethod
    def _rows(cursor):
        """Mengambil seluruh baris hasil query sebagai list of dict."""
        result = cursor.fetchall()
        return list(result) if result else []

    @staticmethod
    def _row(cursor):
        """Mengambil satu baris hasil query sebagai dict (atau None)."""
        result = cursor.fetchone()
        return dict(result) if result else None

    # --------------------------------------------------------
    # Konversi tipe
    # --------------------------------------------------------
    @staticmethod
    def to_decimal(value, default=Decimal("0")):
        """Mengubah masukan apa pun menjadi ``Decimal`` yang aman.

        Mengembalikan ``default`` bila nilai tidak dapat dikonversi.
        """
        if value is None:
            return default
        if isinstance(value, Decimal):
            return value
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return default

    @staticmethod
    def format_berat(value):
        """Memformat berat menjadi dua angka desimal tanpa angka nol excess."""
        return f"{BaseModel.to_decimal(value):.2f}"

    # --------------------------------------------------------
    # Helper yang sering dipakai
    # --------------------------------------------------------
    @staticmethod
    def _execute_write(sql, params=()):
        """Menjalankan kueri tulis dalam satu transaksi atomik.

        Mengembalikan ``True`` bila berhasil. Galat integritas
        relasi (1451), duplikasi (1062), dan kegagalan koneksi
        dicatat sebagai peringatan tanpa menghentikan aplikasi.
        """
        try:
            with DatabaseConnection.cursor(commit=True) as cur:
                cur.execute(sql, params)
            return True
        except DatabaseUnavailable:
            logger.error("Koneksi database gagal saat menjalankan kueri tulis.")
            return False
        except mysql.connector.Error as err:
            logger.error("Galat MySQL: %s", err)
            return False
        except Exception as exc:  # noqa: BLE001
            logger.error("Galat tak terduga: %s", exc)
            return False

    @staticmethod
    def _fetch_all(sql, params=()):
        """Menjalankan kueri baca dan mengembalikan list of dict (kosong bila gagal)."""
        try:
            with DatabaseConnection.cursor(dictionary=True) as cur:
                cur.execute(sql, params)
                return BaseModel._rows(cur)
        except DatabaseUnavailable:
            logger.error("Koneksi database gagal saat menjalankan kueri baca.")
            return []
        except mysql.connector.Error as err:
            logger.error("Galat MySQL: %s", err)
            return []
        except Exception as exc:  # noqa: BLE001
            logger.error("Galat tak terduga: %s", exc)
            return []

    @staticmethod
    def _fetch_one(sql, params=()):
        """Menjalankan kueri baca dan mengembalikan satu dict (atau None)."""
        try:
            with DatabaseConnection.cursor(dictionary=True) as cur:
                cur.execute(sql, params)
                return BaseModel._row(cur)
        except DatabaseUnavailable:
            logger.error("Koneksi database gagal saat menjalankan kueri baca.")
            return None
        except mysql.connector.Error as err:
            logger.error("Galat MySQL: %s", err)
            return None
        except Exception as exc:  # noqa: BLE001
            logger.error("Galat tak terduga: %s", exc)
            return None
