"""
=========================================================
ANTARMUKA REGISTRASI AKUN - AGRIUNO  (Modul 7)
=========================================================
Halaman pendaftaran akun khusus pengguna baru AgriUno,
bergaya split-screen yang serasi dengan jendela login.

Sesuai ketentuan UAS Praktikum RPL 2026, tahap UAS menuntut
penambahan fitur registrasi akun khusus pengguna. Form ini
menyediakan:

* Nama lengkap pengguna.
* Username unik (minimal 4 karakter).
* Password (minimal 6 karakter) beserta konfirmasi password.
* Pilihan peran berbentuk kartu pilihan, yaitu ``operator``
  (Operator Gudang) atau ``petani`` (Petani).

Peran ``admin`` sengaja tidak dapat dipilih karena akun
Administrator hanya boleh dibuat oleh pengelola basis data
melalui skrip ``database.sql`` (BR-07). Aturan ini ditegakkan
pada dua lapisan: antarmuka membatasi pilihan, dan model
menolak bila peran di luar daftar yang diizinkan.

Kata sandi yang diketik pengguna tidak pernah disimpan dalam
bentuk teks biasa. Model ``UserModel`` menambahkan salt acak
per pengguna kemudian menyimpan hash SHA-256 dari
``salt + password``.
"""

import tkinter as tk

import customtkinter as ctk

