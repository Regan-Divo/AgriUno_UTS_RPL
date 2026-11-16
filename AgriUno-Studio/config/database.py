"""
==========================================================
KONEKSI BASIS DATA MYSQL - AGRIUNO EDISI STUDIO
==========================================================
Modul ini menyediakan dua hal:

1. Fungsi ``kursor()`` sebagai jalan masuk tunggal ke basis data.
   Setiap blok ``with`` menjamin bahwa kursor DAN koneksi selalu
   ditutup, sehingga tidak terjadi connection leak maupun resource
   yang menggantung (brk-05).

2. Kelas ``DatabaseConnection`` yang dipakai seluruh kelas model
   sebagai pembungkus koneksi: ``connect()``, ``cursor()``, dan
   ``ping()`` sesuai katalog kelas pada dokumentasi teknis.

Kredensial dapat dioverride lewat environment variable sehingga
tidak perlu mengubah kode sumber (AGRIUNO_DB_HOST/PORT/USER/
PASSWORD/NAME).
"""

import logging
import os
from contextlib import contextmanager

import mysql.connector
from mysql.connector import Error

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Parameter koneksi (dapat dioverride lewat environment)
# ------------------------------------------------------------
DB_HOST = os.getenv("AGRIUNO_DB_HOST", "localhost")
DB_PORT = int(os.getenv("AGRIUNO_DB_PORT", "3306"))
DB_USER = os.getenv("AGRIUNO_DB_USER", "root")
DB_PASSWORD = os.getenv("AGRIUNO_DB_PASSWORD", "")
DB_NAME = os.getenv("AGRIUNO_DB_NAME", "agriuno")


class DatabaseTidakTersedia(Exception):
    """Dibangkitkan bila koneksi ke server MySQL gagal dibentuk."""


class DatabaseConnection:
    """Pembungkus koneksi MySQL beserta kursor dan pemeriksaan koneksi."""

    @staticmethod
    def connect(database=None):
        """Membuka koneksi baru ke server MySQL.

        Mengembalikan objek koneksi; galat dilempar sebagai
        ``DatabaseTidakTersedia`` agar model dapat menanganinya.
        """
        try:
            return mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=database if database is not None else DB_NAME,
                connection_timeout=5,
            )
        except Error as exc:
            raise DatabaseTidakTersedia(str(exc)) from exc

    @staticmethod
    @contextmanager
    def cursor(dictionary=True, commit=True):
        """Context manager kursor dengan commit/rollback eksplisit."""
        conn = DatabaseConnection.connect()
        cur = conn.cursor(dictionary=dictionary)
        try:
            yield cur
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            try:
                cur.close()
            finally:
                conn.close()

    @staticmethod
    def ping():
        """True bila server MySQL dapat dihubungi."""
        try:
            conn = DatabaseConnection.connect()
            conn.close()
            return True
        except Exception:  # noqa: BLE001
            return False


@contextmanager
def kursor(dictionary=True, commit=True):
    """Context manager kursor dengan komit/rollback eksplisit."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connection_timeout=5,
        )
    except Error as exc:
        raise DatabaseTidakTersedia(str(exc)) from exc

    cur = conn.cursor(dictionary=dictionary)
    try:
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        try:
            cur.close()
        finally:
            conn.close()


def tersedia():
    """True bila server MySQL dapat dihubungi."""
    try:
        with kursor(commit=False) as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        return True
    except Exception:  # noqa: BLE001
        return False
