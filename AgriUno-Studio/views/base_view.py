"""Kerangka dasar halaman data (header, tabel, panel detail)."""

import customtkinter as ctk

from config import ui_kit
from controllers.auth_controller import AuthController


class HalamanDasar(ctk.CTkFrame):
    """Kerangka halaman: header, alat pencarian, tabel, panel detail."""

    def __init__(self, parent, app, judul, subjudul):
        super().__init__(parent, fg_color=ui_kit.LATAR)
        self.app = app
        self.terpilih = None

        ui_kit.judul_halaman(self, judul, subjudul).pack(fill="x", padx=32, pady=(24, 10))

        # --- Pita baca-saja untuk peran tanpa hak kelola ---
        if not AuthController.boleh(app.user, "kelola"):
            pita = ctk.CTkFrame(self, fg_color=ui_kit.AMBER_LEMBUT, corner_radius=10)
            pita.pack(fill="x", padx=32, pady=(0, 8))
            ctk.CTkLabel(
                pita,
                text="  Peran Anda hanya memiliki akses baca pada modul ini.",
                font=(ui_kit.FONT, 12),
                text_color="#92400e",
                anchor="w",
            ).pack(fill="x", padx=4, pady=6)

        # --- Baris alat: pencarian + tombol utama ---
        alat = ctk.CTkFrame(self, fg_color="transparent")
        alat.pack(fill="x", padx=32, pady=(0, 10))

        self.e_cari = ctk.CTkEntry(
            alat,
            placeholder_text="Cari data...",
            width=280,
            height=38,
            corner_radius=999,
            border_color=ui_kit.GARIS,
            font=(ui_kit.FONT, 12),
        )
        self.e_cari.pack(side="left")
        self.e_cari.bind("<KeyRelease>", self._saat_cari)

        self.chip_jumlah = ui_kit.chip(alat, "0 data")
        self.chip_jumlah.pack(side="left", padx=12)

        self.area_tambah = ctk.CTkFrame(alat, fg_color="transparent")
        self.area_tambah.pack(side="right")
        if AuthController.boleh(app.user, "kelola"):
            self.tombol_tambah = ui_kit.tombol(
                self.area_tambah,
                self._LABEL_TAMBAH,
                self._buka_form_tambah,
                jenis="primer",
                lebar=150,
            )
            self.tombol_tambah.pack()

        # --- Kartu utama: tabel kiri + detail kanan ---
        utama = ctk.CTkFrame(self, fg_color="transparent")
        utama.pack(fill="both", expand=True, padx=32, pady=(0, 24))
        utama.grid_columnconfigure(0, weight=1)
        utama.grid_rowconfigure(0, weight=1)

        kartu_tabel = ui_kit.kartu(utama)
        kartu_tabel.grid(row=0, column=0, sticky="nsew")
        self._bangun_tabel(kartu_tabel)

        kartu_detail = ui_kit.kartu(utama)
        kartu_detail.grid(row=0, column=1, sticky="nsew", padx=(14, 0))
        kartu_detail.configure(width=280)
        kartu_detail.grid_propagate(False)
        self.kartu_detail = kartu_detail
        self._detail_kosong()

    # --------------------------------------------------------
    # DIPAKAI ULANG SUBCLASS
    # --------------------------------------------------------
    def _saat_cari(self, _event=None):
        """Pencarian langsung dengan penundaan kecil (debounce)."""
        if hasattr(self, "_cari_id"):
            self.after_cancel(self._cari_id)
        self._cari_id = self.after(280, lambda: self.winfo_exists() and self.muat())

    # --------------------------------------------------------
    def _detail_kosong(self):
        """Menampilkan pesan bahwa belum ada baris terpilih."""
        for anak in self.kartu_detail.winfo_children():
            anak.destroy()
        ctk.CTkLabel(
            self.kartu_detail,
            text="Pilih baris pada tabel untuk melihat rincian data.",
            font=(ui_kit.FONT, 11),
            text_color=ui_kit.REDUP,
            wraplength=240,
            justify="center",
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _muat_detail(self):
        """Mengisi panel detail dari baris terpilih (diisi subclass)."""
        self._detail_kosong()
