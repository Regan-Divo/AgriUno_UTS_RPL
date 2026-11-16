"""
==========================================================
MODEL PETANI - AGRIUNO
==========================================================
Operasi CRUD pada tabel ``petani``.

Tabel ``petani`` menjadi master data penyetor hasil panen.
Relasi: satu data petani dapat memiliki banyak lot panen
(1 : 0..*) pada tabel ``inventori_panen``.
"""

import logging

import mysql.connector

from config.database import DatabaseConnection, DatabaseUnavailable
from models.base_model import BaseModel

logger = logging.getLogger(__name__)


class PetaniModel(BaseModel):
    """Operasi CRUD pada tabel ``petani``."""

    TABLE = "petani"

    # --------------------------------------------------------
    # Pembacaan data
    # --------------------------------------------------------
    @staticmethod
    def get_all():
        """Mengambil seluruh data petani diurutkan berdasarkan nama."""
        return BaseModel._fetch_all(
            "SELECT id_petani, nama_petani, lokasi_lahan, komoditas_utama "
            "FROM petani ORDER BY nama_petani"
        )

    @staticmethod
    def get_by_id(id_petani):
        """Mengambil satu data petani berdasarkan id."""
        return BaseModel._fetch_one(
            "SELECT id_petani, nama_petani, lokasi_lahan, komoditas_utama "
            "FROM petani WHERE id_petani = %s",
            (id_petani,),
        )

    @staticmethod
    def count():
        """Mengembalikan jumlah data petani (dipakai Dashboard)."""
        row = BaseModel._fetch_one("SELECT COUNT(*) AS total FROM petani")
        return int(row["total"]) if row else 0

    @staticmethod
    def count_petani_aktif():
        """Menghitung petani yang pernah menyetor minimal satu lot panen.

        Nilai ini dipakai sebagai indikator kinerja "Petani Aktif" pada
        Dashboard sehingga angka yang tampil selalu berasal dari data
        nyata, bukan angka tetap.
        """
        row = BaseModel._fetch_one(
            "SELECT COUNT(DISTINCT p.id_petani) AS total "
            "FROM petani p INNER JOIN inventori_panen ip ON ip.id_petani = p.id_petani"
        )
        return int(row["total"]) if row else 0

    @staticmethod
    def exists(id_petani):
        """Memeriksa keberadaan data petani (BR-01)."""
        row = BaseModel._fetch_one(
            "SELECT id_petani FROM petani WHERE id_petani = %s", (id_petani,)
        )
        return row is not None

    # --------------------------------------------------------
    # Penulisan data
    # --------------------------------------------------------
    @staticmethod
    def insert(nama, lokasi, komoditas):
        """Menyisipkan data petani baru. Mengembalikan True/False."""
        return BaseModel._execute_write(
            "INSERT INTO petani (nama_petani, lokasi_lahan, komoditas_utama) VALUES (%s, %s, %s)",
            (nama, lokasi, komoditas),
        )

    @staticmethod
    def update(id_petani, nama, lokasi, komoditas):
        """Memperbarui data petani. Mengembalikan True/False."""
        return BaseModel._execute_write(
            "UPDATE petani SET nama_petani = %s, lokasi_lahan = %s, "
            "komoditas_utama = %s WHERE id_petani = %s",
            (nama, lokasi, komoditas, id_petani),
        )

    @staticmethod
    def delete(id_petani):
        """Menghapus data petani.

        Penghapusan ditolak apabila petani masih memiliki riwayat
        setoran panen (violation foreign key, errno 1451) - BR-01.
        """
        try:
            with DatabaseConnection.cursor(commit=True) as cur:
                cur.execute("DELETE FROM petani WHERE id_petani = %s", (id_petani,))
            return True, "Data petani berhasil dihapus!"
        except DatabaseUnavailable:
            return False, "Koneksi database gagal!"
        except mysql.connector.Error as err:
            if BaseModel._is_foreign_key_violation(err):
                return False, (
                    "Gagal menghapus! Petani masih memiliki riwayat setoran "
                    "panen aktif di gudang (BR-01)."
                )
            logger.error("Galat MySQL: %s", err)
            return False, "Terjadi kesalahan database: %s" % BaseModel._describe(err)
        except Exception as exc:  # noqa: BLE001
            logger.error("Galat tak terduga: %s", exc)
            return False, "Terjadi kesalahan sistem: %s" % exc
