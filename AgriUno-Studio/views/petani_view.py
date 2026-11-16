"""Tampilan master-detail data petani beserta formulirnya."""

from tkinter import messagebox

import customtkinter as ctk

import customtkinter as ctk

from config import ui_kit
from controllers.auth_controller import AuthController
from controllers.controller import AgriUnoController
from config.ui_kit import DialogModal
from views.base_view import HalamanDasar

class PetaniView(HalamanDasar):
    """Master-detail data petani."""

    _LABEL_TAMBAH = "+  Petani Baru"

    def __init__(self, parent, app):
        super().__init__(
            parent,
            app,
            "Data Petani",
            "Master data penyetor hasil panen yang tercatat pada gudang.",
        )

    # --------------------------------------------------------
    def _bangun_tabel(self, kartu_tabel):
        """Menyusun tabel petani."""
        kepala = ctk.CTkFrame(kartu_tabel, fg_color="transparent")
        kepala.pack(fill="x", padx=20, pady=(16, 4))
        ctk.CTkLabel(
            kepala, text="Daftar Petani", font=(ui_kit.FONT, 13, "bold"), text_color=ui_kit.TEKS
        ).pack(side="left")

        kolom = (
            ("id", "ID", 48, "center"),
            ("nama", "Nama Petani", 150, "w"),
            ("lokasi", "Lokasi Lahan", 152, "w"),
            ("komo", "Komoditas Utama", 122, "w"),
            ("lot", "Lot", 44, "center"),
            ("total", "Total (Kg)", 90, "center"),
        )
        wadah, self.tree = ui_kit.tabel(kartu_tabel, kolom, tinggi=12)
        wadah.pack(fill="both", expand=True, padx=20, pady=(4, 16))
        self.tree.bind("<ButtonRelease-1>", self._saat_pilih)

    # --------------------------------------------------------
    def muat(self):
        """Menyegarkan tabel dari basis data."""
        for baris in self.tree.get_children():
            self.tree.delete(baris)

        data = AgriUnoController.get_petani(self.e_cari.get())
        for idx, item in enumerate(data):
            self.tree.insert(
                "",
                "end",
                iid=str(item["id_petani"]),
                values=(
                    item["id_petani"],
                    item["nama_petani"],
                    item["lokasi_lahan"],
                    item["komoditas_utama"],
                    item["jml_lot"],
                    "%.2f" % float(item["total_setor"]),
                ),
                tags=(ui_kit.tag_zebra(idx),),
            )
        self.chip_jumlah.configure(text="%d petani" % len(data))

        # Jaga panel detail tetap sinkron bila baris terpilih masih ada.
        if self.terpilih is not None:
            if self.tree.exists(str(self.terpilih)):
                self.tree.selection_set(str(self.terpilih))
                self._muat_detail()
            else:
                self.terpilih = None
                self._detail_kosong()

    # --------------------------------------------------------
    def _saat_pilih(self, _event=None):
        """Menampilkan rincian petani terpilih."""
        fokus = self.tree.focus()
        if not fokus:
            return
        self.terpilih = int(fokus)
        self._muat_detail()

    # --------------------------------------------------------
    def _cari_data(self):
        """Mengembalikan baris data petani terpilih."""
        for item in AgriUnoController.get_petani():
            if int(item["id_petani"]) == self.terpilih:
                return item
        return None

    # --------------------------------------------------------
    def _muat_detail(self):
        """Panel rincian petani beserta aksinya."""
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
            text=data["nama_petani"],
            font=(ui_kit.FONT, 16, "bold"),
            text_color=ui_kit.TEKS,
            wraplength=260,
            justify="left",
        ).pack(anchor="w")
        ui_kit.chip(tubuh, "ID %s" % data["id_petani"]).pack(anchor="w", pady=(4, 10))

        for label, nilai in (
            ("Lokasi Lahan", data["lokasi_lahan"]),
            ("Komoditas Utama", data["komoditas_utama"]),
            ("Jumlah Lot Panen", "%s lot" % data["jml_lot"]),
            ("Total Setoran", "%.2f Kg" % float(data["total_setor"])),
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

        if AuthController.boleh(self.app.user, "kelola"):
            aksi = ctk.CTkFrame(tubuh, fg_color="transparent")
            aksi.pack(side="bottom", fill="x", pady=(12, 0))
            ui_kit.tombol(aksi, "Ubah", self._buka_form_ubah, jenis="sekunder", lebar=110).pack(
                side="right"
            )
            if AuthController.boleh(self.app.user, "hapus"):
                ui_kit.tombol(aksi, "Hapus", self._hapus, jenis="bahaya", lebar=96).pack(
                    side="right", padx=(0, 8)
                )

    # --------------------------------------------------------
    def _buka_form_tambah(self):
        DialogFormPetani(self.app, on_selesai=self._setelah_simpan)

    def _buka_form_ubah(self):
        if not self._pilih_baris_terpilih("ubah"):
            return
        DialogFormPetani(self.app, data=self._cari_data(), on_selesai=self._setelah_simpan)

    def _setelah_simpan(self, ok, pesan):
        ui_kit.toast(self.app, pesan, jenis="sukses" if ok else "galat")
        self.muat()

    def _hapus(self):
        if not self._pilih_baris_terpilih("hapus"):
            return
        if not messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus petani ini?"):
            return
        ok, pesan = AgriUnoController.hapus_petani(self.app.user, self.terpilih)
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
                "Pilih data petani yang ingin " + aksi + "!",
                jenis="galat",
            )
            return False
        return True


