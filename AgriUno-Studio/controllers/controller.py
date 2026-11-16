"""
Controller utama AgriUno Edisi Studio.

Jembatan antara tampilan (View) dan model data. Seluruh method
bersifat statis dan langsung mendelegasikan pemanggilan ke kelas
model; aturan bisnis BR-02, BR-05, BR-09, dan BR-11 ditegakkan
di dalam kelas model.
"""

from models.dashboard_model import DashboardModel
from models.distribusi_model import DistribusiModel
from models.panen_model import PanenModel
from models.petani_model import PetaniModel
from models.user_model import UserModel


class AgriUnoController:
    """Kontroler utama aplikasi AgriUno Edisi Studio."""

    # ========================================================
    # PETANI  (BR-01, BR-03, BR-11)
    # ========================================================
    @staticmethod
    def get_petani(cari=""):
        """Mengambil petani beserta rekapitulasi setorannya."""
        return PetaniModel.get_all(cari)

    @staticmethod
    def get_pilihan_petani():
        """Daftar petani untuk dropdown form."""
        return PetaniModel.get_options()

    @staticmethod
    def simpan_petani(user, id_petani, nama, lokasi, komoditas):
        """Menyimpan (tambah/ubah) data petani."""
        return PetaniModel.simpan(user, id_petani, nama, lokasi, komoditas)

    @staticmethod
    def hapus_petani(user, id_petani):
        """Menghapus petani (hanya Administrator)."""
        return PetaniModel.hapus(user, id_petani)

    # ========================================================
    # INVENTORI PANEN  (BR-01, BR-03, BR-10)
    # ========================================================
    @staticmethod
    def get_panen(cari=""):
        """Mengambil lot panen beserta sisa stoknya."""
        return PanenModel.get_all(cari)

    @staticmethod
    def simpan_panen(user, id_panen, id_petani, jenis, berat, tanggal):
        """Menyimpan lot setoran panen."""
        return PanenModel.simpan(user, id_panen, id_petani, jenis, berat, tanggal)

    @staticmethod
    def hapus_panen(user, id_panen):
        """Menghapus lot panen (hanya Administrator)."""
        return PanenModel.hapus(user, id_panen)

    # ========================================================
    # DISTRIBUSI  (BR-02, BR-05, BR-09)
    # ========================================================
    @staticmethod
    def get_distribusi(cari="", status=""):
        """Mengambil alokasi distribusi."""
        return DistribusiModel.get_all(cari, status)

    @staticmethod
    def simpan_distribusi(user, id_distribusi, id_panen, tujuan, jumlah, status):
        """Menyimpan alokasi dengan pemeriksaan stok transaksional."""
        return DistribusiModel.simpan(user, id_distribusi, id_panen, tujuan, jumlah, status)

    @staticmethod
    def lanjut_status(user, id_distribusi):
        """Memajukan status pengiriman satu tahap."""
        return DistribusiModel.lanjut_status(user, id_distribusi)

    @staticmethod
    def hapus_distribusi(user, id_distribusi):
        """Menghapus alokasi (hanya Administrator)."""
        return DistribusiModel.hapus(user, id_distribusi)

    # ========================================================
    # DASHBOARD
    # ========================================================
    @staticmethod
    def get_statistik():
        """Ringkasan angka untuk kartu KPI Dashboard."""
        return DashboardModel.get_statistik()

    # ========================================================
    # AKUN PENGGUNA  (UC-09)
    # ========================================================
    @staticmethod
    def ubah_sandi(user, sandi_lama, sandi_baru, konfirmasi):
        """Mengubah kata sandi pengguna yang sedang login."""
        return UserModel.update_password(user, sandi_lama, sandi_baru, konfirmasi)

    # ========================================================
    # ALIAS METODE KATALOG KELAS (dokumentasi teknis 4.7)
    # ========================================================
    @staticmethod
    def tambah_petani(user, nama, lokasi, komoditas):
        """Menambah data petani baru."""
        return PetaniModel.simpan(user, None, nama, lokasi, komoditas)

    @staticmethod
    def update_petani(user, id_petani, nama, lokasi, komoditas):
        """Memperbarui data petani."""
        return PetaniModel.simpan(user, id_petani, nama, lokasi, komoditas)

    @staticmethod
    def tambah_panen(user, id_petani, jenis, berat, tanggal):
        """Menambah lot setoran panen baru."""
        return PanenModel.simpan(user, None, id_petani, jenis, berat, tanggal)

    @staticmethod
    def update_panen(user, id_panen, id_petani, jenis, berat, tanggal):
        """Memperbarui lot setoran panen."""
        return PanenModel.simpan(user, id_panen, id_petani, jenis, berat, tanggal)

    @staticmethod
    def tambah_distribusi(user, id_panen, tujuan, jumlah, status):
        """Menambah alokasi pengiriman baru."""
        return DistribusiModel.simpan(user, None, id_panen, tujuan, jumlah, status)

    @staticmethod
    def update_distribusi(user, id_distribusi, id_panen, tujuan, jumlah, status):
        """Memperbarui alokasi pengiriman."""
        return DistribusiModel.simpan(
            user, id_distribusi, id_panen, tujuan, jumlah, status
        )

    @staticmethod
    def update_status(user, id_distribusi, status):
        """Mengubah status alokasi pengiriman secara langsung."""
        data = DistribusiModel.get_by_id(id_distribusi)
        if not data:
            return False, "Alokasi tidak ditemukan!"
        return DistribusiModel.simpan(
            user,
            id_distribusi,
            data["id_panen"],
            data["tujuan_pengiriman"],
            data["jumlah_dikirim"],
            status,
        )
