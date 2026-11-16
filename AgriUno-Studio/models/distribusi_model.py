"""Model alokasi distribusi (tabel distribusi)."""

import logging

from models.base_model import ke_decimal

import mysql.connector

from config.constants import ALUR_STATUS, STATUS_DAFTAR, STATUS_DIPROSES, STATUS_TERKIRIM, boleh
from config.database import DatabaseTidakTersedia, kursor
logger = logging.getLogger(__name__)


class DistribusiModel:
    """Model alokasi distribusi (tabel distribusi)."""

    @staticmethod
    def get_all(cari="", status=""):
        """Mengambil alokasi distribusi beserta konteks lot dan petaninya."""
        pola = "%{}%".format((cari or "").strip())
        syarat, argumen = [], []
        if cari:
            syarat.append("(d.tujuan_pengiriman LIKE %s OR d.id_distribusi LIKE %s)")
            argumen += [pola, pola]
        if status and status != "Semua":
            syarat.append("d.status_pengiriman = %s")
            argumen.append(status)

        sql = (
            "SELECT d.id_distribusi, d.id_panen, d.tujuan_pengiriman, d.jumlah_dikirim, "
            "d.status_pengiriman, p.jenis_komoditas, pt.nama_petani "
            "FROM distribusi d "
            "LEFT JOIN inventori_panen p ON p.id_panen = d.id_panen "
            "LEFT JOIN petani pt ON pt.id_petani = p.id_petani "
        )
        if syarat:
            sql += "WHERE " + " AND ".join(syarat) + " "
        sql += "ORDER BY d.id_distribusi DESC"

        try:
            with kursor(commit=False) as cur:
                cur.execute(sql, tuple(argumen))
                return cur.fetchall()
        except DatabaseTidakTersedia as exc:
            logger.error("daftar_distribusi: %s", exc)
            return []


    @staticmethod
    def simpan(user, id_distribusi, id_panen, tujuan, jumlah, status):
        """Menyimpan alokasi distribusi dengan pemeriksaan stok transaksional."""
        if not boleh(user, "kelola"):
            return False, "Peran Anda tidak memiliki hak mengelola data!"
        if not id_panen:
            return False, "Pilih lot panen terlebih dahulu!"
        if status not in STATUS_DAFTAR:
            return False, "Status pengiriman tidak dikenali (BR-05)!"

        tujuan = " ".join(str(tujuan or "").split())
        if not tujuan:
            return False, "Tujuan pengiriman wajib diisi!"
        if len(tujuan) > 150:
            return False, "Tujuan pengiriman maksimal 150 karakter!"

        nilai = ke_decimal(jumlah, None)
        if nilai is None or nilai <= 0:
            return False, "Jumlah dikirim harus berupa angka positif!"

        try:
            with kursor(dictionary=True, commit=True) as cur:
                cur.execute(
                    "SELECT p.id_panen, p.jumlah_berat, "
                    "COALESCE((SELECT SUM(d2.jumlah_dikirim) FROM distribusi d2 "
                    "          WHERE d2.id_panen = p.id_panen), 0) AS total_dikirim "
                    "FROM inventori_panen p WHERE p.id_panen = %s FOR UPDATE",
                    (id_panen,),
                )
                lot = cur.fetchone()
                if not lot:
                    return False, "Lot panen tidak terdaftar (BR-03)!"

                total = ke_decimal(lot["jumlah_berat"])
                sudah = ke_decimal(lot["total_dikirim"])
                if id_distribusi:
                    cur.execute(
                        "SELECT jumlah_dikirim FROM distribusi WHERE id_distribusi = %s",
                        (id_distribusi,),
                    )
                    lama = cur.fetchone()
                    if lama is None:
                        return False, "Alokasi tidak ditemukan!"
                    sudah -= ke_decimal(lama["jumlah_dikirim"])
                sisa = total - sudah
                if nilai > sisa:
                    return False, "Jumlah kirim melebihi sisa stok! Sisa tersedia: %.2f Kg." % sisa

                if id_distribusi:
                    cur.execute(
                        "SELECT status_pengiriman FROM distribusi WHERE id_distribusi = %s",
                        (id_distribusi,),
                    )
                    status_lama = cur.fetchone()
                    if status_lama and status_lama["status_pengiriman"] == STATUS_TERKIRIM:
                        return False, (
                            "Alokasi berstatus Terkirim bersifat final dan tidak dapat "
                            "diubah (BR-09)."
                        )
                    cur.execute(
                        "UPDATE distribusi SET id_panen=%s, tujuan_pengiriman=%s, "
                        "jumlah_dikirim=%s, status_pengiriman=%s WHERE id_distribusi=%s",
                        (id_panen, tujuan, nilai, status, id_distribusi),
                    )
                    return True, "Alokasi distribusi berhasil diperbarui."
                cur.execute(
                    "INSERT INTO distribusi (id_panen, tujuan_pengiriman, jumlah_dikirim, "
                    "status_pengiriman) VALUES (%s, %s, %s, %s)",
                    (id_panen, tujuan, nilai, STATUS_DIPROSES),
                )
            return True, "Alokasi pengiriman berhasil dibuat (status awal: Diproses)."
        except DatabaseTidakTersedia as exc:
            return False, "Koneksi database gagal: %s" % exc
        except mysql.connector.Error as err:
            logger.error("simpan_distribusi: %s", err)
            return False, "Terjadi kesalahan database: %s" % err


    @staticmethod
    def lanjut_status(user, id_distribusi):
        """Memajukan status pengiriman satu tahap (alur satu-klik).

        Diproses -> Dalam Pengiriman -> Terkirim. Alokasi Terkirim bersifat
        final dan tidak dapat diproses lagi (BR-09).
        """
        if not boleh(user, "kelola"):
            return False, "Peran Anda tidak memiliki hak mengelola data!"
        try:
            with kursor(dictionary=True, commit=True) as cur:
                cur.execute(
                    "SELECT status_pengiriman FROM distribusi WHERE id_distribusi = %s",
                    (id_distribusi,),
                )
                row = cur.fetchone()
                if not row:
                    return False, "Alokasi tidak ditemukan!"
                status = row["status_pengiriman"]
                if status not in ALUR_STATUS:
                    return False, "Alokasi berstatus Terkirim bersifat final (BR-09)."
                cur.execute(
                    "UPDATE distribusi SET status_pengiriman = %s WHERE id_distribusi = %s",
                    (ALUR_STATUS[status], id_distribusi),
                )
            return True, "Status diperbarui menjadi '%s'." % ALUR_STATUS[status]
        except DatabaseTidakTersedia as exc:
            return False, "Koneksi database gagal: %s" % exc
        except mysql.connector.Error as err:
            logger.error("lanjut_status: %s", err)
            return False, "Terjadi kesalahan database: %s" % err


    @staticmethod
    def hapus(user, id_distribusi):
        """Menghapus alokasi (hanya Administrator; Terkirim terkunci, BR-09)."""
        if not boleh(user, "hapus"):
            return False, "Penghapusan data hanya dapat dilakukan oleh Administrator!"
        try:
            with kursor(dictionary=True, commit=True) as cur:
                cur.execute(
                    "SELECT status_pengiriman FROM distribusi WHERE id_distribusi = %s",
                    (id_distribusi,),
                )
                row = cur.fetchone()
                if not row:
                    return False, "Alokasi tidak ditemukan!"
                if row["status_pengiriman"] == STATUS_TERKIRIM:
                    return False, "Alokasi berstatus Terkirim bersifat final (BR-09)."
                cur.execute("DELETE FROM distribusi WHERE id_distribusi = %s", (id_distribusi,))
            return True, "Alokasi distribusi berhasil dihapus."
        except DatabaseTidakTersedia as exc:
            return False, "Koneksi database gagal: %s" % exc
        except mysql.connector.Error as err:
            logger.error("hapus_distribusi: %s", err)
            return False, "Terjadi kesalahan database: %s" % err


    # ========================================================
    # METODE KATALOG KELAS (dokumentasi teknis 4.7)
    # ========================================================
    @staticmethod
    def get_by_id(id_distribusi):
        """Mengambil satu alokasi distribusi beserta konteks lot dan petaninya."""
        try:
            with kursor(commit=False) as cur:
                cur.execute(
                    "SELECT d.id_distribusi, d.id_panen, d.tujuan_pengiriman, "
                    "d.jumlah_dikirim, d.status_pengiriman, p.jenis_komoditas, "
                    "pt.nama_petani FROM distribusi d "
                    "LEFT JOIN inventori_panen p ON p.id_panen = d.id_panen "
                    "LEFT JOIN petani pt ON pt.id_petani = p.id_petani "
                    "WHERE d.id_distribusi = %s",
                    (id_distribusi,),
                )
                return cur.fetchone()
        except DatabaseTidakTersedia as exc:
            logger.error("alokasi: %s", exc)
            return None

    @staticmethod
    def create_with_stock_check(user, id_panen, tujuan, jumlah, status=STATUS_DIPROSES):
        """Membuat alokasi baru setelah pemeriksaan sisa stok (BR-02)."""
        return DistribusiModel.simpan(user, None, id_panen, tujuan, jumlah, status)

    @staticmethod
    def update_with_stock_check(user, id_distribusi, id_panen, tujuan, jumlah, status):
        """Memperbarui alokasi setelah pemeriksaan sisa stok (BR-02)."""
        return DistribusiModel.simpan(
            user, id_distribusi, id_panen, tujuan, jumlah, status
        )

    @staticmethod
    def count(status=""):
        """Menghitung jumlah alokasi, opsional penyaring status."""
        syarat, argumen = [], []
        if status and status != "Semua":
            syarat.append("status_pengiriman = %s")
            argumen.append(status)
        sql = "SELECT COUNT(*) AS t FROM distribusi"
        if syarat:
            sql += " WHERE " + " AND ".join(syarat)
        try:
            with kursor(commit=False) as cur:
                cur.execute(sql, tuple(argumen))
                return int(cur.fetchone()["t"])
        except DatabaseTidakTersedia:
            return 0

    @staticmethod
    def count_by_status():
        """Menghitung jumlah alokasi per status pengiriman."""
        hasil = {status: 0 for status in STATUS_DAFTAR}
        try:
            with kursor(commit=False) as cur:
                cur.execute(
                    "SELECT status_pengiriman, COUNT(*) AS t FROM distribusi GROUP BY status_pengiriman"
                )
                for row in cur.fetchall():
                    hasil[row["status_pengiriman"]] = int(row["t"])
        except DatabaseTidakTersedia:
            pass
        return hasil

    @staticmethod
    def total_dikirim():
        """Menghitung total berat yang sudah dialokasikan keluar gudang."""
        try:
            with kursor(commit=False) as cur:
                cur.execute("SELECT COALESCE(SUM(jumlah_dikirim), 0) AS t FROM distribusi")
                return ke_decimal(cur.fetchone()["t"])
        except DatabaseTidakTersedia:
            return ke_decimal(0)

    @staticmethod
    def insert(user, id_panen, tujuan, jumlah, status=STATUS_DIPROSES):
        """Menyimpan alokasi baru."""
        return DistribusiModel.simpan(user, None, id_panen, tujuan, jumlah, status)

    @staticmethod
    def update(user, id_distribusi, id_panen, tujuan, jumlah, status):
        """Memperbarui alokasi yang sudah ada."""
        return DistribusiModel.simpan(
            user, id_distribusi, id_panen, tujuan, jumlah, status
        )

    @staticmethod
    def delete(user, id_distribusi):
        """Menghapus alokasi distribusi."""
        return DistribusiModel.hapus(user, id_distribusi)

    @staticmethod
    def valid_status(status):
        """True bila status berada pada daftar status baku (BR-05)."""
        return status in STATUS_DAFTAR

    @staticmethod
    def is_locked(id_distribusi):
        """True bila alokasi berstatus Terkirim sehingga terkunci (BR-09)."""
        data = DistribusiModel.get_by_id(id_distribusi)
        return bool(data) and data.get("status_pengiriman") == STATUS_TERKIRIM