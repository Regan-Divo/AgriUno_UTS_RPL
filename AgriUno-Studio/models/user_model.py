"""
Model autentikasi, registrasi, dan pemeliharaan akun pengguna
pada tabel users.

Kata sandi disimpan sebagai hash SHA-256 bersalt dengan skema
identik aplikasi utama sehingga akun dapat dipakai di kedua
aplikasi.
"""

import hashlib
import hmac
import logging
import secrets

import mysql.connector

from config.constants import HAK_AKSES, LABEL_PERAN, ROLE_OPERATOR, ROLE_PETANI
from config.database import DatabaseTidakTersedia, kursor

logger = logging.getLogger(__name__)


class UserModel:
    """Model data dan autentikasi pengguna (tabel users)."""

    # --------------------------------------------------------
    # Helper kata sandi
    # --------------------------------------------------------
    @staticmethod
    def hash_password(password, salt):
        """SHA-256 dari (salt + password) - kompatibel aplikasi utama."""
        if password is None or salt is None:
            return ""
        return hashlib.sha256((salt + str(password)).encode("utf-8")).hexdigest()

    @staticmethod
    def generate_salt():
        """Membangkitkan salt acak sepanjang 16 byte."""
        return secrets.token_hex(16)

    @staticmethod
    def verify_password(password, salt, stored_hash):
        """Memeriksa kecocokan kata sandi dengan hash tersimpan."""
        if password is None or salt is None or not stored_hash:
            return False
        kandidat = UserModel.hash_password(password, salt)
        return hmac.compare_digest(kandidat, stored_hash)

    # --------------------------------------------------------
    # Autentikasi dan registrasi
    # --------------------------------------------------------
    @staticmethod
    def authenticate(username, password):
        """Memverifikasi kredensial. Mengembalikan (ok, pesan, user)."""
        username = (username or "").strip()
        if not username or not password:
            return False, "Username dan password wajib diisi!", None

        try:
            with kursor(commit=False) as cur:
                cur.execute(
                    "SELECT id_user, username, password, salt, full_name, role, is_active "
                    "FROM users WHERE username = %s",
                    (username,),
                )
                row = cur.fetchone()
        except DatabaseTidakTersedia as exc:
            return False, "Koneksi database gagal: %s" % exc, None

        if row is None:
            return False, "Username tidak ditemukan!", None
        if not int(row["is_active"] or 0):
            return False, "Akun ini tidak aktif. Hubungi Administrator.", None

        if not UserModel.verify_password(password, row["salt"], row["password"]):
            return False, "Password salah!", None

        user = {
            "id_user": row["id_user"],
            "username": row["username"],
            "nama": row["full_name"] or row["username"],
            "role": row["role"] if row["role"] in HAK_AKSES else ROLE_PETANI,
            "label_peran": LABEL_PERAN.get(row["role"], "Pengguna"),
        }
        return True, "Selamat datang, %s!" % user["nama"], user

    @staticmethod
    def register(nama, username, password, konfirmasi, role):
        """Mendaftarkan akun khusus baru (peran operator/petani, BR-07).

        Kata sandi disimpan sebagai hash SHA-256 bersalt - skema identik
        dengan aplikasi utama sehingga akun dapat dipakai di kedua aplikasi.
        """
        nama = " ".join(str(nama or "").split())
        username = (username or "").strip().lower()
        if not nama or not username or not password or not konfirmasi:
            return False, "Seluruh kolom wajib diisi!"
        if len(username) < 4 or not all(c.isalnum() or c in "._" for c in username):
            return False, "Username minimal 4 karakter (huruf, angka, titik, garis bawah)."
        if len(password) < 6:
            return False, "Password minimal 6 karakter!"
        if password != konfirmasi:
            return False, "Konfirmasi password tidak sama dengan password!"
        if role not in (ROLE_OPERATOR, ROLE_PETANI):
            return False, "Peran 'admin' tidak dapat dipilih saat pendaftaran."

        salt = UserModel.generate_salt()
        hash_sandi = UserModel.hash_password(password, salt)
        try:
            with kursor(commit=True) as cur:
                cur.execute("SELECT id_user FROM users WHERE username = %s", (username,))
                if cur.fetchone():
                    return False, "Username '%s' sudah dipakai pengguna lain!" % username
                cur.execute(
                    "INSERT INTO users (username, password, salt, full_name, role, is_active) "
                    "VALUES (%s, %s, %s, %s, %s, 1)",
                    (username, hash_sandi, salt, nama, role),
                )
            return True, "Akun '%s' berhasil didaftarkan. Silakan masuk." % username
        except DatabaseTidakTersedia as exc:
            return False, "Koneksi database gagal: %s" % exc
        except mysql.connector.Error as err:
            logger.error("daftar_pengguna: %s", err)
            return False, "Terjadi kesalahan database: %s" % err

    # --------------------------------------------------------
    # Pemeliharaan akun (oleh Administrator)
    # --------------------------------------------------------
    @staticmethod
    def get_all(cari=""):
        """Mengambil seluruh akun pengguna, opsional dengan kata kunci."""
        pola = "%{}%".format((cari or "").strip())
        try:
            with kursor(commit=False) as cur:
                cur.execute(
                    "SELECT id_user, username, full_name, role, is_active, created_at "
                    "FROM users WHERE username LIKE %s OR full_name LIKE %s "
                    "ORDER BY id_user",
                    (pola, pola),
                )
                return cur.fetchall()
        except DatabaseTidakTersedia as exc:
            logger.error("daftar_akun: %s", exc)
            return []

    @staticmethod
    def get_by_username(username):
        """Mengambil satu akun berdasarkan username."""
        try:
            with kursor(commit=False) as cur:
                cur.execute(
                    "SELECT id_user, username, full_name, role, is_active, created_at "
                    "FROM users WHERE username = %s",
                    ((username or "").strip().lower(),),
                )
                return cur.fetchone()
        except DatabaseTidakTersedia as exc:
            logger.error("akun: %s", exc)
            return None

    @staticmethod
    def username_exists(username, kecuali_id=None):
        """True bila username sudah dipakai akun lain."""
        try:
            with kursor(commit=False) as cur:
                if kecuali_id:
                    cur.execute(
                        "SELECT id_user FROM users WHERE username = %s AND id_user <> %s",
                        ((username or "").strip().lower(), kecuali_id),
                    )
                else:
                    cur.execute(
                        "SELECT id_user FROM users WHERE username = %s",
                        ((username or "").strip().lower(),),
                    )
                return cur.fetchone() is not None
        except DatabaseTidakTersedia:
            return False

    @staticmethod
    def update_profile(id_user, nama):
        """Memperbarui nama lengkap pengguna."""
        nama = " ".join(str(nama or "").split())
        if not nama:
            return False, "Nama lengkap wajib diisi!"
        try:
            with kursor(commit=True) as cur:
                cur.execute(
                    "UPDATE users SET full_name = %s WHERE id_user = %s",
                    (nama, id_user),
                )
            return True, "Profil pengguna berhasil diperbarui!"
        except DatabaseTidakTersedia as exc:
            return False, "Koneksi database gagal: %s" % exc

    @staticmethod
    def change_password(user, sandi_lama, sandi_baru, konfirmasi):
        """Mengubah kata sandi pengguna yang sedang login (UC-09).

        Kata sandi lama diverifikasi terhadap hash yang tersimpan,
        kemudian kata sandi baru disimpan dengan salt yang sama
        sesuai ketentuan dokumentasi teknis.
        """
        if not user:
            return False, "Sesi pengguna tidak ditemukan!"
        sandi_lama = sandi_lama or ""
        sandi_baru = sandi_baru or ""
        konfirmasi = konfirmasi or ""
        if not sandi_lama or not sandi_baru:
            return False, "Seluruh kolom wajib diisi!"
        if len(sandi_baru) < 6:
            return False, "Password baru minimal 6 karakter!"
        if sandi_baru != konfirmasi:
            return False, "Konfirmasi password baru tidak sama dengan password baru!"
        if sandi_lama == sandi_baru:
            return False, "Kata sandi baru harus berbeda dari kata sandi lama!"

        try:
            with kursor(commit=False) as cur:
                cur.execute(
                    "SELECT password, salt FROM users WHERE id_user = %s",
                    (user["id_user"],),
                )
                row = cur.fetchone()
        except DatabaseTidakTersedia as exc:
            return False, "Koneksi database gagal: %s" % exc

        if row is None:
            return False, "Data pengguna tidak ditemukan!"
        if not UserModel.verify_password(sandi_lama, row["salt"], row["password"]):
            return False, "Kata sandi lama tidak sesuai!"

        hash_baru = UserModel.hash_password(sandi_baru, row["salt"])
        try:
            with kursor(commit=True) as cur:
                cur.execute(
                    "UPDATE users SET password = %s WHERE id_user = %s",
                    (hash_baru, user["id_user"]),
                )
            return True, "Kata sandi berhasil diperbarui!"
        except DatabaseTidakTersedia as exc:
            return False, "Koneksi database gagal: %s" % exc
        except mysql.connector.Error as err:
            logger.error("ubah_kata_sandi: %s", err)
            return False, "Terjadi kesalahan database: %s" % err

    @staticmethod
    def update_password(user, sandi_lama, sandi_baru, konfirmasi):
        """Alias ``change_password`` untuk kompatibilitas pemanggilan."""
        return UserModel.change_password(user, sandi_lama, sandi_baru, konfirmasi)

    @staticmethod
    def set_active(id_user, aktif=True):
        """Mengaktifkan atau menonaktifkan sebuah akun."""
        try:
            with kursor(commit=True) as cur:
                cur.execute(
                    "UPDATE users SET is_active = %s WHERE id_user = %s",
                    (1 if aktif else 0, id_user),
                )
            return True, "Akun berhasil %s." % ("diaktifkan" if aktif else "dinonaktifkan")
        except DatabaseTidakTersedia as exc:
            return False, "Koneksi database gagal: %s" % exc

    @staticmethod
    def delete(id_user):
        """Menghapus sebuah akun pengguna."""
        try:
            with kursor(commit=True) as cur:
                cur.execute("DELETE FROM users WHERE id_user = %s", (id_user,))
            return True, "Akun pengguna berhasil dihapus!"
        except DatabaseTidakTersedia as exc:
            return False, "Koneksi database gagal: %s" % exc
        except mysql.connector.Error as err:
            logger.error("hapus_akun: %s", err)
            return False, "Gagal menghapus akun: %s" % err
