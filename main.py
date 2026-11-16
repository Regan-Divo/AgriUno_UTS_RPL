"""
==========================================================
APLIKASI UTAMA DESKTOP - AGRIUNO
==========================================================
Titik masuk aplikasi AgriUno.

Alur jendela::

    SplashView  ->  LoginView  ->  AgriUnoApp
                      ^              |
                      |              v
                  RegisterView   (Keluar / logout)

* ``SplashView`` menampilkan logo dan animasi pembukaan.
* ``LoginView`` memverifikasi kredensial terhadap tabel ``users``.
* ``RegisterView`` digunakan pengguna baru membuat akun khusus.
* ``AgriUnoApp`` adalah jendela utama yang memuat sidebar navigasi
  dan seluruh halaman aplikasi.

Seluruh halaman bersifat turunan ``CTkFrame`` dan ditumpuk pada
satu area konten, lalu ditampilkan dengan ``tkraise()``.
"""

import logging

import customtkinter as ctk

from config.constants import (
    APP_NAME,
    COLOR_BG,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    WIN_MAIN,
)
from config.mesin_database import siapkan_database
from config.ui_kit import FONT, TS_BADAN, TS_KECIL, gambar_logo
from config.window_utils import pasang_ikon
from controllers.auth_controller import AuthController
from controllers.controller import AgriUnoController
from views.dashboard_view import DashboardView
from views.distribusi_view import DistribusiView
from views.login_view import LoginView
from views.panen_view import PanenView
from views.petani_view import PetaniView
from views.register_view import RegisterView
from views.splash_view import SplashView

logger = logging.getLogger(__name__)

#: Penanda bahwa pengguna nyata-nyata ingin menutup aplikasi.
#: Nilai ini membedakan dua keadaan yang sama-sama menutup jendela
#: utama: pengguna menekan tombol "Keluar" (aplikasi harus berhenti)
#: atau pengguna menekan tombol "Ganti Pengguna" (hanya sesi yang
#: berakhir, jendela login ditampilkan kembali).
keluar_diminta = False

#: Penanda bahwa pengguna menekan "Ganti Pengguna": sesi diakhiri
#: namun aplikasi tetap berjalan dan jendela login ditampilkan kembali.
ganti_diminta = False

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")


