"""
==========================================================
MODEL PENGGUNA - AGRIUNO  (Modul 7: Autentikasi & Otorisasi)
==========================================================
Menangani seluruh operasi pada tabel ``users``:

* registrasi akun baru (dibatasi pada peran 'operator' dan 'petani'),
* verifikasi kredensial saat login,
* pengelolaan data profil pengguna.

Keamanan kata sandi:
------------------
Kata sandi TIDAK PERNAH disimpan dalam bentuk teks biasa. Setiap
pengguna memperoleh ``salt`` acak sepanjang 16 byte yang disimpan
pada kolom ``salt``. Nilai yang disimpan pada kolom ``password``
adalah SHA-256 dari ``salt + password``::

    hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

Pendekatan ini mempertahankan karakteristik ``deterministic`` dan
``irreversible`` dari SHA-256 sekaligus menutup celah rainbow-table
yang dimiliki oleh hash tanpa salt. Perbandingan memakai
``hmac.compare_digest`` agar tahan terhadap timing attack.
"""

import hashlib
import hmac
import logging
import secrets

import mysql.connector

from config.constants import (
    ALL_ROLES,
    REGISTRABLE_ROLES,
    ROLE_ADMIN,
)
from config.database import DatabaseConnection, DatabaseUnavailable
from models.base_model import BaseModel

logger = logging.getLogger(__name__)

#: Panjang salt dalam karakter heksadesimal (16 byte = 32 karakter).
SALT_LENGTH = 16


