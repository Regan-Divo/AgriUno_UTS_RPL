"""
==========================================================
PENGUJIAN OTOMATIS - AUTENTIKASI (Modul 7)
==========================================================
Pengujian unit untuk modul autentikasi dan registrasi AgriUno.

Pengujian yang memerlukan koneksi basis data ditandai dengan
penanda ``@pytest.mark.db`` sehingga dapat dilewati secara
otomatis pada runner GitHub Actions yang tidak memiliki MySQL::

    pytest -v                    # menjalankan seluruh pengujian
    pytest -v -m "not db"        # hanya pengujian tanpa basis data
    pytest -v -m db              # hanya pengujian basis data

Konfigurasi penanda ``db`` berada pada berkas ``pytest.ini``.
"""

from contextlib import contextmanager

import pytest

from config.constants import ROLE_ADMIN, ROLE_OPERATOR, ROLE_PETANI
from controllers.auth_controller import AuthController, Session
from models.user_model import UserModel


# ============================================================
# 1. ALGORITMA HASHING SHA-256  (tidak memerlukan basis data)
# ============================================================
class TestHashing:
    """Pengujian konsistensi algoritma hashing kata sandi."""

    def test_hash_deterministik(self):
        """Hash untuk masukan yang sama harus selalu identik."""
        salt = "abcdef0123456789"
        pertama = UserModel.hash_password("admin123", salt)
        kedua = UserModel.hash_password("admin123", salt)
        assert pertama == kedua
        assert len(pertama) == 64

    def test_hash_berbeda_untuk_password_berbeda(self):
        """Password berbeda harus menghasilkan hash berbeda."""
        salt = "abcdef0123456789"
        assert UserModel.hash_password("admin123", salt) != UserModel.hash_password(
            "admin124", salt
        )

    def test_hash_berbeda_untuk_salt_berbeda(self):
        """Salt berbeda harus menghasilkan hash berbeda (efek salt)."""
        assert UserModel.hash_password("admin123", "salt11111111111111") != UserModel.hash_password(
            "admin123", "salt22222222222222"
        )

    def test_password_tidak_terkirim_apa_adanya(self):
        """Password asli tidak boleh muncul di dalam hash."""
        salt = "abcdef0123456789"
        hash_pw = UserModel.hash_password("rahasia123", salt)
        assert "rahasia123" not in hash_pw

    def test_verify_password_berhasil(self):
        """Password yang benar harus lolos verifikasi."""
        salt = "abcdef0123456789"
        hash_pw = UserModel.hash_password("admin123", salt)
        assert UserModel.verify_password("admin123", salt, hash_pw) is True

    def test_verify_password_gagal(self):
        """Password yang salah harus ditolak."""
        salt = "abcdef0123456789"
        hash_pw = UserModel.hash_password("admin123", salt)
        assert UserModel.verify_password("salah", salt, hash_pw) is False

    def test_verify_password_dengan_masukan_kosong(self):
        """Masukan kosong harus ditolak tanpa galat."""
        assert UserModel.verify_password("", "salt", "hash") is False
        assert UserModel.verify_password("password", "", "hash") is False

    def test_salt_acak_berbeda(self):
        """Dua salt yang dibangkitkan tidak boleh sama."""
        assert UserModel.generate_salt() != UserModel.generate_salt()


