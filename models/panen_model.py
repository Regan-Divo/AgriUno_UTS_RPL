"""
==========================================================
MODEL INVENTORI PANEN - AGRIUNO
==========================================================
Operasi CRUD pada tabel ``inventori_panen``.

CATATAN PENTING TENTANG KOLOM ``jumlah_berat``
----------------------------------------------
Nilai kolom ``jumlah_berat`` adalah **berat awal lot** saatysetor
ke gudang, BUKAN sisa stok. Kolom ini sengaja tidak dimodifikasi
setiap kali dibuat alokasi distribusi, sebab dengan begitu:

1. Histori setoran tetap dapat ditelusuri kembali.
2. Sisa stok dapat dihitung ulang dari sumber kebenaran yang
   tunggal (tabel ``distribusi``), sehingga tidak mungkin terjadi
   ketidaksesuaian antara data stok dan data alokasi.

Sisa stok dihitung dengan rumus (BR-02)::

    sisa_stok = jumlah_berat - SUM(distribusi.jumlah_dikirim)

Penghitungan ini dilakukan pada level basis data melalui query
LEFT JOIN sehingga nilai yang ditampilkan antarmuka selalu
konsisten dengan aturan bisnis.
"""

import logging

import mysql.connector

from config.database import DatabaseConnection, DatabaseUnavailable
from models.base_model import BaseModel

logger = logging.getLogger(__name__)

#: Query dasar yang menyertakan perhitungan sisa stok.
_SELECT_WITH_STOCK = """
    SELECT p.id_panen,
           p.id_petani,
           p.jenis_komoditas,
           p.jumlah_berat,
           p.tgl_panen,
           COALESCE(SUM(d.jumlah_dikirim), 0) AS total_dikirim,
           (p.jumlah_berat - COALESCE(SUM(d.jumlah_dikirim), 0)) AS sisa_stok
    FROM inventori_panen p
    LEFT JOIN distribusi d ON d.id_panen = p.id_panen
"""


class PanenModel(BaseModel):
    """Operasi CRUD pada tabel ``inventori_panen``."""

    TABLE = "inventori_panen"

    # --------------------------------------------------------
    # Pembacaan data
    # --------------------------------------------------------
    @staticmethod
    def get_all():
        """Mengambil seluruh lot panen beserta sisa stoknya."""
        return BaseModel._fetch_all(
            _SELECT_WITH_STOCK + " GROUP BY p.id_panen, p.id_petani, p.jenis_komoditas, "
            "p.jumlah_berat, p.tgl_panen ORDER BY p.tgl_panen DESC, p.id_panen DESC"
        )

    @staticmethod
    def get_by_id(id_panen):
        """Mengambil satu lot panen beserta sisa stoknya."""
        return BaseModel._fetch_one(
            _SELECT_WITH_STOCK + " WHERE p.id_panen = %s "
            "GROUP BY p.id_panen, p.id_petani, p.jenis_komoditas, "
            "p.jumlah_berat, p.tgl_panen",
            (id_panen,),
        )

    @staticmethod
    def get_sisa_stok(id_panen):
        """Mengembalikan sisa stok (Kg) untuk sebuah lot panen."""
        row = BaseModel._fetch_one(
            "SELECT (p.jumlah_berat - COALESCE(SUM(d.jumlah_dikirim), 0)) AS sisa_stok "
            "FROM inventori_panen p "
            "LEFT JOIN distribusi d ON d.id_panen = p.id_panen "
            "WHERE p.id_panen = %s GROUP BY p.id_panen, p.jumlah_berat",
            (id_panen,),
        )
        if not row:
            return None
        return BaseModel.to_decimal(row["sisa_stok"])

    @staticmethod
    def get_total_terkirim(id_panen):
        """Mengembalikan total berat yang sudah dialokasikan dari sebuah lot."""
        row = BaseModel._fetch_one(
            "SELECT COALESCE(SUM(jumlah_dikirim), 0) AS total FROM distribusi WHERE id_panen = %s",
            (id_panen,),
        )
        return BaseModel.to_decimal(row["total"]) if row else BaseModel.to_decimal(0)

    @staticmethod
    def count():
        """Mengembalikan jumlah lot panen (dipakai Dashboard)."""
        row = BaseModel._fetch_one("SELECT COUNT(*) AS total FROM inventori_panen")
        return int(row["total"]) if row else 0

    @staticmethod
    def total_berat():
        """Mengembalikan total berat lot panen yang tercatat."""
        row = BaseModel._fetch_one(
            "SELECT COALESCE(SUM(jumlah_berat), 0) AS total FROM inventori_panen"
        )
        return BaseModel.to_decimal(row["total"]) if row else BaseModel.to_decimal(0)

    # --------------------------------------------------------
    # Penulisan data
    # --------------------------------------------------------
    @staticmethod
    def insert(id_petani, jenis, berat, tanggal):
        """Mencatat lot setoran panen baru. Mengembalikan True/False."""
        return BaseModel._execute_write(
            "INSERT INTO inventori_panen (id_petani, jenis_komoditas, jumlah_berat, tgl_panen) "
            "VALUES (%s, %s, %s, %s)",
            (id_petani, jenis, berat, tanggal),
        )

    @staticmethod
    def update(id_panen, id_petani, jenis, berat, tanggal):
        """Memperbarui data lot panen. Mengembalikan True/False."""
        return BaseModel._execute_write(
            "UPDATE inventori_panen SET id_petani = %s, jenis_komoditas = %s, "
            "jumlah_berat = %s, tgl_panen = %s WHERE id_panen = %s",
            (id_petani, jenis, berat, tanggal, id_panen),
        )

    @staticmethod
    def delete(id_panen):
        """Menghapus lot panen.

        Penghapusan ditolak apabila lot masih terikat pada data alokasi
        distribusi (violation foreign key, errno 1451) - BR-03.
        """
        try:
            with DatabaseConnection.cursor(commit=True) as cur:
                cur.execute("DELETE FROM inventori_panen WHERE id_panen = %s", (id_panen,))
            return True, "Lot panen berhasil dihapus!"
        except DatabaseUnavailable:
            return False, "Koneksi database gagal!"
        except mysql.connector.Error as err:
            if BaseModel._is_foreign_key_violation(err):
                return False, (
                    "Gagal menghapus! Lot panen masih terikat dengan data alokasi distribusi."
                )
            logger.error("Galat MySQL: %s", err)
            return False, "Terjadi kesalahan database: %s" % BaseModel._describe(err)
        except Exception as exc:  # noqa: BLE001
            logger.error("Galat tak terduga: %s", exc)
            return False, "Terjadi kesalahan sistem: %s" % exc
