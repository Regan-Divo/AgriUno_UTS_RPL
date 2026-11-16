"""Model master data petani (tabel petani)."""

import logging

import mysql.connector

from config.constants import boleh
from config.database import DatabaseTidakTersedia, kursor
from models.base_model import normalkan

logger = logging.getLogger(__name__)


class PetaniModel:
    """Model master data petani (tabel petani)."""

    @staticmethod
    def get_all(cari=""):
        """Mengambil petani beserta rekapitulasi setorannya."""
        pola = "%{}%".format((cari or "").strip())
        try:
            with kursor(commit=False) as cur:
                cur.execute(
                    "SELECT pt.id_petani, pt.nama_petani, pt.lokasi_lahan, "
                    "pt.komoditas_utama, COUNT(ip.id_panen) AS jml_lot, "
                    "COALESCE(SUM(ip.jumlah_berat), 0) AS total_setor "
                    "FROM petani pt LEFT JOIN inventori_panen ip ON ip.id_petani = pt.id_petani "
                    "WHERE pt.nama_petani LIKE %s OR pt.lokasi_lahan LIKE %s "
                    "OR pt.komoditas_utama LIKE %s "
                    "GROUP BY pt.id_petani, pt.nama_petani, pt.lokasi_lahan, pt.komoditas_utama "
                    "ORDER BY pt.nama_petani",
                    (pola, pola, pola),
                )
                return cur.fetchall()
        except DatabaseTidakTersedia as exc:
            logger.error("daftar_petani: %s", exc)
            return []

    @staticmethod
    def get_options():
        """Peta id -> data petani untuk dropdown (urut id)."""
        try:
            with kursor(commit=False) as cur:
                cur.execute(
                    "SELECT id_petani, nama_petani, komoditas_utama FROM petani ORDER BY id_petani"
                )
                return cur.fetchall()
        except DatabaseTidakTersedia as exc:
            logger.error("peta_petani: %s", exc)
            return []

    @staticmethod
    def simpan(user, id_petani, nama, lokasi, komoditas):
        """Menyimpan (tambah bila id kosong / ubah bila id terisi) data petani."""
        if not boleh(user, "kelola"):
            return False, "Peran Anda tidak memiliki hak mengelola data!"

        nama, lokasi, komoditas = normalkan(nama), normalkan(lokasi), normalkan(komoditas)
        if not nama or not lokasi or not komoditas:
            return False, "Nama, lokasi lahan, dan komoditas utama wajib diisi!"
        if len(nama) > 100 or len(lokasi) > 150 or len(komoditas) > 100:
            return False, "Panjang teks melebihi batas kolom basis data!"

        try:
            with kursor(dictionary=True, commit=True) as cur:
                cur.execute(
                    "SELECT id_petani, nama_petani FROM petani "
                    "WHERE LOWER(nama_petani) = %s AND LOWER(lokasi_lahan) = %s "
                    "AND LOWER(komoditas_utama) = %s",
                    (nama.casefold(), lokasi.casefold(), komoditas.casefold()),
                )
                duplikat = cur.fetchone()
                if duplikat and str(duplikat["id_petani"]) != str(id_petani or ""):
                    return False, (
                        "Gagal menyimpan! Petani dengan nama, lokasi lahan, dan komoditas "
                        "yang sama sudah terdaftar (ID %s - %s) sesuai aturan BR-11."
                        % (duplikat["id_petani"], duplikat["nama_petani"])
                    )

                if id_petani:
                    cur.execute(
                        "UPDATE petani SET nama_petani=%s, lokasi_lahan=%s, komoditas_utama=%s "
                        "WHERE id_petani=%s",
                        (nama, lokasi, komoditas, id_petani),
                    )
                    return True, "Data petani berhasil diperbarui."
                cur.execute(
                    "INSERT INTO petani (nama_petani, lokasi_lahan, komoditas_utama) "
                    "VALUES (%s, %s, %s)",
                    (nama, lokasi, komoditas),
                )
            return True, "Petani baru berhasil didaftarkan."
        except DatabaseTidakTersedia as exc:
            return False, "Koneksi database gagal: %s" % exc
        except mysql.connector.Error as err:
            if err.errno == 1451:
                return (
                    False,
                    "Petani masih memiliki riwayat setoran dan tidak dapat diubah/dihapus.",
                )
            logger.error("simpan_petani: %s", err)
            return False, "Terjadi kesalahan database: %s" % err

    @staticmethod
    def hapus(user, id_petani):
        """Menghapus petani (hanya Administrator; ditolak bila masih terikat)."""
        if not boleh(user, "hapus"):
            return False, "Penghapusan data hanya dapat dilakukan oleh Administrator!"
        try:
            with kursor(commit=True) as cur:
                cur.execute("DELETE FROM petani WHERE id_petani = %s", (id_petani,))
            return True, "Data petani berhasil dihapus."
        except DatabaseTidakTersedia as exc:
            return False, "Koneksi database gagal: %s" % exc
        except mysql.connector.Error as err:
            if err.errno == 1451:
                return False, (
                    "Gagal menghapus! Petani masih memiliki riwayat setoran panen "
                    "aktif di gudang (BR-01)."
                )
            logger.error("hapus_petani: %s", err)
            return False, "Terjadi kesalahan database: %s" % err

    # ========================================================
    # METODE KATALOG KELAS (dokumentasi teknis 4.7)
    # ========================================================
    @staticmethod
    def get_by_id(id_petani):
        """Mengambil satu data petani beserta rekapitulasi setorannya."""
        try:
            with kursor(commit=False) as cur:
                cur.execute(
                    "SELECT pt.id_petani, pt.nama_petani, pt.lokasi_lahan, "
                    "pt.komoditas_utama, COUNT(ip.id_panen) AS jml_lot, "
                    "COALESCE(SUM(ip.jumlah_berat), 0) AS total_setor "
                    "FROM petani pt LEFT JOIN inventori_panen ip "
                    "ON ip.id_petani = pt.id_petani WHERE pt.id_petani = %s "
                    "GROUP BY pt.id_petani, pt.nama_petani, pt.lokasi_lahan, "
                    "pt.komoditas_utama",
                    (id_petani,),
                )
                return cur.fetchone()
        except DatabaseTidakTersedia as exc:
            logger.error("petani: %s", exc)
            return None

    @staticmethod
    def exists(id_petani):
        """True bila petani dengan ID tersebut terdaftar (BR-01)."""
        try:
            with kursor(commit=False) as cur:
                cur.execute("SELECT id_petani FROM petani WHERE id_petani = %s", (id_petani,))
                return cur.fetchone() is not None
        except DatabaseTidakTersedia:
            return False

    @staticmethod
    def count():
        """Menghitung jumlah petani tersimpan."""
        try:
            with kursor(commit=False) as cur:
                cur.execute("SELECT COUNT(*) AS t FROM petani")
                return int(cur.fetchone()["t"])
        except DatabaseTidakTersedia:
            return 0

    @staticmethod
    def count_petani_aktif():
        """Menghitung petani yang memiliki riwayat setoran panen."""
        try:
            with kursor(commit=False) as cur:
                cur.execute(
                    "SELECT COUNT(DISTINCT p.id_petani) AS t FROM petani p "
                    "INNER JOIN inventori_panen ip ON ip.id_petani = p.id_petani"
                )
                return int(cur.fetchone()["t"])
        except DatabaseTidakTersedia:
            return 0

    @staticmethod
    def insert(user, nama, lokasi, komoditas):
        """Menyimpan data petani baru."""
        return PetaniModel.simpan(user, None, nama, lokasi, komoditas)

    @staticmethod
    def update(user, id_petani, nama, lokasi, komoditas):
        """Memperbarui data petani yang sudah ada."""
        return PetaniModel.simpan(user, id_petani, nama, lokasi, komoditas)

    @staticmethod
    def delete(user, id_petani):
        """Menghapus data petani."""
        return PetaniModel.hapus(user, id_petani)
