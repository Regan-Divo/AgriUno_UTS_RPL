"""
==========================================================
MODEL DISTRIBUSI - AGRIUNO
==========================================================
Operasi CRUD pada tabel ``distribusi``.

Aturan bisnis yang dijaga bersama lapisan Controller:

* BR-02 : jumlah yang dialokasikan tidak boleh melebihi sisa stok lot.
* BR-03 : ``id_panen`` wajib menunjuk lot panen yang terdaftar.
* BR-04 : status awal alokasi baru adalah "Diproses".
* BR-05 : hanya tiga nilai status baku yang diterima.
* BR-09 : alokasi berstatus "Terkirim" bersifat final sehingga tidak
  dapat diubah maupun dihapus.

Pembuatan dan pembaruan alokasi dijalankan dalam SATU transaksi
dengan penguncian baris (``SELECT ... FOR UPDATE``) pada lot
panen. Hal ini menutup celah *race condition* yang pada versi
sebelumnya memungkinkan dua alokasi concurrently lolos dari
pemeriksaan sisa stok sehingga terjadi stok minus.
"""

import logging

import mysql.connector

from config.constants import STATUS_DIPROSES, STATUS_PENGIRIMAN, STATUS_TERKUNCI
from config.database import DatabaseConnection, DatabaseUnavailable
from AgriUno_UTS_RPL.models.base_model import BaseModel

logger = logging.getLogger(__name__)