# ============================================================
# 2. OTORISASI BERBASIS PERAN (RBAC)
# ============================================================
class TestOtorisasi:
    """Pengujian peta hak akses tiap peran pengguna."""

    def test_admin_memiliki_akses_penuh(self):
        """Administrator wajib memiliki akses ke seluruh modul."""
        session = Session()
        session.set_user(
            {"id_user": 1, "username": "admin", "full_name": "Administrator", "role": ROLE_ADMIN}
        )
        assert session.boleh("bisa_kelola_petani") is True
        assert session.boleh("bisa_kelola_panen") is True
        assert session.boleh("bisa_kelola_distribusi") is True
        assert session.boleh("bisa_kelola_pengguna") is True

    def test_operator_dapat_mengelola_data_operasional(self):
        """Operator boleh mengelola data operasional, bukan data pengguna."""
        session = Session()
        session.set_user(
            {"id_user": 2, "username": "operator", "full_name": "Operator", "role": ROLE_OPERATOR}
        )
        assert session.boleh("bisa_kelola_petani") is True
        assert session.boleh("bisa_kelola_panen") is True
        assert session.boleh("bisa_kelola_distribusi") is True
        assert session.boleh("bisa_kelola_pengguna") is False

    def test_petani_hanya_akses_baca(self):
        """Peran Petani hanya boleh melihat dashboard."""
        session = Session()
        session.set_user(
            {"id_user": 3, "username": "petani", "full_name": "Petani", "role": ROLE_PETANI}
        )
        assert session.boleh("bisa_masuk_dashboard") is True
        assert session.boleh("bisa_kelola_petani") is False
        assert session.boleh("bisa_kelola_panen") is False
        assert session.boleh("bisa_kelola_distribusi") is False

    def test_peran_tidak_dikenal_berhak_default_readonly(self):
        """Peran yang tidak dikenal harus jatuh ke hak akses paling kecil."""
        session = Session()
        session.set_user(
            {"id_user": 9, "username": "anon", "full_name": "Anonim", "role": "hacker"}
        )
        assert session.boleh("bisa_kelola_petani") is False

    def test_sesi_kosong_berhak_tidak_ada(self):
        """Sesi yang belum aktif tidak memiliki hak akses apa pun."""
        session = Session()
        assert session.aktif() is False
        assert session.boleh("bisa_kelola_petani") is False

    def test_reset_mengosongkan_sesi(self):
        """Method reset harus menghapus seluruh data sesi."""
        session = Session()
        session.set_user(
            {"id_user": 1, "username": "admin", "full_name": "Administrator", "role": ROLE_ADMIN}
        )
        session.reset()
        assert session.aktif() is False
        assert session.username is None


# ============================================================
# 3. VALIDASI REGISTRASI (tidak memerlukan basis data)
# ============================================================
class _FakeCursor:
    """Kursor tiruan untuk menguji logika tanpa server MySQL."""

    def __init__(self):
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def fetchone(self):
        return None

    def fetchall(self):
        return []

    def close(self):
        pass


