"""Tampilan master-detail alokasi pengiriman dengan alur status."""

from tkinter import messagebox

import customtkinter as ctk

from config import constants, ui_kit
from config.ui_kit import DialogModal
from controllers.auth_controller import AuthController
from controllers.controller import AgriUnoController
from views.base_view import HalamanDasar


class DistribusiView(HalamanDasar):
    """Master-detail alokasi pengiriman dengan alur status satu-klik."""

    _LABEL_TAMBAH = "+  Alokasi Baru"
    _FILTER_STATUS = ("Semua",) + constants.STATUS_DAFTAR

    def __init__(self, parent, app):
        super().__init__(
            parent,
            app,
            "Alokasi Distribusi",
            "Pengiriman hasil panen dari gudang menuju distributor.",
        )

    # --------------------------------------------------------
    def _bangun_tabel(self, kartu_tabel):
        kepala = ctk.CTkFrame(kartu_tabel, fg_color="transparent")
        kepala.pack(fill="x", padx=20, pady=(16, 4))
        ctk.CTkLabel(
            kepala,
            text="Daftar Alokasi",
            font=(ui_kit.FONT, 13, "bold"),
            text_color=ui_kit.TEKS,
        ).pack(side="left")

        # Chip filter status
        baris_filter = ctk.CTkFrame(kepala, fg_color="transparent")
        baris_filter.pack(side="right")
        self.chip_filter = {}
        for status in self._FILTER_STATUS:
            warna_latar, warna_teks = ui_kit.STATUS_WARNA.get(
                status, (ui_kit.KEPALA_TABEL, ui_kit.REDUP)
            )
            b = ctk.CTkButton(
                baris_filter,
                text=status,
                width=64 if status != "Semua" else 70,
                height=26,
                corner_radius=999,
                font=(ui_kit.FONT, 10, "bold"),
                fg_color=ui_kit.HIJAU,
                hover_color=ui_kit.HIJAU_HOVER,
                text_color="white",
                command=lambda s=status: self._filter(s),
            )
            b.pack(side="left", padx=3)
            self.chip_filter[status] = b
        self._filter_aktif = "Semua"
        self._warnai_filter()

        kolom = (
            ("id", "ID", 48, "center"),
            ("tujuan", "Tujuan Pengiriman", 178, "w"),
            ("komo", "Komoditas", 132, "w"),
            ("jumlah", "Jumlah (Kg)", 94, "center"),
            ("status", "Status", 128, "center"),
        )
        wadah, self.tree = ui_kit.tabel(kartu_tabel, kolom, tinggi=12)
        wadah.pack(fill="both", expand=True, padx=20, pady=(4, 16))
        self.tree.bind("<ButtonRelease-1>", self._saat_pilih)

    # --------------------------------------------------------
    def _warnai_filter(self):
        """Menandai chip filter yang aktif."""
        for status, tombol in self.chip_filter.items():
            if status == self._filter_aktif:
                latar, teks = ui_kit.STATUS_WARNA.get(status, (ui_kit.HIJAU, "white"))
                if status == "Semua":
                    latar, teks = ui_kit.HIJAU, "white"
                tombol.configure(fg_color=latar, text_color=teks)
            else:
                tombol.configure(fg_color=ui_kit.ZEBRA, text_color=ui_kit.REDUP)

    def _filter(self, status):
        """Mengganti filter status dan menyegarkan tabel."""
        self._filter_aktif = status
        self._warnai_filter()
        self.muat()

    # --------------------------------------------------------
    def muat(self):
        """Menyegarkan tabel alokasi."""
        for baris in self.tree.get_children():
            self.tree.delete(baris)

        data = AgriUnoController.get_distribusi(self.e_cari.get(), self._filter_aktif)
        for idx, item in enumerate(data):
            self.tree.insert(
                "",
                "end",
                iid=str(item["id_distribusi"]),
                values=(
                    item["id_distribusi"],
                    item["tujuan_pengiriman"],
                    item["jenis_komoditas"] or "-",
                    "%.2f" % float(item["jumlah_dikirim"]),
                    item["status_pengiriman"],
                ),
                tags=(ui_kit.tag_zebra(idx),),
            )
        self.chip_jumlah.configure(text="%d alokasi" % len(data))

        if self.terpilih is not None:
            if self.tree.exists(str(self.terpilih)):
                self.tree.selection_set(str(self.terpilih))
                self._muat_detail()
            else:
                self.terpilih = None
                self._detail_kosong()

    # --------------------------------------------------------
    def _saat_pilih(self, _event=None):
        fokus = self.tree.focus()
        if not fokus:
            return
        self.terpilih = int(fokus)
        self._muat_detail()

    def _cari_data(self):
        for item in AgriUnoController.get_distribusi():
            if int(item["id_distribusi"]) == self.terpilih:
                return item
        return None

    # --------------------------------------------------------
    def _muat_detail(self):
        """Panel rincian alokasi dengan stepper alur status."""
        data = self._cari_data()
        if not data:
            self.terpilih = None
            self._detail_kosong()
            return

        for anak in self.kartu_detail.winfo_children():
            anak.destroy()

        tubuh = ctk.CTkFrame(self.kartu_detail, fg_color="transparent")
        tubuh.pack(fill="both", expand=True, padx=18, pady=16)

        ctk.CTkLabel(
            tubuh,
            text="Alokasi #%s" % data["id_distribusi"],
            font=(ui_kit.FONT, 16, "bold"),
            text_color=ui_kit.TEKS,
        ).pack(anchor="w")

        latar, warna = ui_kit.pil_status(data["status_pengiriman"])
        ui_kit.chip(tubuh, data["status_pengiriman"], latar, warna).pack(anchor="w", pady=(4, 10))

        for label, nilai in (
            ("Tujuan Pengiriman", data["tujuan_pengiriman"]),
            ("Komoditas", data["jenis_komoditas"] or "-"),
            ("Petani Asal", data["nama_petani"] or "-"),
            ("Jumlah Dikirim", "%.2f Kg" % float(data["jumlah_dikirim"])),
        ):
            ctk.CTkLabel(tubuh, text=label, font=(ui_kit.FONT, 10), text_color=ui_kit.REDUP).pack(
                anchor="w", pady=(8, 0)
            )
            ctk.CTkLabel(
                tubuh,
                text=str(nilai),
                font=(ui_kit.FONT, 12, "bold"),
                text_color=ui_kit.TEKS,
                wraplength=260,
                justify="left",
            ).pack(anchor="w")

        # Stepper alur status
        ctk.CTkLabel(
            tubuh, text="Alur Pengiriman", font=(ui_kit.FONT, 10), text_color=ui_kit.REDUP
        ).pack(anchor="w", pady=(14, 4))
        baris_langkah = ctk.CTkFrame(tubuh, fg_color="transparent")
        baris_langkah.pack(fill="x")
        for idx, status in enumerate(constants.STATUS_DAFTAR):
            sudah = constants.STATUS_DAFTAR.index(data["status_pengiriman"]) >= idx
            warna = ui_kit.HIJAU_HOVER if sudah else ui_kit.GARIS
            titik = ctk.CTkFrame(
                baris_langkah, fg_color=warna, corner_radius=999, width=14, height=14
            )
            titik.pack(side="left", padx=(0, 4))
            ctk.CTkLabel(
                baris_langkah,
                text=status,
                font=(ui_kit.FONT, 9),
                text_color=ui_kit.TEKS if sudah else ui_kit.REDUP,
            ).pack(side="left")
            if idx < len(constants.STATUS_DAFTAR) - 1:
                ctk.CTkLabel(
                    baris_langkah, text="—", font=(ui_kit.FONT, 9), text_color=ui_kit.GARIS
                ).pack(side="left", padx=3)

        if AuthController.boleh(self.app.user, "kelola"):
            aksi = ctk.CTkFrame(tubuh, fg_color="transparent")
            aksi.pack(side="bottom", fill="x", pady=(12, 0))

            if data["status_pengiriman"] in constants.ALUR_STATUS:
                berikut = constants.ALUR_STATUS[data["status_pengiriman"]]
                ui_kit.tombol(
                    aksi, "→ " + berikut, self._lanjut_status, jenis="primer", lebar=190
                ).pack(side="right")
            ui_kit.tombol(aksi, "Ubah", self._buka_form_ubah, jenis="sekunder", lebar=84).pack(
                side="right", padx=(0, 8)
            )
            if (
                AuthController.boleh(self.app.user, "hapus")
                and data["status_pengiriman"] != constants.STATUS_TERKIRIM
            ):
                ui_kit.tombol(aksi, "Hapus", self._hapus, jenis="bahaya", lebar=84).pack(
                    side="left"
                )

    # --------------------------------------------------------
    def _lanjut_status(self):
        """Memajukan status alokasi satu tahap."""
        ok, pesan = AgriUnoController.lanjut_status(self.app.user, self.terpilih)
        ui_kit.toast(self.app, pesan, jenis="sukses" if ok else "galat")
        self.muat()

    def _buka_form_tambah(self):
        DialogFormDistribusi(self.app, on_selesai=self._setelah_simpan)

    def _buka_form_ubah(self):
        if not self._pilih_baris_terpilih("ubah"):
            return
        DialogFormDistribusi(self.app, data=self._cari_data(), on_selesai=self._setelah_simpan)

    def _setelah_simpan(self, ok, pesan):
        ui_kit.toast(self.app, pesan, jenis="sukses" if ok else "galat")
        self.muat()

    def _hapus(self):
        if not self._pilih_baris_terpilih("hapus"):
            return
        if not messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus alokasi ini?"):
            return
        ok, pesan = AgriUnoController.hapus_distribusi(self.app.user, self.terpilih)
        ui_kit.toast(self.app, pesan, jenis="sukses" if ok else "galat")
        if ok:
            self.terpilih = None
            self._detail_kosong()
        self.muat()

    # --------------------------------------------------------
    # ALIAS METODE KATALOG KELAS (dokumentasi teknis 4.7)
    # --------------------------------------------------------
    def load_table(self):
        """Menyegarkan tabel data (alias ``muat``)."""
        return self.muat()

    def simpan(self):
        """Membuka formulir tambah data baru (alias ``_buka_form_tambah``)."""
        return self._buka_form_tambah()

    def ubah(self):
        """Membuka formulir ubah data terpilih (alias ``_buka_form_ubah``)."""
        return self._buka_form_ubah()

    def hapus(self):
        """Menghapus data terpilih (alias ``_hapus``)."""
        return self._hapus()

    def on_select(self, _event=None):
        """Menangani pemilihan baris pada tabel (alias ``_saat_pilih``)."""
        return self._saat_pilih(_event)

    # --------------------------------------------------------
    def _pilih_baris_terpilih(self, aksi):
        """Memastikan ada baris terpilih sebelum menjalankan aksi."""
        if self.terpilih is None:
            ui_kit.toast(
                self.app,
                "Pilih data distribusi yang ingin " + aksi + "!",
                jenis="galat",
            )
            return False
        return True


