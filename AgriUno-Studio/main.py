"""
AgriUno Edisi Studio - antarmuka dalam satu jendela.

Login, registrasi, dan ganti pengguna hanya pergantian tampilan.
Navigasi rail, tabel master-detail, pencarian langsung, formulir
modal, toast, dan alur status satu-klik. Struktur proyek:
config/ (konstanta, koneksi, kit antarmuka), models/ (kelas data
dan aturan bisnis), controllers/ (autentikasi dan orkestrasi),
serta views/ (splash, login, registrasi, dan halaman data).
"""

import contextlib
import logging
import os
import sys

import customtkinter as ctk

from config import constants, ui_kit
from config.mesin_database import siapkan_database
from controllers.auth_controller import AuthController, Session
from views.dashboard_view import DashboardView
from views.dialog_ubah_sandi import DialogUbahSandi
from views.distribusi_view import DistribusiView
from views.login_view import LoginView
from views.panen_view import PanenView
from views.pengguna_view import PenggunaView
from views.petani_view import PetaniView
from views.splash_view import SplashView

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")


class AgriUnoApp(ctk.CTk):
    """Satu jendela untuk seluruh alur aplikasi."""

    def __init__(self):
        super().__init__()
        self.title("AgriUno - Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal")
        # Ukuran jendela menyesuaikan skala DPI agar tidak melebihi layar.
        try:
            skala = self._get_window_scaling()
        except Exception:  # noqa: BLE001
            skala = 1.0
        lebar = min(1400, int(self.winfo_screenwidth() / skala) - 40)
        tinggi = min(780, int(self.winfo_screenheight() / skala) - 60)
        self.geometry("%dx%d" % (lebar, tinggi))
        self.minsize(1240, 680)
        self.configure(fg_color=ui_kit.LATAR)
        if os.path.exists(constants.IKON):
            with contextlib.suppress(Exception):
                self.iconbitmap(constants.IKON)

        self.sesi = Session()
        self.shell = None
        self.pages = {}
        self.nav_buttons = {}
        self.content = None
        self._tampilkan_splash()

    @property
    def user(self):
        """Profil pengguna aktif dari sesi."""
        return self.sesi.user

    # --------------------------------------------------------
    # API APLIKASI (katalog kelas dokumentasi teknis 4.7)
    # --------------------------------------------------------
    def show_page(self, page_name):
        """Berpindah ke halaman tertentu dan menyegarkan datanya."""
        if self.shell is not None:
            self.shell.pilih(page_name)

    def _build_sidebar(self):
        """Menyusun rail navigasi pada shell yang sedang aktif."""
        if self.shell is not None:
            return self.shell._bangun_rail()
        return None

    def _build_content(self):
        """Menyusun area konten pada shell yang sedang aktif."""
        if self.shell is not None:
            return self.shell._build_content()
        return None

    def keluar(self):
        """Mengakhiri sesi pengguna dan kembali ke halaman login (FR-06)."""
        AuthController.logout(self.sesi)
        self._tampilkan_login()

    # --------------------------------------------------------
    def _bersihkan(self):
        """Menghapus seluruh tampilan aktif pada jendela."""
        for anak in self.winfo_children():
            if isinstance(anak, ctk.CTkToplevel):
                continue
            anak.destroy()
        self.shell = None

    # --------------------------------------------------------
    def _tampilkan_splash(self):
        """Menampilkan animasi pemuatan sebagai tampilan pertama."""
        self._bersihkan()
        splash = SplashView(self, on_selesai=self._tampilkan_login)
        splash.pack(fill="both", expand=True)

    # --------------------------------------------------------
    def _tampilkan_login(self):
        """Menampilkan layar pembuka login."""
        self._bersihkan()
        login = LoginView(self, on_sukses=self._masuk)
        login.pack(fill="both", expand=True)

    # --------------------------------------------------------
    def _masuk(self, user):
        """Membangun shell utama setelah login berhasil."""
        self.sesi.set_user(user)
        self._bersihkan()
        self.shell = Shell(self)
        self.shell.pack(fill="both", expand=True)
        # Sinkronkan referensi halaman, tombol navigasi, dan area konten
        # sesuai katalog kelas pada dokumentasi teknis.
        self.pages = self.shell.halaman
        self.nav_buttons = self.shell.nav_tombol
        self.content = self.shell.konten

    # --------------------------------------------------------
    def ganti_pengguna(self):
        """Kembali ke layar login tanpa menutup aplikasi."""
        self.sesi.reset()
        self._tampilkan_login()

    # --------------------------------------------------------
    def ubah_kata_sandi(self):
        """Membuka formulir ubah kata sandi pengguna aktif (UC-09)."""
        DialogUbahSandi(self, on_selesai=None)


