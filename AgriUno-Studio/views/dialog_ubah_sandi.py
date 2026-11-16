"""Dialog ubah kata sandi pengguna aktif (UC-09)."""

import customtkinter as ctk

from config import ui_kit
from config.ui_kit import DialogModal
from controllers.controller import AgriUnoController


class DialogUbahSandi(DialogModal):
    """Formulir ubah kata sandi dengan verifikasi kata sandi lama."""

    def __init__(self, master, on_selesai=None):
        super().__init__(master, "Ubah Kata Sandi Pengguna", lebar=520)
        self.on_selesai = on_selesai

        bingkai = ctk.CTkFrame(self, fg_color="transparent")
        bingkai.pack(padx=30, pady=24)

        ctk.CTkLabel(
            bingkai,
            text="Ubah Kata Sandi",
            font=(ui_kit.FONT, 18, "bold"),
            text_color=ui_kit.TEKS,
        ).pack(anchor="w")
        ctk.CTkLabel(
            bingkai,
            text="Kata sandi baru akan disimpan dengan salt baru (hash SHA-256).",
            font=(ui_kit.FONT, 10),
            text_color=ui_kit.REDUP,
            wraplength=450,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        kolom_lama, self.e_lama = ui_kit.bidang(
            bingkai, "Kata Sandi Lama", "Masukkan kata sandi saat ini", lebar=440
        )
        kolom_lama.pack(fill="x", pady=(14, 0))
        self.e_lama.configure(show="*")

        kolom_baru, self.e_baru = ui_kit.bidang(
            bingkai, "Kata Sandi Baru", "Minimal 6 karakter", lebar=440
        )
        kolom_baru.pack(fill="x", pady=(10, 0))
        self.e_baru.configure(show="*")

        kolom_konfirmasi, self.e_konfirmasi = ui_kit.bidang(
            bingkai, "Konfirmasi Kata Sandi Baru", "Ulangi kata sandi baru", lebar=440
        )
        kolom_konfirmasi.pack(fill="x", pady=(10, 0))
        self.e_konfirmasi.configure(show="*")

        self.pesan = ctk.CTkLabel(
            bingkai,
            text="",
            font=(ui_kit.FONT, 11),
            text_color=ui_kit.MERAH,
            wraplength=440,
            justify="left",
        )
        self.pesan.pack(fill="x", pady=(8, 0))

        self._baris_aksi(bingkai, "Simpan Kata Sandi", self.proses)

    # --------------------------------------------------------
    def proses(self):
        """Menyimpan kata sandi baru pengguna aktif."""
        user = getattr(self.master, "user", None)
        ok, pesan = AgriUnoController.ubah_sandi(
            user,
            self.e_lama.get(),
            self.e_baru.get(),
            self.e_konfirmasi.get(),
        )
        self.pesan.configure(text="" if ok else pesan)
        if ok:
            ui_kit.toast(self.master, pesan, jenis="sukses")
            if callable(self.on_selesai):
                self.on_selesai(True, pesan)
            self.after(900, self.destroy)
