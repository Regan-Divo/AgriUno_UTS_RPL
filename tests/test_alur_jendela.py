"""
==========================================================
PENGUJIAN OTOMATIS - ALUR JENDELA AgriUno
==========================================================
Memverifikasi alur perpindahan jendela pada ``main.py`` tanpa
menjalankan Tk yang sesungguhnya: ``LoginView`` dan ``AgriUnoApp``
ditirukan dengan kelas palsu yang mengikuti urutan yang sama.

Skenario yang dijaga:

* Login berhasil  -> jendela utama terbuka.
* "Keluar Aplikasi" di jendela utama -> seluruh aplikasi berhenti.
* "Ganti Pengguna" di jendela utama -> kembali ke jendela login
  (bug sebelumnya: aplikasi langsung ter-tutup seluruhnya).
"""

import pytest

import main
from controllers.auth_controller import AuthController


class _JendelaPalsu:
    """Kelas dasar jendela tiruan yang meniru siklus mainloop()."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def mainloop(self):
        return None


class TestAlurJendela:
    """Pengujian siklus login -> jendela utama -> keluar/ganti."""

    def _jalankan(self, aksi_jendela_utama, batas=5):
        """Menjalankan loop login dengan jendela tiruan.

        ``aksi_jendela_utama`` menerima nomor iterasi dan harus
        mengembalikan "ganti", "keluar", atau "tutup-login".
        """
        iterasi = {"login": 0, "utama": 0}

        class LoginPalsu(_JendelaPalsu):
            def mainloop(self):
                iterasi["login"] += 1
                if iterasi["login"] > batas:
                    pytest.fail("Loop login tidak berhenti (lebih dari %d kali)" % batas)
                callback = self.kwargs.get("on_login_success")
                if callable(callback):
                    callback(None)

        class AppPalsu(_JendelaPalsu):
            def mainloop(self):
                iterasi["utama"] += 1
                aksi_jendela_utama(iterasi["utama"])

        asli_login, asli_app = main.LoginView, main.AgriUnoApp
        try:
            main.LoginView = LoginPalsu
            main.AgriUnoApp = AppPalsu
            main.jalankan_login()
        finally:
            main.LoginView, main.AgriUnoApp = asli_login, asli_app
        return iterasi

    def setup_method(self):
        """Memastikan sesi bersih sebelum tiap pengujian."""
        AuthController.logout()

    def test_ganti_pengguna_kembali_ke_login(self):
        """Bug: Ganti Pengguna harus menampilkan login, bukan menutup aplikasi."""

        def aksi(ke_i):
            if ke_i == 1:
                main.ganti_diminta = True
                AuthController.logout()
                return
            # Iterasi kedua harus terjadi; akhiri dengan keluar.
            main.keluar_diminta = True
            AuthController.logout()

        hasil = self._jalankan(aksi)
        assert hasil["login"] == 2, "Setelah Ganti Pengguna, jendela login harus muncul lagi"
        assert main.keluar_diminta is True

    def test_keluar_menghentikan_aplikasi(self):
        """Tombol Keluar Aplikasi menghentikan loop sepenuhnya."""

        def aksi(ke_i):
            main.keluar_diminta = True
            AuthController.logout()

        hasil = self._jalankan(aksi)
        assert hasil["login"] == 1
        assert hasil["utama"] == 1

    def test_login_ditutup_tanpa_berhasil_menghentikan_aplikasi(self):
        """Menutup jendela login tanpa login sukses -> aplikasi berhenti."""

        def aksi(ke_i):  # jendela utama tidak pernah terbuka
            pytest.fail("Jendela utama tidak seharusnya terbuka")

        # LoginPalsu menutup tanpa callback sukses.
        class LoginTutupPalsu(_JendelaPalsu):
            def mainloop(self):
                AuthController.logout()  # sesi tetap kosong

        asli_login = main.LoginView
        asli_app = main.AgriUnoApp
        try:
            main.LoginView = LoginTutupPalsu
            main.AgriUnoApp = _JendelaPalsu
            main.jalankan_login()
        finally:
            main.LoginView, main.AgriUnoApp = asli_login, asli_app
        assert AuthController.session.aktif() is False
