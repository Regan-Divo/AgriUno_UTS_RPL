"""
=========================================================
ANTARMUKA LOGIN - AGRIUNO  (Modul 7)
=========================================================
Jendela login AgriUno bergaya split-screen:

* Panel kiri  : panel merek berlatar hijau tua berisi logo,
  nama aplikasi, dan ringkasan kemampuan sistem.
* Panel kanan : formulir kredensial dengan label di atas
  isian, penyingkap kata sandi, dan pesan galat inline.

Logika autentikasi tidak berubah dibanding versi UTS/UAS
sebelumnya: ``AuthController.login()`` memverifikasi kredensial
terhadap tabel ``users`` dengan hash SHA-256 bersalt dan
``hmac.compare_digest``.
"""

import customtkinter as ctk

from config.constants import (
    APP_NAME,
    APP_RELEASE,
    APP_TAGLINE,
    APP_VERSION,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    WIN_LOGIN,
)
from config.ui_kit import (
    CORNER_INPUT,
    FONT,
    TINGGI_INPUT,
    TS_BADAN,
    TS_DISPLAY,
    TS_KECIL,
    WARNA_GARIS,
    WARNA_REDUP,
    WARNA_TEBEL,
    bidang_isian,
    gambar_logo,
)
from config.window_utils import pasang_ikon
from controllers.auth_controller import AuthController

#: Panel kiri (panel merek) dalam piksel.
LEBAR_PANEL_MEREK = 388