class TestValidasiRegistrasi:
    """Pengujian aturan validasi formulir registrasi."""

    @staticmethod
    def _patch(mp, username_taken=False):
        """Menyiapkan tiruan basis data untuk pengujian registrasi."""
        from config.database import DatabaseConnection
        from models.base_model import BaseModel

        @contextmanager
        def fake_cursor(dictionary=False, commit=False):
            yield _FakeCursor()

        mp.setattr(DatabaseConnection, "cursor", staticmethod(fake_cursor))
        mp.setattr(
            BaseModel,
            "_fetch_one",
            staticmethod(lambda *a, **k: {"id_user": 1} if username_taken else None),
        )

    def test_username_kosong_ditolak(self):
        """Username wajib diisi."""
        with pytest.MonkeyPatch.context() as mp:
            self._patch(mp)
            berhasil, pesan = UserModel.register(
                "", "rahasia123", "rahasia123", "Budi", ROLE_OPERATOR
            )
        assert berhasil is False
        assert "Username" in pesan

    def test_username_terlalu_pendek_ditolak(self):
        """Username minimal empat karakter."""
        with pytest.MonkeyPatch.context() as mp:
            self._patch(mp)
            berhasil, pesan = UserModel.register(
                "ab", "rahasia123", "rahasia123", "Budi", ROLE_OPERATOR
            )
        assert berhasil is False
        assert "minimal 4 karakter" in pesan

    def test_nama_lengkap_kosong_ditolak(self):
        """Nama lengkap wajib diisi."""
        with pytest.MonkeyPatch.context() as mp:
            self._patch(mp)
            berhasil, pesan = UserModel.register(
                "budi01", "rahasia123", "rahasia123", "", ROLE_OPERATOR
            )
        assert berhasil is False
        assert "Nama lengkap" in pesan

    def test_password_terlalu_pendek_ditolak(self):
        """Password minimal enam karakter."""
        with pytest.MonkeyPatch.context() as mp:
            self._patch(mp)
            berhasil, pesan = UserModel.register("budi01", "123", "123", "Budi", ROLE_OPERATOR)
        assert berhasil is False
        assert "minimal 6 karakter" in pesan

    def test_konfirmasi_password_tidak_sama_ditolak(self):
        """Konfirmasi password harus sama dengan password."""
        with pytest.MonkeyPatch.context() as mp:
            self._patch(mp)
            berhasil, pesan = UserModel.register(
                "budi01", "rahasia123", "rahasia124", "Budi", ROLE_OPERATOR
            )
        assert berhasil is False
        assert "Konfirmasi password" in pesan

    def test_peran_admin_tidak_boleh_didaftarkan(self):
        """Peran admin hanya dapat dibuat oleh pengelola basis data (BR-07)."""
        with pytest.MonkeyPatch.context() as mp:
            self._patch(mp)
            berhasil, pesan = UserModel.register(
                "budi01", "rahasia123", "rahasia123", "Budi", ROLE_ADMIN
            )
        assert berhasil is False
        assert "Administrator" in pesan

    def test_username_yang_sudah_dipakai_ditolak(self):
        """Username harus unik (BR-06)."""
        with pytest.MonkeyPatch.context() as mp:
            self._patch(mp, username_taken=True)
            berhasil, pesan = UserModel.register(
                "budi01", "rahasia123", "rahasia123", "Budi", ROLE_OPERATOR
            )
        assert berhasil is False
        assert "sudah digunakan" in pesan

    def test_peran_operator_diperbolehkan(self):
        """Peran operator boleh dipilih saat pendaftaran."""
        with pytest.MonkeyPatch.context() as mp:
            self._patch(mp)
            berhasil, pesan = UserModel.register(
                "budi01", "rahasia123", "rahasia123", "Budi", ROLE_OPERATOR
            )
        assert berhasil is True
        assert "budi01" in pesan

    def test_peran_petani_diperbolehkan(self):
        """Peran petani juga boleh dipilih saat pendaftaran."""
        with pytest.MonkeyPatch.context() as mp:
            self._patch(mp)
            berhasil, pesan = UserModel.register(
                "budi01", "rahasia123", "rahasia123", "Budi", ROLE_PETANI
            )
        assert berhasil is True


# ============================================================
# 4. AUTENTIKASI TERHUBUNG KE BASIS DATA
# ============================================================
@pytest.mark.db
class TestAutentikasiDatabase:
    """Pengujian login terhadap tabel ``users`` (memerlukan MySQL)."""

    def test_login_dengan_kredensial_benar(self):
        """Akun admin demo harus berhasil login."""
        hasil = AuthController.login("admin", "admin123")
        assert hasil[0] is True
        assert AuthController.session.role == ROLE_ADMIN
        AuthController.logout()

    def test_login_dengan_password_salah(self):
        """Password salah harus ditolak."""
        hasil = AuthController.login("admin", "passwordsalah")
        assert hasil[0] is False
        assert "salah" in hasil[1].lower()

    def test_login_username_tidak_ada(self):
        """Username yang tidak terdaftar harus ditolak."""
        hasil = AuthController.login("tidakada99", "apa_saja")
        assert hasil[0] is False

    def test_login_dengan_masukan_kosong(self):
        """Masukan kosong harus ditolak tanpa galat."""
        assert AuthController.login("", "")[0] is False
