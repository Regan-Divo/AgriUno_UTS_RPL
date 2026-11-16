"""
=========================================================
HALAMAN DASHBOARD - AGRIUNO
=========================================================
Menyajikan ringkasan operasional gudang.

Berbeda dengan versi UTS yang menampilkan tiga progress bar dengan
nilai tetap (0.75, 0.50, dan 0.85), versi ini menghitung seluruh
indikator dari data nyata pada basis data:

* **Alokasi Terdistribusi** - rasio total berat yang sudah
  dialokasikan terhadap total berat setoran.
* **Pengiriman Selesai**   - rasio alokasi berstatus "Terkirim"
  terhadap seluruh alokasi.
* **Petani Aktif**         - rasio petani yang pernah menyetor
  terhadap seluruh petani terdaftar.

Dengan demikian angka yang tampil pada dashboard selalu konsisten
dengan kondisi gudang terkini.
"""

import customtkinter as ctk

from config.constants import (
    COLOR_ACCENT,
    COLOR_INFO,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
)
from config.ui_kit import (
    FONT,
    TS_BADAN,
    TS_JUDUL,
    TS_KECIL,
    TS_SEKSI,
    WARNA_LATAR,
    WARNA_REDUP,
    WARNA_TEBEL,
    judul_halaman,
    kartu,
)

#: Karakter chip ikon untuk tiap kartu statistik.
_CHIP = {"petani": "P", "panen": "H", "distribusi": "D"}


