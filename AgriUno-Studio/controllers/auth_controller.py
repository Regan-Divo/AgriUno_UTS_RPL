"""
Controller autentikasi AgriUno Edisi Studio.

Menangani proses masuk, pendaftaran akun, pemeliharaan akun
pengguna, sesi pengguna, dan pemeriksaan hak akses berbasis peran
(Role-Based Access Control).
"""

from config import constants
from controllers.user_controller import UserController
from AgriUno_UTS_RPL.models.user_model import UserModel


class Session:
    """Penyimpan state sesi pengguna yang sedang login.

    Objek ini menyimpan profil pengguna sehingga seluruh halaman
    dapat menyesuaikan hak aksesnya, dan menyediakan rangkuman
    kapabilitas peran untuk ditampilkan pada panel profil.
    """

    def __init__(self):
        self.reset()

    # --------------------------------------------------------
    def reset(self):
        """Mengosongkan sesi (dipanggil saat keluar atau ganti pengguna)."""
        self.user = None

    def set_user(self, user):
        """Mengisi sesi dengan profil pengguna hasil autentikasi."""
        self.user = user

    def aktif(self):
        """True bila terdapat pengguna yang sedang login."""
        return bool(self.user)

    # --------------------------------------------------------
    # Ringkasan profil pengguna
    # --------------------------------------------------------
    @property
    def id_user(self):
        """Identitas pengguna aktif."""
        return (self.user or {}).get("id_user")

    @property
    def role(self):
        """Peran pengguna aktif."""
        return (self.user or {}).get("role")

    @property
    def username(self):
        """Nama akun pengguna aktif."""
        return (self.user or {}).get("username")

    @property
    def full_name(self):
        """Nama lengkap pengguna aktif."""
        return (self.user or {}).get("nama")

    def label_peran(self):
        """Label peran pengguna untuk ditampilkan di antarmuka."""
        if not self.user:
            return "Pengguna"
        return constants.LABEL_PERAN.get(self.role, "Pengguna")

    def capabilities(self):
        """Daftar kapabilitas yang dimiliki peran pengguna aktif."""
        if not self.user:
            return []
        hak = constants.HAK_AKSES.get(self.role, {})
        daftar = []
        if hak.get("kelola"):
            daftar.append("kelola")
        if hak.get("hapus"):
            daftar.append("hapus")
        return daftar

    def boleh(self, aksi):
        """Memeriksa apakah pengguna aktif memiliki kapabilitas tertentu."""
        if not self.user:
            return False
        return constants.boleh(self.user, aksi)

    def ringkasan(self):
        """Ringkasan profil pengguna aktif untuk ditampilkan."""
        if not self.user:
            return {}
        return {
            "id_user": self.id_user,
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role,
            "label_peran": self.label_peran(),
            "kapabilitas": self.capabilities(),
        }


class AuthController:
    """Kontroler autentikasi dan otorisasi AgriUno Studio."""

    @staticmethod
    def login(username, password):
        """Memverifikasi kredensial melalui UserModel."""
        return UserModel.authenticate(username, password)

    @staticmethod
    def logout(session):
        """Mengakhiri sesi pengguna dan mengosongkan objek Session."""
        if session is not None:
            session.reset()
        return True, "Anda telah keluar dari aplikasi."

    @staticmethod
    def register(nama, username, password, konfirmasi, role):
        """Mendaftarkan akun khusus (peran operator/petani).

        Alur registrasi diteruskan ke UserController.daftar() sesuai
        katalog kelas pada dokumentasi teknis.
        """
        return UserController.daftar(nama, username, password, konfirmasi, role)

    @staticmethod
    def current_user(session):
        """Profil pengguna yang sedang login."""
        return getattr(session, "user", None)

    @staticmethod
    def boleh(user, kemampuan):
        """Memeriksa hak akses peran ('kelola' / 'hapus')."""
        return constants.boleh(user, kemampuan)

    @staticmethod
    def daftar_akun(cari=""):
        """Daftar seluruh akun pengguna (khusus Administrator)."""
        return UserModel.get_all(cari)

    @staticmethod
    def set_akun_aktif(id_user, aktif=True):
        """Mengaktifkan atau menonaktifkan sebuah akun."""
        return UserModel.set_active(id_user, aktif)

    @staticmethod
    def hapus_akun(id_user):
        """Menghapus sebuah akun pengguna."""
        return UserModel.delete(id_user)

    @staticmethod
    def ubah_password(user, sandi_lama, sandi_baru, konfirmasi):
        """Mengubah kata sandi pengguna yang sedang login (UC-09)."""
        return UserModel.change_password(user, sandi_lama, sandi_baru, konfirmasi)
