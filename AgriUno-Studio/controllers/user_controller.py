"""
Controller pemeliharaan akun pengguna AgriUno Edisi Studio.

Menangani registrasi akun baru serta sejumlah operasi pemeliharaan
yang hanya dapat dilakukan Administrator: daftar akun, ubah profil,
ubah kata sandi, aktif/nonaktifkan, dan hapus akun.
"""

from config.constants import ROLE_ADMIN
from AgriUno_UTS_RPL.models.user_model import UserModel


class UserController:
    """Kontroler logika pemeliharaan akun pengguna.

    Seluruh metode bersifat statis sehingga tidak menyimpan state
    objek.
    """

    @staticmethod
    def daftar(cari=""):
        """Daftar akun pengguna beserta rekapitulasialiensinya."""
        return UserModel.get_all(cari)

    @staticmethod
    def daftar_akun_baru(nama, username, password, konfirmasi, role):
        """Mendaftarkan akun baru melalui formulir registrasi (FR-08)."""
        return UserModel.register(nama, username, password, konfirmasi, role)

    @staticmethod
    def daftar_akun(cari=""):
        """Alias ``daftar`` untuk pemanggilan dari antarmuka."""
        return UserModel.get_all(cari)

    @staticmethod
    def ubah_profil(id_user, nama):
        """Memperbarui nama lengkap pengguna."""
        return UserModel.update_profile(id_user, nama)

    @staticmethod
    def ubah_password(user, sandi_lama, sandi_baru, konfirmasi):
        """Mengubah kata sandi pengguna yang sedang login."""
        return UserModel.change_password(user, sandi_lama, sandi_baru, konfirmasi)

    @staticmethod
    def aktifkan(id_user):
        """Mengaktifkan kembali sebuah akun nonaktif."""
        return UserModel.set_active(id_user, True)

    @staticmethod
    def nonaktifkan(id_user):
        """Menonaktifkan sebuah akun tanpa menghapusnya."""
        return UserModel.set_active(id_user, False)

    @staticmethod
    def hapus(id_user):
        """Menghapus sebuah akun pengguna."""
        return UserModel.delete(id_user)

    @staticmethod
    def boleh_kelola_pengguna(user):
        """True bila pengguna berhak mengelola akun pengguna lain."""
        if not user:
            return False
        return user.get("role") == ROLE_ADMIN