class LoginView(ctk.CTk):
    """Jendela login AgriUno."""

    def __init__(self, on_login_success=None, on_open_register=None):
        super().__init__()
        self.on_login_success = on_login_success
        self.on_open_register = on_open_register

        self.title("%s - Login" % APP_NAME)
        self.geometry("%dx%d" % WIN_LOGIN)
        self.resizable(False, False)
        self.configure(fg_color="#e9efeb")
        pasang_ikon(self)

        self._build_ui()
        self.bind("<Return>", lambda _event: self.proses_login())
        self.after(80, lambda: self.e_user.focus_set())

    # ========================================================
    # Antarmuka
    # ========================================================
    def _build_ui(self):
        """Menyusun dua panel jendela login."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._panel_merek()
        self._panel_formulir()

    # ------------------------------------------------------------
    def _panel_merek(self):
        """Panel kiri: identitas dan ringkasan kemampuan sistem."""
        panel = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY, corner_radius=0, width=LEBAR_PANEL_MEREK)
        panel.grid(row=0, column=0, sticky="nsew")
        panel.grid_propagate(False)

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=34, pady=34)

        logo = gambar_logo(78)
        if logo is not None:
            ctk.CTkLabel(inner, image=logo, text="").pack(anchor="w", pady=(6, 10))

        ctk.CTkLabel(
            inner,
            text=APP_NAME,
            font=(FONT, TS_DISPLAY, "bold"),
            text_color="white",
        ).pack(anchor="w")

        ctk.CTkLabel(
            inner,
            text=APP_TAGLINE,
            font=(FONT, TS_KECIL + 1),
            text_color="#b9d4c4",
            justify="left",
            wraplength=290,
        ).pack(anchor="w", pady=(2, 26))

        # Ringkasan kemampuan sistem.
        for fitur in (
            "Pencatatan data petani dan lot panen",
            "Alokasi distribusi dengan kontrol stok",
            "Keamanan akun SHA-256 dan kontrol peran",
        ):
            baris = ctk.CTkFrame(inner, fg_color="transparent")
            baris.pack(fill="x", pady=5)

            ctk.CTkLabel(
                baris,
                text="✓",
                font=(FONT, TS_BADAN, "bold"),
                text_color="#8fe3a9",
                width=22,
                anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                baris,
                text=fitur,
                font=(FONT, TS_BADAN),
                text_color="#e8f2ec",
                anchor="w",
                wraplength=280,
                justify="left",
            ).pack(side="left", fill="x", expand=True)

        # Catatan bawah panel merek.
        bawah = ctk.CTkFrame(panel, fg_color="transparent")
        bawah.pack(side="bottom", fill="x", padx=34, pady=20)
        ctk.CTkLabel(
            bawah,
            text="%s  •  Universitas Tadulako" % APP_RELEASE,
            font=(FONT, TS_KECIL),
            text_color="#7fa894",
        ).pack(anchor="w")

    # ------------------------------------------------------------
    def _panel_formulir(self):
        """Panel kanan: formulir kredensial."""
        panel = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        panel.grid(row=0, column=1, sticky="nsew")

        frame = ctk.CTkFrame(panel, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=64, pady=40)

        ctk.CTkLabel(
            frame,
            text="Selamat Datang Kembali",
            font=(FONT, TS_DISPLAY - 3, "bold"),
            text_color=WARNA_TEBEL,
        ).pack(anchor="w")

        ctk.CTkLabel(
            frame,
            text="Masuk untuk melanjutkan pengelolaan gudang Anda.",
            font=(FONT, TS_BADAN),
            text_color=WARNA_REDUP,
        ).pack(anchor="w", pady=(2, 24))

        # --- Bidang username ---
        kolom_user, self.e_user = bidang_isian(frame, "Username", "Masukkan username", lebar=380)
        kolom_user.pack(fill="x")

        # --- Bidang password dengan penyingkap ---
        baris_pass = ctk.CTkFrame(frame, fg_color="transparent")
        baris_pass.pack(fill="x", pady=(16, 0))

        atas_pass = ctk.CTkFrame(baris_pass, fg_color="transparent")
        atas_pass.pack(fill="x")
        ctk.CTkLabel(
            atas_pass,
            text="Password *",
            font=(FONT, TS_KECIL + 1, "bold"),
            text_color=WARNA_TEBEL,
        ).pack(side="left")

        self.tampil_pass = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            atas_pass,
            text="Tampilkan",
            variable=self.tampil_pass,
            command=self._togol_password,
            font=(FONT, TS_KECIL),
            text_color=WARNA_REDUP,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            checkbox_height=18,
            checkbox_width=18,
            corner_radius=5,
        ).pack(side="right")

        self.e_pass = ctk.CTkEntry(
            baris_pass,
            width=380,
            height=TINGGI_INPUT,
            placeholder_text="Masukkan password",
            show="*",
            corner_radius=CORNER_INPUT,
            font=(FONT, TS_BADAN),
            border_color=WARNA_GARIS,
            fg_color="#fbfcfb",
        )
        self.e_pass.pack(fill="x", pady=(5, 0))

        # --- Pesan galat inline ---
        self.lbl_error = ctk.CTkLabel(
            frame,
            text="",
            font=(FONT, TS_BADAN),
            text_color="#dc2626",
            wraplength=360,
            justify="left",
        )
        self.lbl_error.pack(fill="x", pady=(12, 0))

        # --- Tombol masuk ---
        self.btn_masuk = ctk.CTkButton(
            frame,
            text="Masuk ke Sistem",
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            width=380,
            height=44,
            corner_radius=CORNER_INPUT + 2,
            font=(FONT, TS_BADAN + 2, "bold"),
            command=self.proses_login,
        )
        self.btn_masuk.pack(fill="x", pady=(14, 0))

        # --- Pembatas dan tautan registrasi ---
        pembatas = ctk.CTkFrame(frame, fg_color=WARNA_GARIS, height=1)
        pembatas.pack(fill="x", pady=(22, 0))
        pembatas.pack_propagate(False)

        self.link_daftar = ctk.CTkButton(
            frame,
            text="Belum punya akun?  Daftar akun baru",
            fg_color="transparent",
            hover_color="#eef4f0",
            text_color=COLOR_PRIMARY,
            border_width=1,
            border_color="#c8d8cd",
            height=40,
            corner_radius=CORNER_INPUT + 2,
            font=(FONT, TS_BADAN),
            command=self._buka_registrasi,
        )
        self.link_daftar.pack(fill="x", pady=(18, 0))

        ctk.CTkLabel(
            frame,
            text="Versi %s  •  %s" % (APP_VERSION, APP_RELEASE),
            font=(FONT, TS_KECIL - 1),
            text_color="#9ca3af",
        ).pack(side="bottom", pady=(12, 0))

    # ------------------------------------------------------------
    def _togol_password(self):
        """Menampilkan atau menyembunyikan isi kolom password."""
        self.e_pass.configure(show="" if self.tampil_pass.get() else "*")

    # ========================================================
    # Aksi
    # ========================================================
    def proses_login(self):
        """Menjalankan proses autentikasi saat tombol ditekan."""
        username = self.e_user.get().strip()
        password = self.e_pass.get()

        if not username or not password:
            self._tampilkan_error("Username dan password wajib diisi!")
            return

        self.btn_loading(True)
        self.update_idletasks()

        berhasil, pesan = AuthController.login(username, password)
        self.btn_loading(False)

        if berhasil:
            self._tampilkan_error("")
            self.destroy()
            if callable(self.on_login_success):
                self.on_login_success(AuthController.current_user())
        else:
            self._tampilkan_error(pesan)
            self.e_pass.delete(0, "end")
            self.e_pass.focus_set()

    # ------------------------------------------------------------
    def btn_loading(self, aktif):
        """Mengubah tampilan tombol selama proses verifikasi."""
        if aktif:
            self.btn_masuk.configure(text="Memproses...", state="disabled")
        else:
            self.btn_masuk.configure(text="Masuk ke Sistem", state="normal")

    # ------------------------------------------------------------
    def _tampilkan_error(self, pesan):
        """Menampilkan atau menyembunyikan pesan galat inline."""
        self.lbl_error.configure(text=pesan)

    # ------------------------------------------------------------
    def _buka_registrasi(self, _event=None):
        """Membuka jendela registrasi akun baru."""
        if callable(self.on_open_register):
            self.on_open_register(self)