from config.constants import (
    APP_NAME,
    APP_RELEASE,
    APP_TAGLINE,
    APP_VERSION,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    REGISTRABLE_ROLES,
    ROLE_CAPABILITIES,
    WIN_REGISTER,
)
from config.ui_kit import (
    CORNER_INPUT,
    FONT,
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

#: Label tampilan untuk setiap peran yang dapat dipilih.
_ROLE_LABELS = {role: ROLE_CAPABILITIES[role]["label"] for role in REGISTRABLE_ROLES}

#: Panel kiri (panel merek) dalam piksel.
LEBAR_PANEL_MEREK = 388


class RegisterView(ctk.CTk):
    """Jendela registrasi akun baru AgriUno."""

    def __init__(self, master=None, on_success=None, on_back=None):
        super().__init__(master)
        self.on_success = on_success
        self.on_back = on_back

        self.title("%s - Registrasi Akun" % APP_NAME)
        self.geometry("%dx%d" % WIN_REGISTER)
        self.resizable(False, False)
        self.configure(fg_color="#e9efeb")
        pasang_ikon(self)

        self._build_ui()
        self.bind("<Return>", lambda _event: self.proses_registrasi())

    # ========================================================
    # Antarmuka
    # ========================================================
    def _build_ui(self):
        """Menyusun dua panel jendela registrasi."""
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
        """Panel kanan: formulir registrasi."""
        panel = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        panel.grid(row=0, column=1, sticky="nsew")

        frame = ctk.CTkFrame(panel, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=58, pady=32)

        ctk.CTkLabel(
            frame,
            text="Buat Akun Baru",
            font=(FONT, TS_DISPLAY - 3, "bold"),
            text_color=WARNA_TEBEL,
        ).pack(anchor="w")

        ctk.CTkLabel(
            frame,
            text="Daftarkan diri Anda untuk mulai menggunakan AgriUno.",
            font=(FONT, TS_BADAN),
            text_color=WARNA_REDUP,
        ).pack(anchor="w", pady=(2, 18))

        # --- Nama lengkap ---
        kolom_nama, self.e_nama = bidang_isian(
            frame, "Nama Lengkap", "Contoh: Budi Santoso", lebar=360
        )
        kolom_nama.pack(fill="x")

        # --- Username ---
        kolom_user, self.e_user = bidang_isian(frame, "Username", "Minimal 4 karakter", lebar=360)
        kolom_user.pack(fill="x", pady=(12, 0))

        # --- Password dan konfirmasi berdampingan ---
        baris_pass = ctk.CTkFrame(frame, fg_color="transparent")
        baris_pass.pack(fill="x", pady=(12, 0))
        baris_pass.grid_columnconfigure(0, weight=1)
        baris_pass.grid_columnconfigure(1, weight=1)

        kolom_pass, self.e_pass = bidang_isian(
            baris_pass, "Password", "Minimal 6 karakter", lebar=150
        )
        kolom_pass.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        kolom_pass2, self.e_pass2 = bidang_isian(
            baris_pass, "Konfirmasi Password", "Ulangi password", lebar=150
        )
        kolom_pass2.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        # --- Pilihan peran berbentuk kartu radio ---
        ctk.CTkLabel(
            frame,
            text="Peran Pengguna *",
            font=(FONT, TS_KECIL + 1, "bold"),
            text_color=WARNA_TEBEL,
        ).pack(anchor="w", pady=(14, 5))

        self.var_peran = tk.StringVar(value=REGISTRABLE_ROLES[0])
        baris_peran = ctk.CTkFrame(frame, fg_color="transparent")
        baris_peran.pack(fill="x")
        baris_peran.grid_columnconfigure(0, weight=1)
        baris_peran.grid_columnconfigure(1, weight=1)

        for idx, role in enumerate(REGISTRABLE_ROLES):
            kartu_peran = ctk.CTkFrame(
                baris_peran,
                fg_color="#f6f9f7",
                corner_radius=CORNER_INPUT + 2,
                border_width=1,
                border_color=WARNA_GARIS,
            )
            kartu_peran.grid(row=0, column=idx, sticky="ew", padx=(0, 8) if idx == 0 else (8, 0))

            ctk.CTkRadioButton(
                kartu_peran,
                text=_ROLE_LABELS[role],
                variable=self.var_peran,
                value=role,
                command=self._peran_diganti,
                font=(FONT, TS_BADAN, "bold"),
                text_color=WARNA_TEBEL,
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_PRIMARY_HOVER,
            ).pack(anchor="w", padx=14, pady=12)

        # --- Petunjuk peran terpilih ---
        self.lbl_info = ctk.CTkLabel(
            frame,
            text="",
            font=(FONT, TS_KECIL + 1),
            text_color=WARNA_REDUP,
            wraplength=380,
            justify="left",
        )
        self.lbl_info.pack(fill="x", pady=(8, 0))

        # --- Pesan galat ---
        self.lbl_error = ctk.CTkLabel(
            frame,
            text="",
            font=(FONT, TS_BADAN),
            text_color="#dc2626",
            wraplength=380,
            justify="left",
        )
        self.lbl_error.pack(fill="x", pady=(8, 0))

        # --- Tombol aksi ---
        self.btn_daftar = ctk.CTkButton(
            frame,
            text="Daftar Sekarang",
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            width=380,
            height=44,
            corner_radius=CORNER_INPUT + 2,
            font=(FONT, TS_BADAN + 2, "bold"),
            command=self.proses_registrasi,
        )
        self.btn_daftar.pack(fill="x", pady=(12, 0))

        self.link_kembali = ctk.CTkButton(
            frame,
            text="Sudah punya akun?  Kembali ke Login",
            fg_color="transparent",
            hover_color="#eef4f0",
            text_color=COLOR_PRIMARY,
            border_width=1,
            border_color="#c8d8cd",
            height=40,
            corner_radius=CORNER_INPUT + 2,
            font=(FONT, TS_BADAN),
            command=self._kembali_ke_login,
        )
        self.link_kembali.pack(fill="x", pady=(10, 0))

        ctk.CTkLabel(
            frame,
            text="Versi %s  •  %s" % (APP_VERSION, APP_RELEASE),
            font=(FONT, TS_KECIL - 1),
            text_color="#9ca3af",
        ).pack(side="bottom", pady=(8, 0))

        self._peran_diganti()

    # ========================================================
    # Aksi
    # ========================================================
    def _peran_diganti(self, _value=None):
        """Menampilkan deskripsi singkat peran yang dipilih."""
        role = self._peran_terpilih()
        deskripsi = ROLE_CAPABILITIES.get(role, {}).get("deskripsi", "")
        self.lbl_info.configure(text=deskripsi)

    def _peran_terpilih(self):
        """Mengembalikan nilai peran yang dipilih pada kartu radio."""
        nilai = self.var_peran.get()
        if nilai in REGISTRABLE_ROLES:
            return nilai
        return REGISTRABLE_ROLES[0]

    # ------------------------------------------------------------
    def proses_registrasi(self):
        """Memproses pendaftaran akun baru."""
        nama = self.e_nama.get().strip()
        username = self.e_user.get().strip()
        password = self.e_pass.get()
        konfirmasi = self.e_pass2.get()
        role = self._peran_terpilih()

        if not nama or not username or not password or not konfirmasi:
            self.lbl_error.configure(text="Seluruh kolom wajib diisi!")
            return

        self.btn_daftar.configure(text="Mendaftarkan...", state="disabled")
        self.update_idletasks()

        berhasil, pesan = AuthController.register(username, password, konfirmasi, nama, role)

        self.btn_daftar.configure(text="Daftar Sekarang", state="normal")

        if berhasil:
            self.lbl_error.configure(text="", text_color="#15803d")
            self._info_sukses(pesan)
            if callable(self.on_success):
                self.after(1500, self.on_success)
        else:
            self.lbl_error.configure(text=pesan, text_color="#dc2626")

    # ------------------------------------------------------------
    def _info_sukses(self, pesan):
        """Menampilkan konfirmasi berhasil pada jendela."""
        self.lbl_error.configure(text=pesan, text_color="#15803d")
        self.e_nama.delete(0, "end")
        self.e_user.delete(0, "end")
        self.e_pass.delete(0, "end")
        self.e_pass2.delete(0, "end")

    # ------------------------------------------------------------
    def _kembali_ke_login(self, _event=None):
        """Menutup jendela registrasi dan kembali ke jendela login."""
        self.destroy()
        if callable(self.on_back):
            self.on_back()
