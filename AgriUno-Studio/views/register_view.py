"""Dialog pendaftaran akun khusus (peran operator/petani)."""

import tkinter as tk

import customtkinter as ctk

import customtkinter as ctk

from config import ui_kit
from config import constants
from controllers.auth_controller import AuthController
from config.ui_kit import DialogModal

class RegisterView(DialogModal):
    """Dialog pendaftaran akun khusus (peran operator/petani)."""

    def __init__(self, master):
        super().__init__(master, "AgriUno - Daftar Akun Baru", lebar=560)
        bingkai = ctk.CTkFrame(self, fg_color="transparent")
        bingkai.pack(padx=30, pady=26)

        ctk.CTkLabel(
            bingkai, text="Buat Akun Baru", font=(ui_kit.FONT, 19, "bold"), text_color=ui_kit.TEKS
        ).pack(anchor="w")

        kolom_nama, self.e_nama = ui_kit.bidang(
            bingkai, "Nama Lengkap", "Contoh: Budi Santoso", lebar=480
        )
        kolom_nama.pack(fill="x", pady=(14, 0))
        kolom_user, self.e_user = ui_kit.bidang(bingkai, "Username", "Minimal 4 karakter", lebar=480)
        kolom_user.pack(fill="x", pady=(10, 0))

        baris = ctk.CTkFrame(bingkai, fg_color="transparent")
        baris.pack(fill="x", pady=(10, 0))
        baris.grid_columnconfigure(0, weight=1)
        baris.grid_columnconfigure(1, weight=1)
        kolom_p1, self.e_p1 = ui_kit.bidang(baris, "Password", "Minimal 6 karakter", lebar=230)
        kolom_p1.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.e_p1.configure(show="*")
        kolom_p2, self.e_p2 = ui_kit.bidang(baris, "Konfirmasi", "Ulangi password", lebar=230)
        kolom_p2.grid(row=0, column=1, sticky="ew")
        self.e_p2.configure(show="*")

        ctk.CTkLabel(
            bingkai, text="Peran *", font=(ui_kit.FONT, 11, "bold"), text_color=ui_kit.TEKS
        ).pack(anchor="w", pady=(14, 5))
        self.var_peran = tk.StringVar(value=constants.ROLE_OPERATOR)
        baris_peran = ctk.CTkFrame(bingkai, fg_color="transparent")
        baris_peran.pack(fill="x")
        for kolom, role in enumerate((constants.ROLE_OPERATOR, constants.ROLE_PETANI)):
            kartu_peran = ctk.CTkFrame(
                baris_peran,
                fg_color=ui_kit.ZEBRA,
                corner_radius=12,
                border_width=1,
                border_color=ui_kit.GARIS,
            )
            kartu_peran.grid(row=0, column=kolom, sticky="ew", padx=6)
            ctk.CTkRadioButton(
                kartu_peran,
                text=constants.label_peran(role),
                variable=self.var_peran,
                value=role,
                font=(ui_kit.FONT, 12, "bold"),
                text_color=ui_kit.TEKS,
                fg_color=ui_kit.HIJAU,
                hover_color=ui_kit.HIJAU_HOVER,
            ).pack(anchor="w", padx=14, pady=12)

        self.pesan = ctk.CTkLabel(
            bingkai,
            text="",
            font=(ui_kit.FONT, 12),
            text_color=ui_kit.MERAH,
            wraplength=480,
            justify="left",
        )
        self.pesan.pack(fill="x", pady=(10, 0))

        self._baris_aksi(bingkai, "Daftar Sekarang", self.proses)

    # --------------------------------------------------------
    def proses(self):
        """Memproses pendaftaran akun."""
        ok, pesan = AuthController.register(
            self.e_nama.get(),
            self.e_user.get(),
            self.e_p1.get(),
            self.e_p2.get(),
            self.var_peran.get(),
        )
        self.pesan.configure(text=pesan, text_color=ui_kit.HIJAU_TEKS if ok else ui_kit.MERAH)
        if ok:
            ui_kit.toast(self.master, pesan, jenis="sukses")
            self.after(1200, self.destroy)
