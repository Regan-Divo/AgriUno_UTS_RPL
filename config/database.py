"""
==========================================================
KONFIGURASI DATABASE MYSQL - AGRIUNO
Database : agriuno (MySQL 8.0 - Laragon)
==========================================================
Pola yang diterapkan pada berkas ini:

1. Context manager ``DatabaseConnection.cursor()`` sebagai jalan
   masuk tunggal ke basis data. Setiap blok ``with`` menjamin
   bahwa kursor DAN koneksi selalu ditutup, sehingga tidak terjadi
   connection leak maupun resource yang menggantung (brk-05).

2. Transaksi dieksplisitkan. Semua operasi tulis dibungkus
   ``conn.commit()`` pada keberhasilan dan ``conn.rollback()``
   pada kegagalan - embodies prinsip Atomicity (kegagalan tidak
   meninggalkan perubahan setengah jadi pada basis data).

3. Parameterized query (placeholder %s) dipakai seluruh kueri
   sehingga aman terhadap SQL Injection.

4. Parameter koneksi dapat dioverride lewat environment variable
   sehingga kredensial tidak harus hardcode di dalam kode sumber.
"""

import logging
import os
from contextlib import contextmanager

import mysql.connector
from mysql.connector import Error

# Logger modul: seluruh pesan koneksi dicatat ke konsol/tornado log
logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# PARAMETER KONEKSI
# Nilai bawaan mengikuti konfigurasi standar Laragon (root tanpa
# kata sandi, port 3306) yang dipakai pada Modul 2 s.d. Modul 8.
# Untuk lingkungan lain, set environment variable berikut.
# ------------------------------------------------------------
DB_HOST = os.getenv("AGRIUNO_DB_HOST", "localhost")
DB_PORT = int(os.getenv("AGRIUNO_DB_PORT", "3306"))
DB_USER = os.getenv("AGRIUNO_DB_USER", "root")
DB_PASSWORD = os.getenv("AGRIUNO_DB_PASSWORD", "")
DB_NAME = os.getenv("AGRIUNO_DB_NAME", "agriuno")
DB_CONNECT_TIMEOUT = int(os.getenv("AGRIUNO_DB_TIMEOUT", "5"))


class DatabaseConnection:
    """Pabrik koneksi MySQL untuk AgriUno."""

    # --------------------------------------------------------
    # Pembuatan koneksi
    # --------------------------------------------------------
    @staticmethod
    def connect(database=DB_NAME):
        """Membuat dan mengembalikan objek koneksi MySQL.

        Mengembalikan ``None`` apabila koneksi gagal, sehingga pemanggil
        dapat menampilkan pesan galat yang informatif alih-alih aplikasi
        berhenti mendadak (NFR-03).
        """
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=database,
                user=DB_USER,
                password=DB_PASSWORD,
                connection_timeout=DB_CONNECT_TIMEOUT,
            )
            if connection.is_connected():
                return connection
            connection.close()
            logger.error("Koneksi tersusun tetapi tidak berstatus terhubung.")
            return None
        except Error as exc:
            logger.error("Kesalahan koneksi database: %s", exc)
            return None
        except Exception as exc:  # noqa: BLE001 - jaring pengaman terakhir
            logger.error("Kesalahan tak terduga saat koneksi: %s", exc)
            return None

    # --------------------------------------------------------
    # Context manager kursor
    # --------------------------------------------------------
    @contextmanager
    def cursor(dictionary=False, commit=True):
        """Memberikan kursor di dalam ``with`` beserta pembersihannya.

        Parameter
        ----------
        dictionary : bool
            Bila ``True`` hasil baris dikembalikan sebagai ``dict``.
        commit : bool
            Bila ``True`` (nilai bawaan) transaksi dikomit ketika blok
            selesai tanpa galat. Bila blok melempar galat, transaksi
            di-rollback sehingga tidak ada perubahan setengah jadi.

            Nilai bawaan ``True`` dipilih dengan sengaja: MySQL
            Connector/Python menjalankan driver dalam mode non-autocommit.
            Tanpa ``commit`` eksplisit, seluruh operasi tulis akan
            dibatalkan secara diam-diam saat koneksi ditutup.
        """
        conn = DatabaseConnection.connect()
        if conn is None:
            raise DatabaseUnavailable("Tidak dapat terhubung ke server MySQL.")

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

    # --------------------------------------------------------
    # Pemeriksaan kesehatan koneksi
    # --------------------------------------------------------
    @staticmethod
    def ping():
        """Mengembalikan ``True`` bila server MySQL dapat dihubungi."""
        conn = DatabaseConnection.connect()
        if conn is None:
            return False
        try:
            conn.ping(reconnect=True, attempts=1, delay=0)
            return True
        except Error:
            return False
        finally:
            conn.close()


class DatabaseUnavailable(Exception):
    """Ditetakkan ketika koneksi ke server MySQL tidak dapat dibentuk."""