class DialogFormDistribusi(DialogModal):
    """Dialog tambah/ubah alokasi distribusi."""

    def __init__(self, master, data=None, id_panen_awal=None, on_selesai=None):
        super().__init__(master, "Formulir Alokasi Pengiriman", lebar=580)
        self.data = data
        self.on_selesai = on_selesai
        self._sisa_lot = {}

        bingkai = ctk.CTkFrame(self, fg_color="transparent")
        bingkai.pack(padx=30, pady=24)

        ctk.CTkLabel(
            bingkai,
            text="Ubah Alokasi" if data else "Alokasi Pengiriman Baru",
            font=(ui_kit.FONT, 18, "bold"),
            text_color=ui_kit.TEKS,
        ).pack(anchor="w")

        daftar_lot = AgriUnoController.get_panen()
        nilai = ["- Pilih Lot Panen -"]
        for item in daftar_lot:
            label = "#%s - %s (sisa %s Kg)" % (
                item["id_panen"],
                item["jenis_komoditas"],
                item["sisa_stok"],
            )
            nilai.append(label)
            self._sisa_lot[label] = item["id_panen"]

        kolom_lot, self.opt_lot = ui_kit.pilihan(bingkai, "Lot Panen", nilai, lebar=500)
        kolom_lot.pack(fill="x", pady=(12, 0))

        kolom_tujuan, self.e_tujuan = ui_kit.bidang(
            bingkai, "Tujuan Pengiriman", "Contoh: Pasar Induk Karya", lebar=500
        )
        kolom_tujuan.pack(fill="x", pady=(10, 0))

        baris = ctk.CTkFrame(bingkai, fg_color="transparent")
        baris.pack(fill="x", pady=(10, 0))
        baris.grid_columnconfigure(0, weight=1)
        baris.grid_columnconfigure(1, weight=1)
        kolom_jumlah, self.e_jumlah = ui_kit.bidang(
            baris, "Jumlah Dikirim (Kg)", "Contoh: 50", lebar=240
        )
        kolom_jumlah.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        if data:
            label_cocok = next(
                (
                    label
                    for label in self._sisa_lot
                    if str(label).split("#")[1].split(" - ")[0] == str(data["id_panen"])
                ),
                None,
            )
            if label_cocok:
                self.opt_lot.set(label_cocok)
            self.e_tujuan.insert(0, data["tujuan_pengiriman"])
            self.e_jumlah.insert(0, "%.2f" % float(data["jumlah_dikirim"]))
        elif id_panen_awal:
            label_cocok = next(
                (
                    label
                    for label in self._sisa_lot
                    if str(label).split("#")[1].split(" - ")[0] == str(id_panen_awal)
                ),
                None,
            )
            if label_cocok:
                self.opt_lot.set(label_cocok)

        self.pesan = ctk.CTkLabel(
            bingkai,
            text="",
            font=(ui_kit.FONT, 12),
            text_color=ui_kit.MERAH,
            wraplength=500,
            justify="left",
        )
        self.pesan.pack(fill="x", pady=(8, 0))

        self._baris_aksi(bingkai, "Simpan Alokasi", self.proses)

    # --------------------------------------------------------
    def proses(self):
        """Menyimpan alokasi distribusi."""
        label = self.opt_lot.get()
        id_panen = self._sisa_lot.get(label)
        status = self.data["status_pengiriman"] if self.data else constants.STATUS_DIPROSES
        ok, pesan = AgriUnoController.simpan_distribusi(
            getattr(self.master, "user", None),
            self.data["id_distribusi"] if self.data else None,
            id_panen,
            self.e_tujuan.get(),
            self.e_jumlah.get(),
            status,
        )
        self.pesan.configure(text=pesan)
        if ok:
            ui_kit.toast(self.master, pesan, jenis="sukses")
            if callable(self.on_selesai):
                self.on_selesai(True, pesan)
            self.after(1000, self.destroy)