class AgriUnoApp(ctk.CTk):
    """Jendela utama aplikasi AgriUno."""

    def __init__(self, user=None):
        super().__init__()
        self.user = user or AuthController.current_user()

        self.title("%s - Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal" % APP_NAME)
        self.geometry("%dx%d" % WIN_MAIN)
        self.minsize(1080, 640)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        pasang_ikon(self)

        # Menutup jendela utama dengan tombol X juga mengakhiri sesi.
        self.protocol("WM_DELETE_WINDOW", self.keluar)

        self._build_sidebar()
        self._build_content()
        self.show_page("dashboard")

    # ========================================================
    # Sidebar
    # ========================================================
    def _build_sidebar(self):
        """Menyusun sidebar navigasi dan panel informasi sesi."""
        sidebar = ctk.CTkFrame(self, width=250, fg_color=COLOR_PRIMARY, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # --- Panel merek (logo + nama) ---
        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(26, 0))

        logo = gambar_logo(52)
        if logo is not None:
            ctk.CTkLabel(brand, image=logo, text="").pack(anchor="w")

        ctk.CTkLabel(
            sidebar,
            text=APP_NAME,
            font=(FONT, 25, "bold"),
            text_color="white",
        ).pack(anchor="w", padx=22)

        ctk.CTkLabel(
            sidebar,
            text="Manajemen Pertanian Lokal",
            font=(FONT, TS_KECIL + 1),
            text_color="#a7c6b4",
        ).pack(anchor="w", padx=23, pady=(0, 18))

        # --- Garis pemisah halus ---
        ctk.CTkFrame(sidebar, fg_color="#2f5d4a", height=1).pack(fill="x", padx=20)

        ctk.CTkLabel(
            sidebar,
            text="MENU UTAMA",
            font=(FONT, TS_KECIL - 1, "bold"),
            text_color="#6f9884",
        ).pack(anchor="w", padx=23, pady=(14, 4))

        # --- Menu navigasi (disesuaikan dengan hak akses peran) ---
        self.nav_buttons = {}

        menu = [
            ("dashboard", "Dashboard"),
            ("petani", "Kelola Petani"),
            ("panen", "Inventori Panen"),
            ("distribusi", "Distribusi"),
        ]

        for key, label in menu:
            if key != "dashboard" and not AuthController.boleh("bisa_kelola_%s" % key):
                continue
            button = ctk.CTkButton(
                sidebar,
                text="   " + label,
                fg_color="transparent",
                text_color="#d7e6dd",
                hover_color=COLOR_PRIMARY_HOVER,
                anchor="w",
                height=40,
                corner_radius=10,
                font=(FONT, TS_BADAN + 1),
                command=lambda k=key: self.show_page(k),
            )
            button.pack(fill="x", padx=16, pady=3)
            self.nav_buttons[key] = button

        # --- Panel profil pengguna aktif ---
        self._build_user_panel(sidebar)

        # --- Tombol keluar ---
        footer = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=16, pady=16)

        ctk.CTkButton(
            footer,
            text="   Ganti Pengguna",
            fg_color="transparent",
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="#c9ded2",
            border_width=1,
            border_color="#3d6b57",
            height=38,
            corner_radius=10,
            font=(FONT, TS_BADAN),
            command=self.ganti_pengguna,
        ).pack(fill="x")

        ctk.CTkButton(
            footer,
            text="   Keluar Aplikasi",
            fg_color="transparent",
            hover_color="#3a1f1f",
            text_color="#f2a7a7",
            border_width=1,
            border_color="#6b3a3a",
            height=38,
            corner_radius=10,
            font=(FONT, TS_BADAN),
            command=self.keluar,
        ).pack(fill="x", pady=(6, 0))

    # ------------------------------------------------------------
    def _build_user_panel(self, sidebar):
        """Menyusun panel informasi pengguna yang sedang login."""
        session = AuthController.session

        panel = ctk.CTkFrame(sidebar, fg_color="#16352a", corner_radius=12)
        panel.pack(fill="x", padx=16, pady=(0, 12), side="bottom")

        tubuh = ctk.CTkFrame(panel, fg_color="transparent")
        tubuh.pack(fill="x", padx=14, pady=12)

        # --- Avatar lingkaran dengan inisial ---
        nama = session.full_name or session.username or "-"
        inisial = nama.strip()[:1].upper() or "?"

        ctk.CTkLabel(
            tubuh,
            text=inisial,
            font=(FONT, 15, "bold"),
            text_color="white",
            fg_color=COLOR_PRIMARY_HOVER,
            corner_radius=999,
            width=40,
            height=40,
        ).pack(side="left", padx=(0, 10))

        info = ctk.CTkFrame(tubuh, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            info,
            text=nama,
            font=(FONT, TS_BADAN, "bold"),
            text_color="white",
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            info,
            text=session.label_peran,
            font=(FONT, TS_KECIL),
            text_color="#8fd8a8",
            anchor="w",
        ).pack(fill="x")

    # ========================================================
    # Area konten
    # ========================================================
    def _build_content(self):
        """Membangun area konten dan menumpuk seluruh halaman."""
        self.content = ctk.CTkFrame(self, fg_color=COLOR_BG, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.pages = {}
        for page_class in (DashboardView, PetaniView, PanenView, DistribusiView):
            page = page_class(parent=self.content, controller=AgriUnoController)
            self.pages[page_class.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

    # ========================================================
    # Navigasi
    # ========================================================
    def show_page(self, page_name):
        """Berpindah ke halaman yang dipilih dan memuat datanya."""
        mapping = {
            "dashboard": "DashboardView",
            "petani": "PetaniView",
            "panen": "PanenView",
            "distribusi": "DistribusiView",
        }
        target = self.pages.get(mapping.get(page_name))
        if not target:
            return

        if hasattr(target, "refresh_data"):
            target.refresh_data()
        elif hasattr(target, "load_data"):
            target.load_data()
        elif hasattr(target, "load_table"):
            target.load_table()

        target.tkraise()
        self._tandai_menu_aktif(page_name)

    # ------------------------------------------------------------
    def _tandai_menu_aktif(self, page_name):
        """Memberi penekanan visual pada tombol menu yang aktif."""
        for key, button in self.nav_buttons.items():
            if key == page_name:
                button.configure(fg_color=COLOR_PRIMARY_HOVER)
            else:
                button.configure(fg_color="transparent")

    # ========================================================
    # Sesi
    # ========================================================
    def keluar(self):
        """Mengakhiri sesi dan MENUTUP SELURUH APLIKASI.

        Tombol "Keluar" dan tombol X pada title bar sama-sama
        menutup aplikasi, bukan hanya menutup jendela utama. Tanpa
        penanda ini, alur login akan berulang dan jendela login
        terus-muncul menggantung.
        """
        global keluar_diminta
        keluar_diminta = True
        AuthController.logout()
        try:
            self.destroy()
        except Exception as exc:  # noqa: BLE001
            logger.error("Galat saat menutup jendela utama: %s", exc)

    # ------------------------------------------------------------
    def ganti_pengguna(self):
        """Mengakhiri sesi namun aplikasi tetap berjalan.

        Jendela login ditampilkan kembali sehingga pengguna lain
        dapat masuk tanpa menutup aplikasi.
        """
        global keluar_diminta, ganti_diminta
        keluar_diminta = False
        ganti_diminta = True
        AuthController.logout()
        try:
            self.destroy()
        except Exception as exc:  # noqa: BLE001
            logger.error("Galat saat menutup jendela utama: %s", exc)


# ============================================================
# Alur jendela
# ============================================================
def jalankan_splash():
    """Menjalankan jendela pemuatan hingga animasi selesai.

    Fungsi ini memblokir sampai jendela splash ditutup, sehingga
    pemanggil dapat melanjutkan ke jendela berikutnya setelah
    animasi benar-benar selesai.
    """
    splash = SplashView()
    splash.mainloop()


def jalankan_login():
    """Menjalankan jendela login dan jendela utama terkait.

    Alur kendalinya:

    * Jendela login ditutup tanpa berhasil login  -> aplikasi berhenti.
    * Pengguna menekan tombol "Keluar"            -> aplikasi berhenti.
    * Pengguna menekan tombol "Ganti Pengguna"    -> jendela login
      ditampilkan kembali tanpa menutup aplikasi.
    """
    global keluar_diminta, ganti_diminta

    while True:
        keluar_diminta = False
        ganti_diminta = False

        login = LoginView(
            on_login_success=_buka_jendela_utama,
            on_open_register=_buka_registrasi,
        )
        login.mainloop()

        # Pengguna menekan tombol "Keluar" -> hentikan aplikasi.
        if keluar_diminta:
            break

        # Pengguna menekan "Ganti Pengguna" -> tampilkan login kembali.
        if ganti_diminta:
            continue

        # Jendela utama ditutup padahal sesi masih aktif -> tampilkan
        # login kembali sebagai jaring pengaman.
        if AuthController.session.aktif():
            continue

        # Jendela login ditutup tanpa login -> hentikan aplikasi.
        break


def jalankan_aplikasi():
    """Menjalankan rangkaian penuh jendela aplikasi AgriUno.

    Sebelum jendela apa pun ditampilkan, mesin basis data dipastikan
    siap: bila MySQL belum berjalan, salinan mesin bawaan pada folder
    ``runtime`` dinyalakan dan ``database.sql`` diimpor otomatis,
    sehingga aplikasi dapat langsung dibuka tanpa penyiapan manual.
    """
    berhasil, pesan = siapkan_database()
    if not berhasil:
        logger.error("Basis data belum siap: %s", pesan)
    jalankan_splash()
    jalankan_login()


def _buka_jendela_utama(user):
    """Membuka jendela utama setelah login berhasil."""
    app = AgriUnoApp(user=user)
    app.mainloop()


def _buka_registrasi(master=None):
    """Membuka jendela registrasi dari jendela login.

    Setelah registrasi berhasil, jendela registrasi ditutup secara
    otomatis sehingga pengguna dapat langsung melanjutkan ke login.
    """
    window = RegisterView(on_success=None, on_back=None)
    window.on_success = window.destroy
    window.on_back = None

    if master is not None:
        try:
            window.transient(master)
        except Exception as exc:  # noqa: BLE001
            logger.error("Galat saat mengaitkan jendela registrasi: %s", exc)

    window.mainloop()


if __name__ == "__main__":
    jalankan_aplikasi()