class UserModel(BaseModel):
    """Operasi CRUD pada tabel ``users``."""

    # --------------------------------------------------------
    # Pembantu hashing
    # --------------------------------------------------------
    @staticmethod
    def generate_salt():
        """Membuat nilai salt acak yang aman secara kriptografis."""
        return secrets.token_hex(SALT_LENGTH)

    @staticmethod
    def hash_password(password, salt):
        """Menghitung hash SHA-256 dari kombinasi salt dan password.

        Fungsi ini bersifat murni (deterministic) sehingga nilai yang
        sama selalu menghasilkan hash yang sama - syarat agar proses
        verifikasi saat login dapat berjalan.
        """
        if password is None or salt is None:
            return ""
        return hashlib.sha256((salt + str(password)).encode("utf-8")).hexdigest()

    @staticmethod
    def verify_password(password, salt, stored_hash):
        """Memverifikasi kecocokan password dengan hash tersimpan."""
        if not password or not salt or not stored_hash:
            return False
        candidate = UserModel.hash_password(password, salt)
        return hmac.compare_digest(candidate, stored_hash)

    # --------------------------------------------------------
    # Pembacaan data
    # --------------------------------------------------------
    @staticmethod
    def get_all():
        """Mengambil seluruh data pengguna yang aktif."""
        return BaseModel._fetch_all(
            "SELECT id_user, username, full_name, role, is_active, created_at "
            "FROM users ORDER BY id_user"
        )

    @staticmethod
    def get_by_username(username):
        """Mengambil satu data pengguna berdasarkan username (tanpa password)."""
        return BaseModel._fetch_one(
            "SELECT id_user, username, full_name, role, is_active, created_at "
            "FROM users WHERE username = %s",
            (username,),
        )

    @staticmethod
    def get_by_id(id_user):
        """Mengambil satu data pengguna berdasarkan id."""
        return BaseModel._fetch_one(
            "SELECT id_user, username, full_name, role, is_active, created_at "
            "FROM users WHERE id_user = %s",
            (id_user,),
        )

    @staticmethod
    def username_exists(username):
        """Memeriksa apakah username sudah dipakai pengguna lain."""
        row = BaseModel._fetch_one("SELECT id_user FROM users WHERE username = %s", (username,))
        return row is not None

    # --------------------------------------------------------
    # Autentikasi
    # --------------------------------------------------------
    @staticmethod
    def authenticate(username, password):
        """Memverifikasi kredensial dan mengembalikan data pengguna.

        Mengembalikan ``None`` bila username tidak ditemukan, password
        salah, atau akun sedang dinonaktifkan. Pesan galat yang
        dikembalikan sengaja diseragamkan agar tidak membocorkan
        informasi apakah sebuah username benar-benar ada.
        """
        if not username or not password:
            return None

        row = BaseModel._fetch_one(
            "SELECT id_user, username, password, salt, full_name, role, is_active "
            "FROM users WHERE username = %s",
            (username,),
        )
        if not row:
            # Jalur pseudo-random untuk menyamakan waktu respons.
            UserModel.hash_password(password, "0" * (SALT_LENGTH * 2))
            return None

        if not UserModel.verify_password(password, row["salt"], row["password"]):
            return None

        if not int(row.get("is_active", 1)):
            return None

        return {
            "id_user": row["id_user"],
            "username": row["username"],
            "full_name": row.get("full_name") or row["username"],
            "role": row.get("role") or ROLE_ADMIN,
        }

    # --------------------------------------------------------
    # Registrasi (Modul 7 - registrasi akun khusus user)
    # --------------------------------------------------------
    @staticmethod
    def register(username, password, konfirmasi_password, full_name, role):
        """Mendaftarkan akun pengguna baru.

        Mengembalikan pasangan ``(berhasil, pesan)``. Aturan yang
        ditegakkan:

        * BR-06 : username wajib diisi, minimal 4 karakter, dan unik.
        * BR-07 : peran yang boleh dipilih hanya 'operator' dan 'petani'.
        * BR-08 : password minimal 6 karakter dan harus sama dengan
          konfirmasi password.
        """
        username = (username or "").strip()
        full_name = (full_name or "").strip()
        role = (role or "").strip().lower()

        if not username:
            return False, "Username wajib diisi!"
        if len(username) < 4:
            return False, "Username minimal 4 karakter!"
        if not username.replace("_", "").replace(".", "").isalnum():
            return False, "Username hanya boleh memuat huruf, angka, titik, atau garis bawah!"
        if not full_name:
            return False, "Nama lengkap wajib diisi!"
        if not password:
            return False, "Password wajib diisi!"
        if len(password) < 6:
            return False, "Password minimal 6 karakter!"
        if password != konfirmasi_password:
            return False, "Konfirmasi password tidak sama dengan password!"
        if role not in ALL_ROLES:
            return False, "Peran pengguna tidak dikenali!"
        if role not in REGISTRABLE_ROLES:
            return False, (
                "Peran '%s' tidak dapat dipilih saat pendaftaran. "
                "Akun Administrator hanya dapat dibuat oleh pengelola basis data." % role
            )
        if UserModel.username_exists(username):
            return False, "Username '%s' sudah digunakan. Silakan gunakan username lain." % username

        salt = UserModel.generate_salt()
        password_hash = UserModel.hash_password(password, salt)

        try:
            with DatabaseConnection.cursor(commit=True) as cur:
                cur.execute(
                    "INSERT INTO users (username, password, salt, full_name, role, is_active) "
                    "VALUES (%s, %s, %s, %s, %s, 1)",
                    (username, password_hash, salt, full_name, role),
                )
            return True, "Registrasi berhasil! Akun '%s' siap digunakan." % username
        except DatabaseUnavailable:
            return False, "Koneksi database gagal, registrasi dibatalkan!"
        except mysql.connector.Error as err:
            if BaseModel._is_duplicate(err):
                return False, (
                    "Username '%s' sudah digunakan. Silakan gunakan username lain." % username
                )
            logger.error("Galat MySQL saat registrasi: %s", err)
            return False, "Terjadi kesalahan database: %s" % BaseModel._describe(err)
        except Exception as exc:  # noqa: BLE001
            logger.error("Galat tak terduga saat registrasi: %s", exc)
            return False, "Terjadi kesalahan sistem: %s" % exc

    # --------------------------------------------------------
    # Pemeliharaan akun
    # --------------------------------------------------------
    @staticmethod
    def update_profile(id_user, full_name):
        """Memperbarui nama lengkap pengguna."""
        if not id_user:
            return False, "Pengguna tidak valid!"
        if not (full_name or "").strip():
            return False, "Nama lengkap wajib diisi!"
        ok = BaseModel._execute_write(
            "UPDATE users SET full_name = %s WHERE id_user = %s",
            (full_name.strip(), id_user),
        )
        if ok:
            return True, "Data profil berhasil diperbarui!"
        return False, "Gagal memperbarui data profil!"

    @staticmethod
    def change_password(id_user, password_lama, password_baru, konfirmasi_baru):
        """Mengubah kata sandi pengguna dengan verifikasi password lama."""
        if not id_user:
            return False, "Pengguna tidak valid!"
        if not password_baru:
            return False, "Password baru wajib diisi!"
        if len(password_baru) < 6:
            return False, "Password baru minimal 6 karakter!"
        if password_baru != konfirmasi_baru:
            return False, "Konfirmasi password baru tidak sama!"

        row = BaseModel._fetch_one(
            "SELECT password, salt FROM users WHERE id_user = %s", (id_user,)
        )
        if not row:
            return False, "Data pengguna tidak ditemukan!"
        if not UserModel.verify_password(password_lama, row["salt"], row["password"]):
            return False, "Password lama tidak sesuai!"

        new_hash = UserModel.hash_password(password_baru, row["salt"])
        ok = BaseModel._execute_write(
            "UPDATE users SET password = %s WHERE id_user = %s",
            (new_hash, id_user),
        )
        if ok:
            return True, "Password berhasil diubah!"
        return False, "Gagal mengubah password!"

    @staticmethod
    def set_active(id_user, is_active):
        """Mengaktifkan atau menonaktifkan sebuah akun."""
        if not id_user:
            return False, "Pengguna tidak valid!"
        ok = BaseModel._execute_write(
            "UPDATE users SET is_active = %s WHERE id_user = %s",
            (1 if is_active else 0, id_user),
        )
        if ok:
            return True, "Status akun berhasil diperbarui!"
        return False, "Gagal memperbarui status akun!"

    @staticmethod
    def delete(id_user):
        """Menghapus akun pengguna."""
        if not id_user:
            return False, "Pengguna tidak valid!"
        ok = BaseModel._execute_write("DELETE FROM users WHERE id_user = %s", (id_user,))
        if ok:
            return True, "Akun pengguna berhasil dihapus!"
        return False, "Gagal menghapus akun pengguna!"
