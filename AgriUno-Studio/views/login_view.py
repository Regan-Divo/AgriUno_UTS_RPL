"""Tampilan login split-screen di dalam jendela induk."""

import customtkinter as ctk

from config import ui_kit
from controllers.auth_controller import AuthController
from views.register_view import RegisterView

class LoginView(ctk.CTkFrame):
    """Layar masuk split-screen di dalam jendela induk."""

    def __init__(self, master, on_sukses):
        super().__init__(master, fg_color=ui_kit.LATAR)
        self.on_sukses = on_sukses
        self.logo = ui_kit.gambar_logo(74)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._panel_merek()
        self._panel_formulir()

    # --------------------------------------------------------
    def _panel_merek(self):
        """Panel identitas di sisi kiri."""
        panel = ctk.CTkFrame(self, fg_color=ui_kit.HIJAU, corner_radius=0, width=400)
        panel.grid(row=0, column=0, sticky="nsew")
        panel.grid_propagate(False)

        dalam = ctk.CTkFrame(panel, fg_color="transparent")
        dalam.pack(expand=True, fill="both", padx=36, pady=36)

        if self.logo:
            ctk.CTkLabel(dalam, image=self.logo, text="").pack(anchor="w", pady=(8, 12))
        ctk.CTkLabel(dalam, text="AgriUno", font=(ui_kit.FONT, 30, "bold"), text_color="white").pack(
            anchor="w"
        )
        ctk.CTkLabel(
            dalam,
            text="Edisi Studio — antarmuka baru untuk pengelolaan hasil panen.",
            font=(ui_kit.FONT, 12),
            text_color="#b9d4c4",
            wraplength=300,
            justify="left",
        ).pack(anchor="w", pady=(4, 28))

        for fitur in (
            "Satu jendela: login hingga keluar tanpa pergantian window",
            "Pencarian langsung dan alur status pengiriman satu-klik",
            "Tabel master-detail dengan ringkasan otomatis",
        ):
            baris = ctk.CTkFrame(dalam, fg_color="transparent")
            baris.pack(fill="x", pady=6)
            ctk.CTkLabel(
                baris,
                text="✓",
                font=(ui_kit.FONT, 13, "bold"),
                text_color="#8fe3a9",
                width=24,
                anchor="w",
            ).pack(side="left")
            ctk.CTkLabel(
                baris,
                text=fitur,
                font=(ui_kit.FONT, 12),
                text_color="#e8f2ec",
                wraplength=290,
                justify="left",
            ).pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            panel,
            text="UAS RPL 2026  •  Universitas Tadulako",
            font=(ui_kit.FONT, 10),
            text_color="#7fa894",
        ).pack(side="bottom", anchor="w", padx=36, pady=22)

    # --------------------------------------------------------
    def _panel_formulir(self):
        """Panel formulir kredensial di sisi kanan."""
        panel = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        panel.grid(row=0, column=1, sticky="nsew")

        bingkai = ctk.CTkFrame(panel, fg_color="transparent")
        bingkai.pack(expand=True, fill="both", padx=72, pady=44)

        ctk.CTkLabel(
            bingkai,
            text="Selamat Datang Kembali",
            font=(ui_kit.FONT, 24, "bold"),
            text_color=ui_kit.TEKS,
        ).pack(anchor="w")
        ctk.CTkLabel(
            bingkai,
            text="Masuk untuk melanjutkan pengelolaan gudang Anda.",
            font=(ui_kit.FONT, 12),
            text_color=ui_kit.REDUP,
        ).pack(anchor="w", pady=(2, 24))

        kolom_user, self.e_user = ui_kit.bidang(bingkai, "Username", "Masukkan username", lebar=380)
        kolom_user.pack(fill="x")

        baris_pass = ctk.CTkFrame(bingkai, fg_color="transparent")
        baris_pass.pack(fill="x", pady=(16, 0))
        kolom_pass, self.e_pass = ui_kit.bidang(
            baris_pass, "Password", "Masukkan password", lebar=380
        )
        kolom_pass.pack(fill="x")
        self.e_pass.configure(show="*")

        self.pesan = ctk.CTkLabel(
            bingkai,
            text="",
            font=(ui_kit.FONT, 12),
            text_color=ui_kit.MERAH,
            wraplength=380,
            justify="left",
        )
        self.pesan.pack(fill="x", pady=(10, 0))

        self.btn_masuk = ui_kit.tombol(
            bingkai, "Masuk ke Sistem", self.proses_login, jenis="primer", lebar=380
        )
        self.btn_masuk.pack(fill="x", pady=(14, 0), ipady=4)

        ui_kit.tombol(
            bingkai,
            "Belum punya akun?  Daftar di sini",
            self._buka_registrasi,
            jenis="sekunder",
            lebar=380,
        ).pack(fill="x", pady=(14, 0))

        ctk.CTkLabel(
            bingkai,
            text="Akun demo: admin/admin123 • operator/operator123 • petani/petani123",
            font=(ui_kit.FONT, 10),
            text_color="#9ca3af",
        ).pack(side="bottom", pady=(14, 0))

        self.bind("<Return>", lambda _e: self.proses_login())
        self.after(120, lambda: self.e_user.focus_set())

    # --------------------------------------------------------
    def proses_login(self):
        """Menjalankan autentikasi dan membuka shell utama."""
        self.btn_masuk.configure(text="Memproses...", state="disabled")
        self.update_idletasks()

        ok, pesan, user = AuthController.login(self.e_user.get(), self.e_pass.get())
        self.btn_masuk.configure(text="Masuk ke Sistem", state="normal")

        if ok:
            self.pesan.configure(text="")
            self.on_sukses(user)
        else:
            self.pesan.configure(text=pesan)
            ui_kit.toast(self.master, pesan, jenis="galat")

    # --------------------------------------------------------
    def _buka_registrasi(self):
        """Membuka dialog pendaftaran akun baru."""
        RegisterView(self.master)