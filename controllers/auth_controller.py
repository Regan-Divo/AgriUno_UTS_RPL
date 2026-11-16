"""
==========================================================
CONTROLLER AUTENTIKASI - AGRIUNO  (Modul 7)
==========================================================
Menangani proses login, sesi pengguna, dan otorisasi berbasis
peran (Role-Based Access Control).

Pola MVC yang diterapkan:

* **Model**  - ``UserModel`` memverifikasi kredensial pada tabel
  ``users`` menggunakan *prepared statement* dan mencocokkan hash
  SHA-256 password.
* **Controller** - kelas ini menerima status autentikasi beserta
  peran pengguna, lalu mengatur alur aplikasi: jendela utama
  dibuka atau login ditolak.
* **View** - menyesuaikan tampilan antarmuka berdasarkan peran,
  yaitu menonaktifkan tombol dan kolom isian yang tidak_diizinkan
  bagi peran tersebut.

Objek ``Session`` menyimpan profil pengguna yang sedang login
sehingga seluruh halaman dapat menyesuaikan hak aksesnya.
"""

import logging

from config.constants import (
    ALL_ROLES,
    ROLE_CAPABILITIES,
    ROLE_PETANI,
)
from models.user_model import UserModel

logger = logging.getLogger(__name__)


class Session:
    """Penyimpan state sesi pengguna yang sedang masuk."""

    def __init__(self):
        self.reset()

    # --------------------------------------------------------
    def reset(self):
        """Mengosongkan sesi (dipanggil saat logout)."""
        self.user = None
        self.role = None
        self.username = None
        self.full_name = None
        self.id_user = None

    # --------------------------------------------------------
    def aktif(self):
        """Menyatakan apakah sesi sedang aktif."""
        return self.user is not None

    # --------------------------------------------------------
    def set_user(self, user):
        """Menyimpan data pengguna hasil verifikasi ke dalam sesi."""
        self.user = user
        self.id_user = user.get("id_user")
        self.username = user.get("username")
        self.full_name = user.get("full_name") or user.get("username")
        self.role = user.get("role") or ROLE_PETANI
        return self

    # --------------------------------------------------------
    def capabilities(self):
        """Mengembalikan kamus hak akses untuk peran sesi aktif."""
        return ROLE_CAPABILITIES.get(self.role, ROLE_CAPABILITIES[ROLE_PETANI])

    # --------------------------------------------------------
    def boleh(self, aksi):
        """Memeriksa apakah peran sesi memiliki hak atas sebuah aksi.

        Contoh pemakaian::

            if session.boleh("bisa_kelola_petani"):
                ...
        """
        return bool(self.capabilities().get(aksi, False))

    # --------------------------------------------------------
    @property
    def label_peran(self):
        """Nama tampilan peran sesi aktif."""
        return self.capabilities().get("label", self.role or "-")

    # --------------------------------------------------------
    def ringkasan(self):
        """Mengembalikan ringkasan sesi untuk ditampilkan pada sidebar."""
        return {
            "id_user": self.id_user,
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role,
            "label_peran": self.label_peran,
        }


class AuthController:
    """Kontroler autentikasi dan otorisasi AgriUno."""

    #: Sesi global aplikasi. Diinisialisasi satu kali saat aplikasi dibuka.
    session = Session()

    # --------------------------------------------------------
    # Autentikasi
    # --------------------------------------------------------
    @staticmethod
    def login(username, password):
        """Memverifikasi kredensial dan membuka sesi pengguna.

        Mengembalikan pasangan ``(berhasil, pesan)``. Bila berhasil,
        ``AuthController.session`` telah terisi data pengguna.
        """
        username = (username or "").strip()
        if not username:
            return False, "Username wajib diisi!"
        if not password:
            return False, "Password wajib diisi!"

        user = UserModel.authenticate(username, password)
        if user is None:
            return False, "Username atau Password salah!"

        if user.get("role") not in ALL_ROLES:
            return False, "Peran pengguna tidak dikenali. Hubungi administrator."

        AuthController.session.set_user(user)
        return True, "Login Berhasil! Selamat datang, %s." % AuthController.session.full_name

    # --------------------------------------------------------
    # Sesi
    # --------------------------------------------------------
    @staticmethod
    def logout():
        """Mengakhiri sesi pengguna."""
        AuthController.session.reset()
        return True, "Anda telah keluar dari sistem."

    @staticmethod
    def current_user():
        """Mengembalikan data pengguna yang sedang aktif."""
        return AuthController.session.user

    @staticmethod
    def boleh(aksi):
        """Memeriksa hak akses aksi tertentu untuk sesi aktif."""
        if not AuthController.session.aktif():
            return False
        return AuthController.session.boleh(aksi)

    # --------------------------------------------------------
    # Registrasi (Modul 7 - registrasi akun khusus user)
    # --------------------------------------------------------
    @staticmethod
    def register(username, password, konfirmasi_password, full_name, role):
        """Mendaftarkan akun pengguna baru.

        Peran yang boleh dipilih hanya ``operator`` dan ``petani``
        (lihat ``config.constants.REGISTRABLE_ROLES``). Akun
        ``admin`` hanya dapat dibuat oleh pengelola basis data.
        """
        return UserModel.register(username, password, konfirmasi_password, full_name, role)

    @staticmethod
    def daftar_akun():
        """Mengambil daftar seluruh akun pengguna (khusus admin)."""
        return UserModel.get_all()

    @staticmethod
    def set_akun_aktif(id_user, aktif):
        """Mengaktifkan atau menonaktifkan sebuah akun (khusus admin)."""
        return UserModel.set_active(id_user, aktif)

    @staticmethod
    def hapus_akun(id_user):
        """Menghapus sebuah akun pengguna (khusus admin)."""
        if AuthController.session.id_user == id_user:
            return False, "Akun yang sedang digunakan tidak dapat dihapus!"
        return UserModel.delete(id_user)

    @staticmethod
    def ubah_password(id_user, password_lama, password_baru, konfirmasi_baru):
        """Mengubah kata sandi seorang pengguna."""
        return UserModel.change_password(id_user, password_lama, password_baru, konfirmasi_baru)