class DashboardView(ctk.CTkFrame):
    """Halaman ringkasan operasional AgriUno."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=WARNA_LATAR)
        self.controller = controller
        self._statistik = {}

        # --------------------------------------------------------
        # Kepala halaman
        # --------------------------------------------------------
        judul_halaman(
            self,
            "Dashboard Operasional",
            "Ringkasan data petani, inventori panen, dan alokasi distribusi.",
        )

        # --------------------------------------------------------
        # Kartu statistik
        # --------------------------------------------------------
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=32, pady=(0, 4))
        for kolom in range(3):
            cards_frame.grid_columnconfigure(kolom, weight=1)

        self.lbl_p = self._kartu_statistik(
            cards_frame, "Total Petani", "0", COLOR_INFO, "petani", 0
        )
        self.lbl_h = self._kartu_statistik(
            cards_frame, "Total Lot Panen", "0", COLOR_ACCENT, "panen", 1
        )
        self.lbl_d = self._kartu_statistik(
            cards_frame, "Total Distribusi", "0", COLOR_PRIMARY_HOVER, "distribusi", 2
        )

        # --------------------------------------------------------
        # Panel indikator kinerja
        # --------------------------------------------------------
        chart_box = kartu(self)
        chart_box.pack(fill="x", padx=32, pady=(14, 6))

        ctk.CTkLabel(
            chart_box,
            text="Indikator Kinerja Rantai Pasok",
            font=(FONT, TS_SEKSI, "bold"),
            text_color=WARNA_TEBEL,
        ).pack(anchor="w", padx=22, pady=(16, 2))

        self.indicators = {}
        for key in ("alokasi", "terkirim", "petani_aktif"):
            row, bar, label = self.create_progress_indicator(chart_box, key)
            self.indicators[key] = {"bar": bar, "label": label}

        # --------------------------------------------------------
        # Panel ringkasan berat
        # --------------------------------------------------------
        weight_box = kartu(self)
        weight_box.pack(fill="x", padx=32, pady=6)

        ctk.CTkLabel(
            weight_box,
            text="Ringkasan Berat Komoditas (Kg)",
            font=(FONT, TS_SEKSI, "bold"),
            text_color=WARNA_TEBEL,
        ).pack(anchor="w", padx=22, pady=(16, 4))

        self.weight_frame = ctk.CTkFrame(weight_box, fg_color="transparent")
        self.weight_frame.pack(fill="x", padx=22, pady=(0, 18))
        for kolom in range(3):
            self.weight_frame.grid_columnconfigure(kolom, weight=1)

        self.lbl_total_setor = self._item_berat("Total Setoran", "0.00", 0)
        self.lbl_total_kirim = self._item_berat("Total Dialokasikan", "0.00", 1)
        self.lbl_sisa = self._item_berat("Sisa di Gudang", "0.00", 2)

        # --------------------------------------------------------
        # Panel tentang sistem
        # --------------------------------------------------------
        info_box = kartu(self)
        info_box.pack(fill="x", padx=32, pady=(6, 22))

        ctk.CTkLabel(
            info_box,
            text="Tentang Sistem AgriUno",
            font=(FONT, TS_SEKSI, "bold"),
            text_color=WARNA_TEBEL,
        ).pack(anchor="w", padx=22, pady=(14, 4))

        desc = (
            "AgriUno adalah platform manajemen hasil panen pertanian lokal terpadu "
            "untuk pencatatan data petani, inventori gudang, dan logistik distribusi "
            "secara real-time. Seluruh kredensial pengguna disimpan sebagai hash "
            "SHA-256 dan hak akses tiap pengguna diatur berdasarkan peran "
            "(Role-Based Access Control)."
        )
        ctk.CTkLabel(
            info_box,
            text=desc,
            font=(FONT, TS_BADAN),
            text_color="#5b6b62",
            justify="left",
            wraplength=860,
        ).pack(anchor="w", padx=22, pady=(0, 16))

        self.load_data()

    # --------------------------------------------------------
    # Komponen
    # --------------------------------------------------------
    def _kartu_statistik(self, parent, judul, nilai, warna, kunci_chip, kolom):
        """Kartu statistik dengan chip ikon huruf dan nilai besar."""
        card = kartu(parent)
        card.grid(row=0, column=kolom, padx=(0, 14) if kolom < 2 else 0, sticky="ew")

        tubuh = ctk.CTkFrame(card, fg_color="transparent")
        tubuh.pack(fill="x", padx=20, pady=18)

        ctk.CTkLabel(
            tubuh,
            text=_CHIP.get(kunci_chip, "?"),
            font=(FONT, 18, "bold"),
            text_color=warna,
            fg_color="#f0f5f2",
            corner_radius=12,
            width=46,
            height=46,
        ).pack(side="left", padx=(0, 14))

        kolom_teks = ctk.CTkFrame(tubuh, fg_color="transparent")
        kolom_teks.pack(side="left", fill="x", expand=True)

        label = ctk.CTkLabel(
            kolom_teks,
            text=nilai,
            font=(FONT, TS_JUDUL, "bold"),
            text_color=WARNA_TEBEL,
        )
        label.pack(anchor="w")

        ctk.CTkLabel(
            kolom_teks,
            text=judul,
            font=(FONT, TS_KECIL),
            text_color=WARNA_REDUP,
        ).pack(anchor="w")
        return label

    # ------------------------------------------------------------
    def create_progress_indicator(self, parent, key):
        """Membuat satu baris indikator kinerja."""
        titles = {
            "alokasi": "Alokasi Terdistribusi",
            "terkirim": "Pengiriman Selesai",
            "petani_aktif": "Petani Aktif",
        }

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=8)

        ctk.CTkLabel(
            row,
            text=titles[key],
            font=(FONT, TS_BADAN),
            width=200,
            anchor="w",
            text_color="#43554b",
        ).pack(side="left")

        bar = ctk.CTkProgressBar(
            row,
            width=480,
            height=10,
            corner_radius=5,
            progress_color=COLOR_PRIMARY_HOVER,
            fg_color="#e5ece7",
        )
        bar.set(0)
        bar.pack(side="left", padx=12, fill="x", expand=True)

        label = ctk.CTkLabel(
            row,
            text="0%",
            font=(FONT, TS_BADAN, "bold"),
            width=54,
            anchor="e",
            text_color=COLOR_PRIMARY,
        )
        label.pack(side="right")

        return row, bar, label

    # ------------------------------------------------------------
    def _item_berat(self, judul, nilai, kolom):
        """Membuat satu kolom ringkasan berat dengan pemisah halus."""
        box = ctk.CTkFrame(self.weight_frame, fg_color="transparent")
        box.grid(row=0, column=kolom, sticky="ew", padx=(0, 18) if kolom < 2 else 0)

        ctk.CTkLabel(
            box,
            text=judul,
            font=(FONT, TS_KECIL),
            text_color=WARNA_REDUP,
        ).pack(anchor="w")

        label = ctk.CTkLabel(
            box,
            text=nilai,
            font=(FONT, 20, "bold"),
            text_color=COLOR_PRIMARY,
        )
        label.pack(anchor="w")
        return label

    # ========================================================
    # Pemuatan data
    # ========================================================
    def load_data(self):
        """Membaca ringkasan statistik terbaru dari basis data."""
        statistik = self.controller.get_statistik()
        self._statistik = statistik

        self.lbl_p.configure(text=str(statistik["total_petani"]))
        self.lbl_h.configure(text=str(statistik["total_panen"]))
        self.lbl_d.configure(text=str(statistik["total_distribusi"]))

        nilai_indikator = dict.fromkeys(self.indicators, 0.0)
        for label, nilai in statistik.get("indikator", []):
            kunci = {
                "Alokasi Terdistribusi": "alokasi",
                "Pengiriman Selesai": "terkirim",
                "Petani Aktif": "petani_aktif",
            }.get(label)
            if kunci:
                nilai_indikator[kunci] = nilai

        for key, widget in self.indicators.items():
            nilai = nilai_indikator.get(key, 0.0)
            widget["bar"].set(nilai)
            widget["label"].configure(text="%d%%" % round(nilai * 100))

        self.lbl_total_setor.configure(text="%.2f" % float(statistik["total_berat"]))
        self.lbl_total_kirim.configure(text="%.2f" % float(statistik["total_kirim"]))
        self.lbl_sisa.configure(text="%.2f" % float(statistik["sisa_gudang"]))
