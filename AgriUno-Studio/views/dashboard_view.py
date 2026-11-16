"""Tampilan dashboard ringkasan operasional."""

from datetime import datetime

import customtkinter as ctk

from config import ui_kit
from controllers.controller import AgriUnoController


class DashboardView(ctk.CTkFrame):
    """Ringkasan operasional: KPI, ringkasan berat, progres, komoditas, aktivitas."""

    _HARI = {
        0: "Senin",
        1: "Selasa",
        2: "Rabu",
        3: "Kamis",
        4: "Jumat",
        5: "Sabtu",
        6: "Minggu",
    }
    _BULAN = (
        "",
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember",
    )

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=ui_kit.LATAR)
        self.app = app

        ui_kit.judul_halaman(
            self, "Dashboard", "Ikhtisar performa gudang berdasarkan data terkini."
        ).pack(fill="x", padx=32, pady=(24, 12))

        self.sapaan = ctk.CTkLabel(self, text="", font=(ui_kit.FONT, 13), text_color=ui_kit.REDUP)
        self.sapaan.pack(fill="x", padx=32, pady=(0, 10))

        # --- Kartu KPI + panel ringkasan berat ---
        baris_kpi = ctk.CTkFrame(self, fg_color="transparent")
        baris_kpi.pack(fill="x", padx=32)
        for kolom in range(4):
            baris_kpi.grid_columnconfigure(kolom, weight=1)
        self.kpi = {}
        for kolom, (kunci, judul_k, ikon, warna, latar_ikon) in enumerate(
            (
                ("petani", "Total Petani", "👥", ui_kit.HIJAU_TEKS, ui_kit.HIJAU_LEMBUT),
                ("lot", "Total Lot Panen", "🌾", ui_kit.AMBER, ui_kit.AMBER_LEMBUT),
                ("alokasi", "Total Distribusi", "🚚", ui_kit.BIRU, ui_kit.BIRU_LEMBUT),
            )
        ):
            kartu = ui_kit.kartu(baris_kpi)
            kartu.grid(row=0, column=kolom, sticky="ew", padx=(0, 12))
            tubuh = ctk.CTkFrame(kartu, fg_color="transparent")
            tubuh.pack(fill="x", padx=18, pady=16)

            lencana = ctk.CTkFrame(
                tubuh, fg_color=latar_ikon, corner_radius=10, width=38, height=38
            )
            lencana.pack(side="right")
            lencana.pack_propagate(False)
            ctk.CTkLabel(lencana, text=ikon, font=(ui_kit.FONT, 15), text_color=warna).pack(
                expand=True
            )

            ctk.CTkLabel(
                tubuh,
                text=judul_k,
                font=(ui_kit.FONT, 10, "bold"),
                text_color=ui_kit.REDUP,
                anchor="w",
                justify="left",
            ).pack(anchor="w", pady=(0, 2))
            label = ctk.CTkLabel(
                tubuh, text="0", font=(ui_kit.FONT, 26, "bold"), text_color=ui_kit.TEKS, anchor="w"
            )
            label.pack(anchor="w")
            ctk.CTkFrame(tubuh, fg_color=warna, corner_radius=2, height=3, width=34).pack(
                anchor="w", pady=(6, 0)
            )
            self.kpi[kunci] = label

        # Panel ringkasan berat (Total Setoran, Total Dialokasikan, Sisa Gudang)
        kartu_berat = ui_kit.kartu(baris_kpi)
        kartu_berat.grid(row=0, column=3, sticky="ew")
        tubuh_berat = ctk.CTkFrame(kartu_berat, fg_color="transparent")
        tubuh_berat.pack(fill="x", padx=18, pady=14)
        ctk.CTkLabel(
            tubuh_berat,
            text="Ringkasan Berat",
            font=(ui_kit.FONT, 10, "bold"),
            text_color=ui_kit.REDUP,
            anchor="w",
        ).pack(anchor="w", pady=(0, 6))
        self.berat = {}
        for kunci, judul in (
            ("setor", "Total Setoran"),
            ("kirim", "Total Dialokasikan"),
            ("sisa", "Sisa di Gudang"),
        ):
            baris = ctk.CTkFrame(tubuh_berat, fg_color="transparent")
            baris.pack(fill="x", pady=1)
            ctk.CTkLabel(
                baris, text=judul, font=(ui_kit.FONT, 10), text_color=ui_kit.REDUP, anchor="w"
            ).pack(side="left")
            nilai = ctk.CTkLabel(
                baris, text="0.00 Kg", font=(ui_kit.FONT, 11, "bold"), text_color=ui_kit.TEKS
            )
            nilai.pack(side="right")
            self.berat[kunci] = nilai

        # --- Baris tengah: progres + komoditas ---
        baris_tengah = ctk.CTkFrame(self, fg_color="transparent")
        baris_tengah.pack(fill="x", padx=32, pady=(12, 0))
        baris_tengah.grid_columnconfigure(0, weight=3)
        baris_tengah.grid_columnconfigure(1, weight=2)
        baris_tengah.grid_rowconfigure(0, weight=1)

        kartu_progres = ui_kit.kartu(baris_tengah)
        kartu_progres.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(
            kartu_progres,
            text="Progres Distribusi",
            font=(ui_kit.FONT, 13, "bold"),
            text_color=ui_kit.TEKS,
        ).pack(anchor="w", padx=20, pady=(16, 6))
        self.progres = {}
        for kunci, label_k in (
            ("alokasi", "Alokasi terhadap setoran"),
            ("terkirim", "Pengiriman selesai"),
            ("aktif", "Petani aktif menyetor"),
        ):
            baris = ctk.CTkFrame(kartu_progres, fg_color="transparent")
            baris.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(
                baris,
                text=label_k,
                font=(ui_kit.FONT, 11),
                text_color=ui_kit.REDUP,
                width=190,
                anchor="w",
            ).pack(side="left")
            bar = ctk.CTkProgressBar(
                baris,
                height=8,
                corner_radius=4,
                progress_color=ui_kit.HIJAU_HOVER,
                fg_color="#e5ece7",
            )
            bar.set(0)
            bar.pack(side="left", fill="x", expand=True, padx=10)
            nilai = ctk.CTkLabel(
                baris,
                text="0%",
                font=(ui_kit.FONT, 11, "bold"),
                text_color=ui_kit.HIJAU,
                width=42,
                anchor="e",
            )
            nilai.pack(side="right")
            self.progres[kunci] = (bar, nilai)

        kartu_komo = ui_kit.kartu(baris_tengah)
        kartu_komo.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        ctk.CTkLabel(
            kartu_komo,
            text="Komoditas Terbanyak",
            font=(ui_kit.FONT, 13, "bold"),
            text_color=ui_kit.TEKS,
        ).pack(anchor="w", padx=20, pady=(16, 6))
        self.kartu_komo_isi = ctk.CTkFrame(kartu_komo, fg_color="transparent")
        self.kartu_komo_isi.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # --- Aktivitas terkini ---
        kartu_aktivitas = ui_kit.kartu(self)
        kartu_aktivitas.pack(fill="both", expand=True, padx=32, pady=(12, 24))
        ctk.CTkLabel(
            kartu_aktivitas,
            text="Aktivitas Terkini",
            font=(ui_kit.FONT, 13, "bold"),
            text_color=ui_kit.TEKS,
        ).pack(anchor="w", padx=20, pady=(16, 4))
        self.isi_aktivitas = ctk.CTkFrame(kartu_aktivitas, fg_color="transparent")
        self.isi_aktivitas.pack(fill="both", expand=True, padx=20, pady=(0, 14))

    # --------------------------------------------------------
    # Metode katalog kelas (dokumentasi teknis 4.7)
    # --------------------------------------------------------
    def load_data(self):
        """Membaca ulang seluruh angka dashboard."""
        return self.muat()

    def create_stat_card(self, induk, kunci, judul_k, ikon, warna, latar_ikon):
        """Menyusun satu kartu statistik pada dashboard."""
        kartu = ui_kit.kartu(induk)
        tubuh = ctk.CTkFrame(kartu, fg_color="transparent")
        tubuh.pack(fill="x", padx=18, pady=16)
        lencana = ctk.CTkFrame(tubuh, fg_color=latar_ikon, corner_radius=10, width=38, height=38)
        lencana.pack(side="right")
        lencana.pack_propagate(False)
        ctk.CTkLabel(lencana, text=ikon, font=(ui_kit.FONT, 15), text_color=warna).pack(expand=True)
        ctk.CTkLabel(
            tubuh, text=judul_k, font=(ui_kit.FONT, 10, "bold"), text_color=ui_kit.REDUP, anchor="w"
        ).pack(anchor="w", pady=(0, 2))
        label = ctk.CTkLabel(
            tubuh, text="0", font=(ui_kit.FONT, 26, "bold"), text_color=ui_kit.TEKS, anchor="w"
        )
        label.pack(anchor="w")
        ctk.CTkFrame(tubuh, fg_color=warna, corner_radius=2, height=3, width=34).pack(
            anchor="w", pady=(6, 0)
        )
        return label

    def create_progress_indicator(self, induk, kunci, judul_k):
        """Menyusun satu indikator kinerja berupa progress bar."""
        baris = ctk.CTkFrame(induk, fg_color="transparent")
        baris.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(
            baris,
            text=judul_k,
            font=(ui_kit.FONT, 11),
            text_color=ui_kit.REDUP,
            width=190,
            anchor="w",
        ).pack(side="left")
        bar = ctk.CTkProgressBar(
            baris, height=8, corner_radius=4, progress_color=ui_kit.HIJAU_HOVER, fg_color="#e5ece7"
        )
        bar.set(0)
        bar.pack(side="left", fill="x", expand=True, padx=10)
        nilai = ctk.CTkLabel(
            baris,
            text="0%",
            font=(ui_kit.FONT, 11, "bold"),
            text_color=ui_kit.HIJAU,
            width=42,
            anchor="e",
        )
        nilai.pack(side="right")
        return bar, nilai

    # --------------------------------------------------------
    def muat(self):
        """Membaca ulang seluruh angka dashboard."""
        data = AgriUnoController.get_statistik()
        user = self.app.user

        jam = datetime.now().hour
        sapaan_waktu = (
            "Selamat pagi"
            if jam < 11
            else "Selamat siang"
            if jam < 15
            else "Selamat sore"
            if jam < 19
            else "Selamat malam"
        )
        tanggal = datetime.now()
        tanggal_id = "%s, %d %s %d" % (
            self._HARI[tanggal.weekday()],
            tanggal.day,
            self._BULAN[tanggal.month],
            tanggal.year,
        )
        self.sapaan.configure(text="%s, %s  •  %s" % (sapaan_waktu, user["nama"], tanggal_id))

        self.kpi["petani"].configure(text=str(data["total_petani"]))
        self.kpi["lot"].configure(text=str(data["total_lot"]))
        self.kpi["alokasi"].configure(text=str(data["total_alokasi"]))

        total_setor = float(data["total_setor"])
        total_kirim = float(data["total_kirim"])
        self.berat["setor"].configure(text="%.2f Kg" % total_setor)
        self.berat["kirim"].configure(text="%.2f Kg" % total_kirim)
        self.berat["sisa"].configure(text="%.2f Kg" % (total_setor - total_kirim))

        rasio_alokasi = (total_kirim / total_setor) if total_setor else 0.0
        rasio_aktif = (
            float(data["petani_aktif"] / data["total_petani"]) if data["total_petani"] else 0.0
        )
        for kunci, nilai in (
            ("alokasi", min(rasio_alokasi, 1.0)),
            ("aktif", min(rasio_aktif, 1.0)),
        ):
            self.progres[kunci][0].set(nilai)
            self.progres[kunci][1].configure(text="%d%%" % round(nilai * 100))

        # Panel komoditas terbanyak
        for anak in self.kartu_komo_isi.winfo_children():
            anak.destroy()
        komoditas = data["komoditas"]
        if komoditas:
            terbesar = float(komoditas[0]["berat"] or 1)
            palet = (
                (ui_kit.HIJAU, "#e5ece7"),
                (ui_kit.BIRU, "#e3ecf5"),
                (ui_kit.AMBER, "#f1ece1"),
                (ui_kit.MERAH, "#f6e4e4"),
                (ui_kit.HIJAU_TEKS, "#e5ece7"),
            )
            for urutan, item in enumerate(komoditas):
                warna_bar, latar_bar = palet[urutan % len(palet)]
                baris = ctk.CTkFrame(self.kartu_komo_isi, fg_color="transparent")
                baris.pack(fill="x", pady=6)
                ctk.CTkLabel(
                    baris,
                    text=item["jenis_komoditas"],
                    font=(ui_kit.FONT, 11),
                    text_color=ui_kit.TEKS,
                ).pack(anchor="w")
                bar = ctk.CTkProgressBar(
                    baris,
                    height=6,
                    corner_radius=3,
                    progress_color=warna_bar,
                    fg_color=latar_bar,
                )
                bar.set(float(item["berat"] or 0) / terbesar)
                bar.pack(fill="x", pady=(2, 0))
                ctk.CTkLabel(
                    baris,
                    text="%.2f Kg" % float(item["berat"]),
                    font=(ui_kit.FONT, 9),
                    text_color=ui_kit.REDUP,
                ).pack(anchor="w")
        else:
            ui_kit.status_kosong(self.kartu_komo_isi, "Belum ada data panen.")

        # Aktivitas terkini
        for anak in self.isi_aktivitas.winfo_children():
            anak.destroy()
        aktivitas = data["aktivitas"]
        if not aktivitas:
            ui_kit.status_kosong(self.isi_aktivitas, "Belum ada aktivitas tercatat.")
            return

        for kolom in range(3):
            self.isi_aktivitas.grid_columnconfigure(kolom, weight=1)
        for idx, item in enumerate(aktivitas):
            jenis = item["jenis"]
            latar, warna = ui_kit.STATUS_WARNA.get(
                item["status"], (ui_kit.KEPALA_TABEL, ui_kit.REDUP)
            )
            baris = ctk.CTkFrame(
                self.isi_aktivitas, fg_color=ui_kit.ZEBRA if idx % 2 else "white", corner_radius=10
            )
            baris.grid(row=idx, column=0, sticky="ew", columnspan=3, pady=1)

            ikon = "⬒" if jenis == "panen" else "➤"
            ctk.CTkLabel(
                baris,
                text=ikon,
                font=(ui_kit.FONT, 13, "bold"),
                text_color=ui_kit.HIJAU_TEKS if jenis == "panen" else ui_kit.BIRU,
                width=30,
            ).pack(side="left", padx=(12, 4))

            teks_utama = "%s — %s Kg" % (item["keterangan"], item["berat"])
            ctk.CTkLabel(
                baris, text=teks_utama, font=(ui_kit.FONT, 12), text_color=ui_kit.TEKS, anchor="w"
            ).pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                baris,
                text=str(item["nama_petani"] or ""),
                font=(ui_kit.FONT, 10),
                text_color=ui_kit.REDUP,
            ).pack(side="left", padx=8)

            if jenis == "distribusi":
                ui_kit.chip(baris, item["status"], latar, warna).pack(side="left", padx=6)
            ctk.CTkLabel(
                baris, text=str(item["tgl"] or ""), font=(ui_kit.FONT, 10), text_color=ui_kit.REDUP
            ).pack(side="right", padx=12)