class DialogFormPetani(DialogModal):
    """Dialog tambah/ubah data petani."""

    def __init__(self, master, data=None, on_selesai=None):
        super().__init__(master, "Formulir Data Petani", lebar=560)
        self.data = data
        self.on_selesai = on_selesai

        bingkai = ctk.CTkFrame(self, fg_color="transparent")
        bingkai.pack(padx=30, pady=24)

        ctk.CTkLabel(
            bingkai,
            text="Ubah Data Petani" if data else "Petani Baru",
            font=(ui_kit.FONT, 18, "bold"),
            text_color=ui_kit.TEKS,
        ).pack(anchor="w")

        kolom_nama, self.e_nama = ui_kit.bidang(
            bingkai, "Nama Petani", "Contoh: Siti Halimah", lebar=480
        )
        kolom_nama.pack(fill="x", pady=(12, 0))
        kolom_lokasi, self.e_lokasi = ui_kit.bidang(
            bingkai, "Lokasi Lahan", "Contoh: Desa Wonosari, Kec. Poncowati", lebar=480, wajib=False
        )
        kolom_lokasi.pack(fill="x", pady=(10, 0))
        kolom_komo, self.e_komo = ui_kit.bidang(
            bingkai, "Komoditas Utama", "Contoh: Beras Organik", lebar=480, wajib=False
        )
        kolom_komo.pack(fill="x", pady=(10, 0))

        if data:
            self.e_nama.insert(0, data["nama_petani"])
            self.e_lokasi.insert(0, data["lokasi_lahan"])
            self.e_komo.insert(0, data["komoditas_utama"])

        self.pesan = ctk.CTkLabel(
            bingkai,
            text="",
            font=(ui_kit.FONT, 12),
            text_color=ui_kit.MERAH,
            wraplength=480,
            justify="left",
        )
        self.pesan.pack(fill="x", pady=(8, 0))

        self._baris_aksi(bingkai, "Simpan Data", self.proses)

    # --------------------------------------------------------
    def proses(self):
        """Menyimpan data petani."""
        ok, pesan = AgriUnoController.simpan_petani(
            getattr(self.master, "user", None),
            self.data["id_petani"] if self.data else None,
            self.e_nama.get(),
            self.e_lokasi.get(),
            self.e_komo.get(),
        )
        self.pesan.configure(text=pesan)
        if ok:
            ui_kit.toast(self.master, pesan, jenis="sukses")
            if callable(self.on_selesai):
                self.on_selesai(True, pesan)
            self.after(1000, self.destroy)
