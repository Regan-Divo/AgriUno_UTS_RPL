"""Tampilan master-detail lot setoran panen beserta formulirnya."""

from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

import customtkinter as ctk

from config import ui_kit
from controllers.auth_controller import AuthController
from controllers.controller import AgriUnoController
from config.ui_kit import DialogModal
from views.base_view import HalamanDasar
from views.distribusi_view import DialogFormDistribusi

class PanenView(HalamanDasar):
    """Master-detail lot setoran panen beserta sisa stok."""

    _LABEL_TAMBAH = "+  Catat Setoran"

    def __init__(self, parent, app):
        super().__init__(
            parent,
            app,
            "Inventori Hasil Panen",
            "Pencatatan lot setoran panen yang masuk ke gudang beserta sisa stoknya.",
        )

    # --------------------------------------------------------
    def _bangun_tabel(self, kartu_tabel):
        kepala = ctk.CTkFrame(kartu_tabel, fg_color="transparent")
        kepala.pack(fill="x", padx=20, pady=(16, 4))
        ctk.CTkLabel(
            kepala, text="Daftar Lot Setoran", font=(ui_kit.FONT, 13, "bold"), text_color=ui_kit.TEKS
        ).pack(side="left")

        kolom = (
            ("id", "ID", 48, "center"),
            ("tgl", "Tanggal", 96, "center"),
            ("petani", "Petani Penyetor", 180, "w"),
            ("komo", "Jenis Komoditas", 150, "w"),
            ("berat", "Berat (Kg)", 90, "center"),
            ("sisa", "Sisa (Kg)", 90, "center"),
        )
        wadah, self.tree = ui_kit.tabel(kartu_tabel, kolom, tinggi=12)
        wadah.pack(fill="both", expand=True, padx=20, pady=(4, 16))
        self.tree.bind("<ButtonRelease-1>", self._saat_pilih)

    # --------------------------------------------------------
    def muat(self):
        """Menyegarkan tabel lot panen."""
        for baris in self.tree.get_children():
            self.tree.delete(baris)

        data = AgriUnoController.get_panen(self.e_cari.get())
        for idx, item in enumerate(data):
            sisa = float(item["sisa_stok"])
            berat = float(item["jumlah_berat"])
            self.tree.insert(
                "",
                "end",
                iid=str(item["id_panen"]),
                values=(
                    item["id_panen"],
                    str(item["tgl_panen"]),
                    item["nama_petani"] or "-",
                    item["jenis_komoditas"],
                    "%.2f" % berat,
                    "%.2f" % sisa,
                ),
                tags=(ui_kit.tag_zebra(idx),),
            )
        self.chip_jumlah.configure(text="%d lot" % len(data))

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
        for item in AgriUnoController.get_panen():
            if int(item["id_panen"]) == self.terpilih:
                return item
        return None

    # --------------------------------------------------------
    def _muat_detail(self):
        """Panel rincian lot panen dengan indikator pemakaian stok."""
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
            text="Lot #%s" % data["id_panen"],
            font=(ui_kit.FONT, 16, "bold"),
            text_color=ui_kit.TEKS,
        ).pack(anchor="w")
        ui_kit.chip(tubuh, str(data["tgl_panen"])).pack(anchor="w", pady=(4, 10))

        for label, nilai in (
            ("Petani Penyetor", data["nama_petani"] or "-"),
            ("Jenis Komoditas", data["jenis_komoditas"]),
            ("Berat Awal", "%.2f Kg" % float(data["jumlah_berat"])),
            ("Sudah Dialokasikan", "%.2f Kg" % float(data["total_dikirim"])),
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

        # Indikator sisa stok
        sisa = float(data["sisa_stok"])
        berat = float(data["jumlah_berat"]) or 1.0
        ctk.CTkLabel(tubuh, text="Sisa Stok", font=(ui_kit.FONT, 10), text_color=ui_kit.REDUP).pack(
            anchor="w", pady=(10, 0)
        )
        bar = ctk.CTkProgressBar(
            tubuh,
            height=8,
            corner_radius=4,
            progress_color=ui_kit.HIJAU_HOVER if sisa > 0 else ui_kit.MERAH,
            fg_color="#e5ece7",
        )
        bar.set(max(0.0, min(1.0, sisa / berat)))
        bar.pack(fill="x", pady=(4, 0))
        ctk.CTkLabel(
            tubuh,
            text="%.2f Kg tersisa dari %.2f Kg" % (sisa, berat),
            font=(ui_kit.FONT, 10),
            text_color=ui_kit.REDUP,
        ).pack(anchor="w", pady=(2, 0))

        if AuthController.boleh(self.app.user, "kelola"):
            aksi = ctk.CTkFrame(tubuh, fg_color="transparent")
            aksi.pack(side="bottom", fill="x", pady=(12, 0))
            ui_kit.tombol(aksi, "Ubah", self._buka_form_ubah, jenis="sekunder", lebar=96).pack(
                side="right"
            )
            if AuthController.boleh(self.app.user, "hapus"):
                ui_kit.tombol(aksi, "Hapus", self._hapus, jenis="bahaya", lebar=90).pack(
                    side="right", padx=(0, 8)
                )
            ui_kit.tombol(aksi, "Alokasikan", self._alokasikan, jenis="lembut", lebar=110).pack(
                side="left"
            )

    # --------------------------------------------------------
    def _buka_form_tambah(self):
        DialogFormPanen(self.app, on_selesai=self._setelah_simpan)

    def _buka_form_ubah(self):
        if not self._pilih_baris_terpilih("ubah"):
            return
        DialogFormPanen(self.app, data=self._cari_data(), on_selesai=self._setelah_simpan)

    def _setelah_simpan(self, ok, pesan):
        ui_kit.toast(self.app, pesan, jenis="sukses" if ok else "galat")
        self.muat()

    def _hapus(self):
        if not self._pilih_baris_terpilih("hapus"):
            return
        if not messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus lot panen ini?"):
            return
        ok, pesan = AgriUnoController.hapus_panen(self.app.user, self.terpilih)
        ui_kit.toast(self.app, pesan, jenis="sukses" if ok else "galat")
        if ok:
            self.terpilih = None
            self._detail_kosong()
        self.muat()

    def _alokasikan(self):
        """Membuka dialog alokasi dengan lot ini terpilih lebih dulu."""
        DialogFormDistribusi(self.app, id_panen_awal=self.terpilih, on_selesai=self._setelah_simpan)


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
                "Pilih data panen yang ingin " + aksi + "!",
                jenis="galat",
            )
            return False
        return True


