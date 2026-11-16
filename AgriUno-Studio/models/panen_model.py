"""Model lot setoran panen (tabel inventori_panen)."""

import logging

from datetime import datetime

from models.base_model import ke_decimal, normalkan

import mysql.connector

from config.constants import boleh
from config.database import DatabaseTidakTersedia, kursor
logger = logging.getLogger(__name__)


class PanenModel:
    """Model lot setoran panen (tabel inventori_panen)."""

    _SQL_PANEN = (
        "SELECT p.id_panen, p.id_petani, p.jenis_komoditas, p.jumlah_berat, p.tgl_panen, "
        "pt.nama_petani, "
        "COALESCE(SUM(d.jumlah_dikirim), 0) AS total_dikirim, "
        "(p.jumlah_berat - COALESCE(SUM(d.jumlah_dikirim), 0)) AS sisa_stok "
        "FROM inventori_panen p "
        "LEFT JOIN distribusi d ON d.id_panen = p.id_panen "
        "LEFT JOIN petani pt ON pt.id_petani = p.id_petani "
    )


    @staticmethod
    def get_all(cari=""):
        """Mengambil lot panen beserta sisa stok dan nama petaninya."""
        pola = "%{}%".format((cari or "").strip())
        where = "WHERE p.jenis_komoditas LIKE %s OR pt.nama_petani LIKE %s OR p.id_panen LIKE %s "
        try:
            with kursor(commit=False) as cur:
                cur.execute(
                    PanenModel._SQL_PANEN
                    + where
                    + " GROUP BY p.id_panen, p.id_petani, p.jenis_komoditas, p.jumlah_berat, "
                    "p.tgl_panen, pt.nama_petani ORDER BY p.tgl_panen DESC, p.id_panen DESC",
                    (pola, pola, pola),
                )
                return cur.fetchall()
        except DatabaseTidakTersedia as exc:
            logger.error("daftar_panen: %s", exc)
            return []


    @staticmethod
    def simpan(user, id_panen, id_petani, jenis, berat, tanggal):
        """Menyimpan lot setoran panen baru/ubah dengan validasi lengkap."""
        if not boleh(user, "kelola"):
            return False, "Peran Anda tidak memiliki hak mengelola data!"
        jenis = normalkan(jenis)
        if not id_petani or not jenis or not str(berat or "").strip() or not str(tanggal or "").strip():
            return False, "Seluruh kolom setoran panen wajib diisi!"
        if len(jenis) > 100:
            return False, "Jenis komoditas maksimal 100 karakter!"

        nilai_berat = ke_decimal(berat, None)
        if nilai_berat is None:
            return False, "Jumlah berat harus berupa angka numerik!"
        if nilai_berat <= 0:
            return False, "Jumlah berat panen harus berupa angka positif!"

        try:
            tgl = datetime.strptime((tanggal or "").strip(), "%Y-%m-%d").date()
        except ValueError:
            return False, "Tanggal harus berformat YYYY-MM-DD!"
        if tgl > datetime.now().date():
            return False, "Tanggal panen tidak boleh di masa depan!"

        try:
            with kursor(commit=True) as cur:
                cur.execute("SELECT id_petani FROM petani WHERE id_petani = %s", (id_petani,))
                if cur.fetchone() is None:
                    return False, "ID Petani tidak terdaftar di sistem!"

                if id_panen:
                    cur.execute(
                        "SELECT COALESCE(SUM(jumlah_dikirim), 0) AS t FROM distribusi "
                        "WHERE id_panen = %s",
                        (id_panen,),
                    )
                    sudah = ke_decimal(cur.fetchone()["t"])
                    if nilai_berat < sudah:
                        return False, (
                            "Berat baru (%.2f Kg) lebih kecil daripada total yang sudah "
                            "dialokasikan (%.2f Kg). Ubah alokasi distribusi terlebih dahulu."
                            % (nilai_berat, sudah)
                        )
                    cur.execute(
                        "UPDATE inventori_panen SET id_petani=%s, jenis_komoditas=%s, "
                        "jumlah_berat=%s, tgl_panen=%s WHERE id_panen=%s",
                        (id_petani, jenis, nilai_berat, tgl, id_panen),
                    )
                    return True, "Lot panen berhasil diperbarui."
                cur.execute(
                    "INSERT INTO inventori_panen (id_petani, jenis_komoditas, jumlah_berat, "
                    "tgl_panen) VALUES (%s, %s, %s, %s)",
                    (id_petani, jenis, nilai_berat, tgl),
                )
            return True, "Setoran panen berhasil dicatat."
        except DatabaseTidakTersedia as exc:
            return False, "Koneksi database gagal: %s" % exc
        except mysql.connector.Error as err:
            if err.errno == 1451:
                return False, "Lot masih terikat alokasi distribusi."
            logger.error("simpan_panen: %s", err)
            return False, "Terjadi kesalahan database: %s" % err


    @staticmethod
    def hapus(user, id_panen):
        """Menghapus lot panen (hanya Administrator; ditolak bila terikat)."""
        if not boleh(user, "hapus"):
            return False, "Penghapusan data hanya dapat dilakukan oleh Administrator!"
        try:
            with kursor(commit=True) as cur:
                cur.execute("DELETE FROM inventori_panen WHERE id_panen = %s", (id_panen,))
            return True, "Lot panen berhasil dihapus."
        except DatabaseTidakTersedia as exc:
            return False, "Koneksi database gagal: %s" % exc
        except mysql.connector.Error as err:
            if err.errno == 1451:
                return False, "Lot masih memiliki alokasi distribusi (BR-03)."
            logger.error("hapus_panen: %s", err)
            return False, "Terjadi kesalahan database: %s" % err


    # ========================================================
    # METODE KATALOG KELAS (dokumentasi teknis 4.7)
    # ========================================================
    @staticmethod
    def get_by_id(id_panen):
        """Mengambil satu lot panen beserta sisa stoknya."""
        try:
            with kursor(commit=False) as cur:
                cur.execute(
                    PanenModel._SQL_PANEN
                    + "WHERE p.id_panen = %s GROUP BY p.id_panen, p.id_petani, "
                    "p.jenis_komoditas, p.jumlah_berat, p.tgl_panen, pt.nama_petani",
                    (id_panen,),
                )
                return cur.fetchone()
        except DatabaseTidakTersedia as exc:
            logger.error("lot_panen: %s", exc)
            return None

    @staticmethod
    def get_sisa_stok(id_panen):
        """Menghitung sisa stok sebuah lot (BR-03)."""
        try:
            with kursor(commit=False) as cur:
                cur.execute(
                    "SELECT COALESCE((SELECT SUM(d.jumlah_dikirim) FROM distribusi d "
                    "  WHERE d.id_panen = p.id_panen), 0) AS t FROM inventori_panen p "
                    "WHERE p.id_panen = %s",
                    (id_panen,),
                )
                row = cur.fetchone()
                if row is None:
                    return ke_decimal(0)
                cur.execute(
                    "SELECT jumlah_berat FROM inventori_panen WHERE id_panen = %s",
                    (id_panen,),
                )
                berat = cur.fetchone()
                if berat is None:
                    return ke_decimal(0)
                return ke_decimal(berat["jumlah_berat"]) - ke_decimal(row["t"])
        except DatabaseTidakTersedia as exc:
            logger.error("sisa_stok: %s", exc)
            return ke_decimal(0)

    @staticmethod
    def get_total_terkirim(id_panen):
        """Menghitung total berat yang sudah dialokasikan dari sebuah lot."""
        try:
            with kursor(commit=False) as cur:
                cur.execute(
                    "SELECT COALESCE(SUM(jumlah_dikirim), 0) AS t FROM distribusi "
                    "WHERE id_panen = %s",
                    (id_panen,),
                )
                row = cur.fetchone()
                return ke_decimal(row["t"]) if row else ke_decimal(0)
        except DatabaseTidakTersedia as exc:
            logger.error("total_terkirim: %s", exc)
            return ke_decimal(0)

    @staticmethod
    def count():
        """Menghitung jumlah lot panen tersimpan."""
        try:
            with kursor(commit=False) as cur:
                cur.execute("SELECT COUNT(*) AS t FROM inventori_panen")
                return int(cur.fetchone()["t"])
        except DatabaseTidakTersedia:
            return 0

    @staticmethod
    def total_berat():
        """Menghitung total berat seluruh setoran panen (Kg)."""
        try:
            with kursor(commit=False) as cur:
                cur.execute("SELECT COALESCE(SUM(jumlah_berat), 0) AS t FROM inventori_panen")
                return ke_decimal(cur.fetchone()["t"])
        except DatabaseTidakTersedia:
            return ke_decimal(0)

    @staticmethod
    def insert(user, id_petani, jenis, berat, tanggal):
        """Menyimpan lot setoran panen baru."""
        return PanenModel.simpan(user, None, id_petani, jenis, berat, tanggal)

    @staticmethod
    def update(user, id_panen, id_petani, jenis, berat, tanggal):
        """Memperbarui lot setoran panen yang sudah ada."""
        return PanenModel.simpan(user, id_panen, id_petani, jenis, berat, tanggal)

    @staticmethod
    def delete(user, id_panen):
        """Menghapus lot setoran panen."""
        return PanenModel.hapus(user, id_panen)