class DistribusiModel(BaseModel):
    """Operasi CRUD pada tabel ``distribusi``."""

    TABLE = "distribusi"

    # --------------------------------------------------------
    # Pembacaan data
    # --------------------------------------------------------
    @staticmethod
    def get_all():
        """Mengambil seluruh alokasi beserta informasi lot asalnya."""
        return BaseModel._fetch_all(
            "SELECT d.id_distribusi, d.id_panen, d.tujuan_pengiriman, "
            "d.jumlah_dikirim, d.status_pengiriman, "
            "p.jenis_komoditas, p.tgl_panen, "
            "pt.nama_petani "
            "FROM distribusi d "
            "INNER JOIN inventori_panen p ON p.id_panen = d.id_panen "
            "INNER JOIN petani pt ON pt.id_petani = p.id_petani "
            "ORDER BY d.id_distribusi DESC"
        )

    @staticmethod
    def get_by_id(id_distribusi):
        """Mengambil satu alokasi berdasarkan id."""
        return BaseModel._fetch_one(
            "SELECT id_distribusi, id_panen, tujuan_pengiriman, jumlah_dikirim, "
            "status_pengiriman FROM distribusi WHERE id_distribusi = %s",
            (id_distribusi,),
        )

    @staticmethod
    def count():
        """Mengembalikan jumlah alokasi (dipakai Dashboard)."""
        row = BaseModel._fetch_one("SELECT COUNT(*) AS total FROM distribusi")
        return int(row["total"]) if row else 0

    @staticmethod
    def count_by_status(status):
        """Mengreturns jumlah alokasi untuk sebuah status tertentu."""
        row = BaseModel._fetch_one(
            "SELECT COUNT(*) AS total FROM distribusi WHERE status_pengiriman = %s",
            (status,),
        )
        return int(row["total"]) if row else 0

    @staticmethod
    def total_dikirim():
        """Mengembalikan total seluruh berat yang sudah dialokasikan."""
        row = BaseModel._fetch_one(
            "SELECT COALESCE(SUM(jumlah_dikirim), 0) AS total FROM distribusi"
        )
        return BaseModel.to_decimal(row["total"]) if row else BaseModel.to_decimal(0)

    # --------------------------------------------------------
    # Pembuatan alokasi (transaksi atomik + row lock)
    # --------------------------------------------------------
    @staticmethod
    def create_with_stock_check(id_panen, tujuan, jumlah, status=STATUS_DIPROSES):
        """Membuat alokasi baru setelah memverifikasi ketersediaan stok.

        Mengembalikan pasangan ``(berhasil, pesan)``. Bila ``berhasil``
        bernilai ``False``, pesan berisi penjelasan yang dapat
        langsung ditampilkan kepada pengguna.
        """
        if status not in STATUS_PENGIRIMAN:
            return False, "Status pengiriman tidak dikenali!"

        jumlah = BaseModel.to_decimal(jumlah, None)
        if jumlah is None or jumlah <= 0:
            return False, "Jumlah dikirim harus lebih dari 0!"

        try:
            with DatabaseConnection.cursor(dictionary=True, commit=True) as cur:
                # Kunci baris lot panen agar tidak ada transaksi lain
                # yang memodifikasi stoklot yang sama secara bersamaan.
                cur.execute(
                    "SELECT p.id_panen, p.jumlah_berat, "
                    "COALESCE((SELECT SUM(d.jumlah_dikirim) FROM distribusi d "
                    "          WHERE d.id_panen = p.id_panen), 0) AS total_dikirim "
                    "FROM inventori_panen p WHERE p.id_panen = %s FOR UPDATE",
                    (id_panen,),
                )
                panen = cur.fetchone()

                if not panen:
                    return False, "ID Panen tidak terdaftar di sistem!"

                total_berat = BaseModel.to_decimal(panen["jumlah_berat"])
                sudah_kirim = BaseModel.to_decimal(panen["total_dikirim"])
                sisa_stok = total_berat - sudah_kirim

                if jumlah > sisa_stok:
                    return False, (
                        "Jumlah kirim melebihi sisa stok inventori yang tersedia "
                        "di gudang! (Sisa: %s Kg)" % f"{sisa_stok:.2f}"
                    )

                cur.execute(
                    "INSERT INTO distribusi (id_panen, tujuan_pengiriman, "
                    "jumlah_dikirim, status_pengiriman) VALUES (%s, %s, %s, %s)",
                    (id_panen, tujuan, jumlah, status),
                )
                cur.execute("SELECT LAST_INSERT_ID() AS id")
                id_baru = cur.fetchone()["id"]

            return True, id_baru
        except DatabaseUnavailable:
            return False, "Koneksi database gagal!"
        except mysql.connector.Error as err:
            logger.error("Galat MySQL: %s", err)
            return False, "Terjadi kesalahan database: %s" % BaseModel._describe(err)
        except Exception as exc:  # noqa: BLE001
            logger.error("Galat tak terduga: %s", exc)
            return False, "Terjadi kesalahan sistem: %s" % exc

    # --------------------------------------------------------
    # Pembaruan dan penghapusan
    # --------------------------------------------------------
    @staticmethod
    def insert(id_panen, tujuan, jumlah, status=STATUS_DIPROSES):
        """Menyisipkan alokasi tanpa validasi stok (dipakai oleh unit test)."""
        return BaseModel._execute_write(
            "INSERT INTO distribusi (id_panen, tujuan_pengiriman, jumlah_dikirim, "
            "status_pengiriman) VALUES (%s, %s, %s, %s)",
            (id_panen, tujuan, jumlah, status),
        )

    @staticmethod
    def update(id_distribusi, id_panen, tujuan, jumlah, status):
        """Memperbarui data alokasi. Mengembalikan True/False."""
        return BaseModel._execute_write(
            "UPDATE distribusi SET id_panen = %s, tujuan_pengiriman = %s, "
            "jumlah_dikirim = %s, status_pengiriman = %s WHERE id_distribusi = %s",
            (id_panen, tujuan, jumlah, status, id_distribusi),
        )

    @staticmethod
    def update_with_stock_check(id_distribusi, id_panen, tujuan, jumlah, status):
        """Memperbarui alokasi dengan verifikasi ulang ketersediaan stok.

        Mengembalikan pasangan ``(berhasil, pesan)``.
        """
        if status not in STATUS_PENGIRIMAN:
            return False, "Status pengiriman tidak dikenali!"

        jumlah = BaseModel.to_decimal(jumlah, None)
        if jumlah is None or jumlah <= 0:
            return False, "Jumlah dikirim harus lebih dari 0!"

        try:
            with DatabaseConnection.cursor(dictionary=True, commit=True) as cur:
                cur.execute(
                    "SELECT id_distribusi, status_pengiriman FROM distribusi "
                    "WHERE id_distribusi = %s FOR UPDATE",
                    (id_distribusi,),
                )
                lama = cur.fetchone()
                if not lama:
                    return False, "Data distribusi tidak ditemukan!"

                if lama["status_pengiriman"] in STATUS_TERKUNCI:
                    return False, (
                        "Alokasi berstatus 'Terkirim' bersifat final dan tidak "
                        "dapat diubah (BR-09)."
                    )

                cur.execute(
                    "SELECT p.id_panen, p.jumlah_berat, "
                    "COALESCE((SELECT SUM(d.jumlah_dikirim) FROM distribusi d "
                    "          WHERE d.id_panen = p.id_panen AND d.id_distribusi <> %s), 0) "
                    "       AS total_dikirim "
                    "FROM inventori_panen p WHERE p.id_panen = %s FOR UPDATE",
                    (id_distribusi, id_panen),
                )
                panen = cur.fetchone()

                if not panen:
                    return False, "ID Panen tidak terdaftar di sistem!"

                total_berat = BaseModel.to_decimal(panen["jumlah_berat"])
                sudah_kirim = BaseModel.to_decimal(panen["total_dikirim"])
                sisa_stok = total_berat - sudah_kirim

                if jumlah > sisa_stok:
                    return False, (
                        "Jumlah kirim melebihi sisa stok inventori yang tersedia "
                        "di gudang! (Sisa: %s Kg)" % f"{sisa_stok:.2f}"
                    )

                cur.execute(
                    "UPDATE distribusi SET id_panen = %s, tujuan_pengiriman = %s, "
                    "jumlah_dikirim = %s, status_pengiriman = %s WHERE id_distribusi = %s",
                    (id_panen, tujuan, jumlah, status, id_distribusi),
                )
            return True, "Data distribusi berhasil diperbarui!"
        except DatabaseUnavailable:
            return False, "Koneksi database gagal!"
        except mysql.connector.Error as err:
            logger.error("Galat MySQL: %s", err)
            return False, "Terjadi kesalahan database: %s" % BaseModel._describe(err)
        except Exception as exc:  # noqa: BLE001
            logger.error("Galat tak terduga: %s", exc)
            return False, "Terjadi kesalahan sistem: %s" % exc

    @staticmethod
    def delete(id_distribusi):
        """Menghapus alokasi distribusi.

        Alokasi berstatus "Terkirim" tidak dapat dihapus (BR-09).
        """
        try:
            with DatabaseConnection.cursor(dictionary=True, commit=True) as cur:
                cur.execute(
                    "SELECT status_pengiriman FROM distribusi WHERE id_distribusi = %s",
                    (id_distribusi,),
                )
                baris = cur.fetchone()
                if not baris:
                    return False, "Data distribusi tidak ditemukan!"
                if baris["status_pengiriman"] in STATUS_TERKUNCI:
                    return False, (
                        "Alokasi berstatus 'Terkirim' bersifat final dan tidak "
                        "dapat dihapus (BR-09)."
                    )
                cur.execute("DELETE FROM distribusi WHERE id_distribusi = %s", (id_distribusi,))
            return True, "Alokasi distribusi berhasil dihapus!"
        except DatabaseUnavailable:
            return False, "Koneksi database gagal!"
        except mysql.connector.Error as err:
            if BaseModel._is_foreign_key_violation(err):
                return False, "Gagal menghapus! Data masih terikat dengan data lain."
            logger.error("Galat MySQL: %s", err)
            return False, "Terjadi kesalahan database: %s" % BaseModel._describe(err)
        except Exception as exc:  # noqa: BLE001
            logger.error("Galat tak terduga: %s", exc)
            return False, "Terjadi kesalahan sistem: %s" % exc

    # --------------------------------------------------------
    # Pembantu
    # --------------------------------------------------------
    @staticmethod
    def valid_status(status):
        """Memeriksa apakah nilai status merupakan nilai baku yang sah (BR-05)."""
        return status in STATUS_PENGIRIMAN

    @staticmethod
    def is_locked(status):
        """Memeriksa apakah status bersifat final/t terkunci (BR-09)."""
        return status in STATUS_TERKUNCI