class DialogFormPanen(DialogModal):
    """Dialog tambah/ubah lot setoran panen."""

    def __init__(self, master, data=None, on_selesai=None):
        super().__init__(master, "Formulir Setoran Panen", lebar=580)
        self.data = data
        self.on_selesai = on_selesai
        self._komo_petani = {}

        bingkai = ctk.CTkFrame(self, fg_color="transparent")
        bingkai.pack(padx=30, pady=24)

        ctk.CTkLabel(
            bingkai,
            text="Ubah Lot Setoran" if data else "Catat Setoran Baru",
            font=(ui_kit.FONT, 18, "bold"),
            text_color=ui_kit.TEKS,
        ).pack(anchor="w")

        daftar_petani = AgriUnoController.get_pilihan_petani()
        nilai = ["- Pilih Petani -"]
        for item in daftar_petani:
            label = "%s - %s" % (item["id_petani"], item["nama_petani"])
            nilai.append(label)
            self._komo_petani[label] = item["komoditas_utama"]

        kolom_petani, self.opt_petani = ui_kit.pilihan(bingkai, "Petani Penyetor", nilai, lebar=500)
        kolom_petani.pack(fill="x", pady=(12, 0))
        self.opt_petani.configure(command=self._isi_komoditas)

        kolom_komo, self.e_komo = ui_kit.bidang(
            bingkai, "Jenis Komoditas", "Terisi otomatis dari master data", lebar=500
        )
        kolom_komo.pack(fill="x", pady=(10, 0))

        baris = ctk.CTkFrame(bingkai, fg_color="transparent")
        baris.pack(fill="x", pady=(10, 0))
        baris.grid_columnconfigure(0, weight=1)
        baris.grid_columnconfigure(1, weight=1)
        kolom_berat, self.e_berat = ui_kit.bidang(
            baris, "Jumlah Berat (Kg)", "Contoh: 120", lebar=240
        )
        kolom_berat.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        kolom_tgl, self.e_tgl = ui_kit.bidang(
            baris, "Tanggal Panen", "YYYY-MM-DD", lebar=240, wajib=False
        )
        kolom_tgl.grid(row=0, column=1, sticky="ew")
        self.e_tgl.insert(0, datetime.now().strftime("%Y-%m-%d"))

        if data:
            label_cocok = next(
                (
                    label
                    for label in self._komo_petani
                    if str(label).split(" - ")[0] == str(data["id_petani"])
                ),
                None,
            )
            if label_cocok:
                self.opt_petani.set(label_cocok)
            self.e_komo.insert(0, data["jenis_komoditas"])
            self.e_berat.insert(0, "%.2f" % float(data["jumlah_berat"]))
            self.e_tgl.delete(0, "end")
            self.e_tgl.insert(0, str(data["tgl_panen"]))

        self.pesan = ctk.CTkLabel(
            bingkai,
            text="",
            font=(ui_kit.FONT, 12),
            text_color=ui_kit.MERAH,
            wraplength=500,
            justify="left",
        )
        self.pesan.pack(fill="x", pady=(8, 0))

        self._baris_aksi(bingkai, "Simpan Setoran", self.proses)

    # --------------------------------------------------------
    def _isi_komoditas(self, _pilihan=None):
        """Mengisi jenis komoditas dari master data petani terpilih."""
        komo = self._komo_petani.get(self.opt_petani.get())
        if komo:
            self.e_komo.delete(0, "end")
            self.e_komo.insert(0, komo)

    def proses(self):
        """Menyimpan lot setoran panen."""
        label = self.opt_petani.get()
        id_petani = label.split(" - ")[0] if " - " in label else None
        ok, pesan = AgriUnoController.simpan_panen(
            self._app_user(),
            self.data["id_panen"] if self.data else None,
            id_petani,
            self.e_komo.get(),
            self.e_berat.get(),
            self.e_tgl.get(),
        )
        self.pesan.configure(text=pesan)
        if ok:
            ui_kit.toast(self.master, pesan, jenis="sukses")
            if callable(self.on_selesai):
                self.on_selesai(True, pesan)
            self.after(1000, self.destroy)

    def _app_user(self):
        """Mengambil objek user aktif dari jendela induk."""
        induk = self.master
        return getattr(induk, "user", None)