class Shell(ctk.CTkFrame):
    """Kerangka aplikasi: rail navigasi + area konten bertumpuk."""

    MENU = (
        ("dashboard", "Dashboard", "◧"),
        ("petani", "Data Petani", "☰"),
        ("panen", "Inventori Panen", "⬒"),
        ("distribusi", "Distribusi", "➤"),
    )

    #: Menu khusus Administrator (pemeliharaan akun pengguna).
    MENU_ADMIN = (("pengguna", "Kelola Pengguna", "⛨"),)

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.logo = ui_kit.gambar_logo(42)
        self.halaman = {}
        self.nav_tombol = {}
        self.konten = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._bangun_rail()

        konten = self._build_content()

        kelas_halaman = {
            "dashboard": DashboardView,
            "petani": PetaniView,
            "panen": PanenView,
            "distribusi": DistribusiView,
        }
        if AuthController.boleh(master.user, "hapus"):
            # Pemeliharaan akun pengguna hanya bagi Administrator.
            kelas_halaman["pengguna"] = PenggunaView
        for kunci, kelas in kelas_halaman.items():
            halaman = kelas(konten, master)
            halaman.grid(row=0, column=0, sticky="nsew")
            self.halaman[kunci] = halaman

        self.pilih("dashboard")

    # --------------------------------------------------------
    def _build_content(self):
        """Menyusun area konten tempat seluruh halaman ditumpuk."""
        konten = ctk.CTkFrame(self, fg_color="transparent")
        konten.grid(row=0, column=1, sticky="nsew")
        konten.grid_rowconfigure(0, weight=1)
        konten.grid_columnconfigure(0, weight=1)
        self.konten = konten
        return konten

    # --------------------------------------------------------
    def _bangun_rail(self):
        """Menyusun rail navigasi hijau di sisi kiri."""
        rail = ctk.CTkFrame(self, fg_color=ui_kit.HIJAU, corner_radius=0, width=236)
        rail.grid(row=0, column=0, sticky="nsew")
        rail.grid_propagate(False)

        merek = ctk.CTkFrame(rail, fg_color="transparent")
        merek.pack(fill="x", padx=22, pady=(26, 0))
        if self.logo:
            ctk.CTkLabel(merek, image=self.logo, text="").pack(anchor="w")
        ctk.CTkLabel(rail, text="AgriUno", font=(ui_kit.FONT, 23, "bold"), text_color="white").pack(
            anchor="w", padx=24
        )

        ctk.CTkFrame(rail, fg_color="#2f5d4a", height=1).pack(fill="x", padx=20, pady=(18, 18))
        ctk.CTkLabel(
            rail, text="MENU UTAMA", font=(ui_kit.FONT, 9, "bold"), text_color="#6f9884"
        ).pack(anchor="w", padx=25, pady=(14, 6))

        for kunci, label, _ikon in self.MENU:
            # Seluruh peran (termasuk baca-saja) tetap dapat melihat
            # semua halaman; pembatasan hak ditegakkan di dalam halaman.
            tombol = ctk.CTkButton(
                rail,
                text="   " + label,
                fg_color="transparent",
                text_color="#d7e6dd",
                hover_color=ui_kit.HIJAU_HOVER,
                anchor="w",
                height=42,
                corner_radius=10,
                font=(ui_kit.FONT, 13),
                command=lambda k=kunci: self.pilih(k),
            )
            tombol.pack(fill="x", padx=16, pady=3)
            self.nav_tombol[kunci] = tombol

        # Menu khusus Administrator: pemeliharaan akun pengguna.
        if AuthController.boleh(self.master.user, "hapus"):
            for kunci, label, _ikon in self.MENU_ADMIN:
                tombol = ctk.CTkButton(
                    rail,
                    text="   " + label,
                    fg_color="transparent",
                    text_color="#d7e6dd",
                    hover_color=ui_kit.HIJAU_HOVER,
                    anchor="w",
                    height=42,
                    corner_radius=10,
                    font=(ui_kit.FONT, 13),
                    command=lambda k=kunci: self.pilih(k),
                )
                tombol.pack(fill="x", padx=16, pady=3)
                self.nav_tombol[kunci] = tombol

        # --- Kartu pengguna aktif + tombol sesi ---
        kartu_user = ctk.CTkFrame(rail, fg_color="#16352a", corner_radius=12)
        kartu_user.pack(fill="x", padx=16, side="bottom", pady=(0, 10))

        tubuh = ctk.CTkFrame(kartu_user, fg_color="transparent")
        tubuh.pack(fill="x", padx=12, pady=12)
        user = self.master.user

        ctk.CTkLabel(
            tubuh,
            text=(user["nama"].strip()[:1].upper() or "?"),
            font=(ui_kit.FONT, 15, "bold"),
            text_color="white",
            fg_color=ui_kit.HIJAU_HOVER,
            corner_radius=999,
            width=40,
            height=40,
        ).pack(side="left", padx=(0, 10))

        info = ctk.CTkFrame(tubuh, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            info, text=user["nama"], font=(ui_kit.FONT, 12, "bold"), text_color="white", anchor="w"
        ).pack(fill="x")
        ctk.CTkLabel(
            info, text=user["label_peran"], font=(ui_kit.FONT, 10), text_color="#8fd8a8", anchor="w"
        ).pack(fill="x")

        tombol_sesi = ctk.CTkFrame(rail, fg_color="transparent")
        tombol_sesi.pack(side="bottom", fill="x", padx=16, pady=16)

        ctk.CTkButton(
            tombol_sesi,
            text="   Ganti Pengguna",
            fg_color="transparent",
            hover_color=ui_kit.HIJAU_HOVER,
            text_color="#c9ded2",
            border_width=1,
            border_color="#3d6b57",
            height=38,
            corner_radius=10,
            font=(ui_kit.FONT, 12),
            command=self.master.ganti_pengguna,
        ).pack(fill="x")
        ctk.CTkButton(
            tombol_sesi,
            text="   Ubah Kata Sandi",
            fg_color="transparent",
            hover_color=ui_kit.HIJAU_HOVER,
            text_color="#c9ded2",
            border_width=1,
            border_color="#3d6b57",
            height=38,
            corner_radius=10,
            font=(ui_kit.FONT, 12),
            command=self.master.ubah_kata_sandi,
        ).pack(fill="x", pady=(6, 0))
        ctk.CTkButton(
            tombol_sesi,
            text="   Keluar Aplikasi",
            fg_color="transparent",
            hover_color="#3a1f1f",
            text_color="#f2a7a7",
            border_width=1,
            border_color="#6b3a3a",
            height=38,
            corner_radius=10,
            font=(ui_kit.FONT, 12),
            command=self.master.keluar,
        ).pack(fill="x", pady=(6, 0))

    # --------------------------------------------------------
    def pilih(self, kunci):
        """Berpidah ke halaman dan menyegarkan datanya."""
        halaman = self.halaman[kunci]
        halaman.muat()
        halaman.tkraise()
        for k, tombol in self.nav_tombol.items():
            tombol.configure(fg_color=ui_kit.HIJAU_HOVER if k == kunci else "transparent")


