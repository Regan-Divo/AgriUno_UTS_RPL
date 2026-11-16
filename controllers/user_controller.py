"""
==========================================================
CONTROLLER PENGGUNA - AGRIUNO  (Modul 7)
==========================================================
Menyediakan antarmuka logika untuk pengelolaan akun pengguna
khusus oleh Administrator.

Modul ini menjadi lapisan antara ``UserModel`` dan antarmuka
pengelolaan akun. Seluruh method mengembalikan pasangan
``(berhasil, pesan)`` agar konsisten dengan ``AgriUnoController``.
"""

import logging

from config.constants import ROLE_ADMIN
from controllers.auth_controller import AuthController
from AgriUno_UTS_RPL.models.user_model import UserModel

logger = logging.getLogger(__name__)


class UserController:
    """Kontroler pengelolaan akun pengguna AgriUno."""

    # --------------------------------------------------------
    # Registrasi (dipakai juga oleh RegisterView)
    # --------------------------------------------------------
    @staticmethod
    def daftar(username, password, konfirmasi_password, full_name, role):
        """Mendaftarkan akun pengguna baru.

        Peran yang boleh dipilih hanya ``operator`` dan ``petani``.
        """
        return UserModel.register(username, password, konfirmasi_password, full_name, role)

    # --------------------------------------------------------
    # Pembacaan data
    # --------------------------------------------------------
    @staticmethod
    def daftar_akun():
        """Mengambil seluruh daftar akun pengguna."""
        return UserModel.get_all()

    @staticmethod
    def akun_by_id(id_user):
        """Mengambil satu data akun pengguna."""
        return UserModel.get_by_id(id_user)

    # --------------------------------------------------------
    # Pemeliharaan akun (khusus Administrator)
    # --------------------------------------------------------
    @staticmethod
    def ubah_profil(id_user, full_name):
        """Memperbarui nama lengkap pengguna."""
        return UserModel.update_profile(id_user, full_name)

    @staticmethod
    def ubah_password(id_user, password_lama, password_baru, konfirmasi_baru):
        """Mengubah kata sandi pengguna."""
        return UserModel.change_password(id_user, password_lama, password_baru, konfirmasi_baru)

    @staticmethod
    def aktifkan(id_user):
        """Mengaktifkan kembali sebuah akun yang dinonaktifkan."""
        return UserModel.set_active(id_user, True)

    @staticmethod
    def nonaktifkan(id_user):
        """Menonaktifkan sebuah akun tanpa menghapusnya."""
        return UserModel.set_active(id_user, False)

    @staticmethod
    def hapus(id_user):
        """Menghapus sebuah akun pengguna."""
        return AuthController.hapus_akun(id_user)

    # --------------------------------------------------------
    # Pemeriksaan hak akses
    # --------------------------------------------------------
    @staticmethod
    def boleh_kelola_pengguna():
        """Menyatakan apakah sesi aktif berhak mengelola akun pengguna."""
        return AuthController.boleh("bisa_kelola_pengguna")

    @staticmethod
    def hanya_admin():
        """Menyatakan apakah sesi aktif berperan sebagai Administrator."""
        return AuthController.session.role == ROLE_ADMIN