def main():
    """Menjalankan aplikasi AgriUno edisi Studio.

    Sebelum jendela dibangun, mesin basis data dipastikan siap:
    bila MySQL belum berjalan, salinan mesin bawaan pada folder
    ``runtime`` dinyalakan dan ``database.sql`` diimpor otomatis,
    sehingga aplikasi langsung terbuka tanpa penyiapan manual.
    """
    _pasang_log_berkas()
    logging.getLogger(__name__).info("Aplikasi dimulai (frozen=%s)", getattr(sys, "frozen", False))
    berhasil, pesan = siapkan_database()
    if not berhasil:
        logging.error("Basis data belum siap: %s", pesan)
    aplikasi = AgriUnoApp()
    aplikasi.mainloop()


def _pasang_log_berkas():
    """Mencatat pesan aplikasi ke berkas log pada folder data pengguna.

    Membantu penelusuran pada komputer pengguna akhir tanpa konsol.
    """
    try:
        dasar = os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "AgriUnoStudio"
        )
        os.makedirs(dasar, exist_ok=True)
        handler = logging.FileHandler(os.path.join(dasar, "aplikasi.log"), encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logging.root.addHandler(handler)
        logging.root.setLevel(logging.INFO)
    except Exception:  # noqa: BLE001 - log adalah kenyamanan, bukan keharusan
        logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    main()