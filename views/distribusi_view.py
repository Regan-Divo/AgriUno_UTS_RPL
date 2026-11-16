"""
==========================================================
HALAMAN DISTRIBUSI - AGRIUNO
==========================================================
Menyediakan form isian dan tabel data untuk mengelola alokasi
pengiriman hasil panen menuju distributor.

Tampilan dibangun dari kit antarmuka bersama (``config/ui_kit``):
kartu bersudut membulat, label di atas isian, tabel dengan baris
selang-seling dan status berwarna, serta hierarki tombol yang
konsisten.

Peningkatan terhadap versi UTS:

1. **Pemilihan lot panen memakai kotak daftar (dropdown)** yang
   menampilkan lot beserta sisa stoknya, sehingga operator dapat
   langsung melihat ketersediaan barang sebelum mengalokasikan.
2. **Informasi sisa stok** ditampilkan pada tabel alokasi.
3. **Alokasi berstatus "Terkirim" dikunci** (BR-09): tombol Ubah
   dan Hapus ditolak untuk baris yang sudah final.
4. **Otorisasi berbasis peran** (RBAC) untuk modul ini.
"""

from tkinter import messagebox

import customtkinter as ctk

from config.constants import STATUS_DIPROSES, STATUS_PENGIRIMAN
from config.ui_kit import (
    FONT,
    TS_SEKSI,
    WARNA_LATAR,
    WARNA_REDUP,
    WARNA_TEBEL,
    bidang_isian,
    chip,
    judul_halaman,
    kartu,
    pilihan_isian,
    pita_pemberitahuan,
    tabel_data,
    tag_status,
    tag_zebra,
    tombol_bahaya,
    tombol_primer,
    tombol_sekunder,
)
from controllers.auth_controller import AuthController


class DistribusiView(ctk.CTkFrame):
    """Halaman pengelolaan alokasi distribusi."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=WARNA_LATAR)
        self.controller = controller
        self.selected_id = None
        self.bisa_ubah = AuthController.boleh("bisa_kelola_distribusi")

        # --------------------------------------------------------
        # Kepala halaman
        # --------------------------------------------------------
        judul_halaman(
            self,
            "Alokasi Distribusi Logistik",
            "Alokasi pengiriman hasil panen dari gudang menuju distributor.",
        )

        # Pita peringatan bagi peran tanpa hak kelola.
        if not self.bisa_ubah:
            pita_pemberitahuan(
                self,
                "Peran Anda hanya memiliki akses baca pada modul ini.",
            ).pack(fill="x", padx=32, pady=(0, 8))

        # --------------------------------------------------------
        # Kartu formulir
        # --------------------------------------------------------
        form_card = kartu(self)
        form_card.pack(fill="x", padx=32, pady=(4, 10))

        ctk.CTkLabel(
            form_card,
            text="Formulir Alokasi Pengiriman",
            font=(FONT, TS_SEKSI, "bold"),
            text_color=WARNA_TEBEL,
        ).pack(anchor="w", padx=22, pady=(16, 2))

        isi_form = ctk.CTkFrame(form_card, fg_color="transparent")
        isi_form.pack(fill="x", padx=22)
        for kolom in range(4):
            isi_form.grid_columnconfigure(kolom, weight=1)

        kolom_panen, self.opt_panen = pilihan_isian(isi_form, "Lot Panen", ["- Pilih Lot Panen -"])
        kolom_panen.grid(row=0, column=0, columnspan=2, sticky="ew", padx=(0, 12))

        kolom_tujuan, self.e_tujuan = bidang_isian(
            isi_form, "Tujuan Pengiriman", "Contoh: Pasar Induk Karya"
        )
        kolom_tujuan.grid(row=0, column=2, sticky="ew", padx=12)

        kolom_jumlah, self.e_jumlah = bidang_isian(isi_form, "Jumlah Dikirim (Kg)", "Contoh: 50")
        kolom_jumlah.grid(row=0, column=3, sticky="ew", padx=(12, 0))

        kolom_status, self.opt_status = pilihan_isian(
            isi_form, "Status Pengiriman", list(STATUS_PENGIRIMAN)
        )
        kolom_status.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0), padx=(0, 12))
        self.opt_status.set(STATUS_DIPROSES)

        # --- Baris tombol aksi ---
        btn_row = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=22, pady=(16, 18))

        self.btn_simpan = tombol_primer(btn_row, "Simpan Alokasi", self.simpan, lebar=140)
        self.btn_simpan.pack(side="right")

        self.btn_hapus = tombol_bahaya(btn_row, "Hapus", self.hapus, lebar=110)
        self.btn_hapus.pack(side="right", padx=(0, 10))

        self.btn_ubah = tombol_sekunder(btn_row, "Ubah Status", self.ubah, lebar=120)
        self.btn_ubah.pack(side="right", padx=(0, 10))

        # --------------------------------------------------------
        # Kartu tabel data
        # --------------------------------------------------------
        table_card = kartu(self)
        table_card.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        kepala = ctk.CTkFrame(table_card, fg_color="transparent")
        kepala.pack(fill="x", padx=22, pady=(16, 4))

        ctk.CTkLabel(
            kepala,
            text="Daftar Alokasi Pengiriman",
            font=(FONT, TS_SEKSI, "bold"),
            text_color=WARNA_TEBEL,
        ).pack(side="left")

        self.chip_jumlah = chip(kepala, "0 alokasi", "#f0f5f2", WARNA_REDUP)
        self.chip_jumlah.pack(side="right")

        kolom = (
            ("id", "ID Distribusi", 110, "center"),
            ("id_panen", "ID Panen", 90, "center"),
            ("tujuan", "Tujuan Pengiriman", 300, "w"),
            ("jumlah", "Jumlah Dikirim (Kg)", 165, "center"),
            ("status", "Status Pengiriman", 170, "center"),
        )
        wadah_tabel, self.tree = tabel_data(table_card, kolom, tinggi=12)
        wadah_tabel.pack(fill="both", expand=True, padx=22, pady=(4, 18))

        self.tree.bind("<ButtonRelease-1>", self.on_select)

        # --------------------------------------------------------
        # Inisialisasi
        # --------------------------------------------------------
        self._panen_map = {}
        self._terapkan_otorisasi()
        # Penghapusan data hanya untuk Administrator (matriks RBAC).
        if not AuthController.boleh("bisa_hapus_data"):
            self.btn_hapus.configure(state="disabled")
        self.clear_form()
        self.load_table()
        self.load_panen()

    # ========================================================
    # Otorisasi
    # ========================================================
    def _terapkan_otorisasi(self):
        """Menonaktifkan elemen form bagi pengguna tanpa hak kelola."""
        if self.bisa_ubah:
            return

        state = "disabled"
        self.opt_panen.configure(state=state)
        self.e_tujuan.configure(state=state)
        self.e_jumlah.configure(state=state)
        self.opt_status.configure(state=state)
        self.btn_simpan.configure(state=state)
        self.btn_ubah.configure(state=state)
        self.btn_hapus.configure(state=state)

    # ========================================================
    # Pemuatan data
    # ========================================================
    def refresh_data(self):
        """Menyegarkan tabel dan daftar lot saat halaman dibuka.

        Dipanggil oleh ``AgriUnoApp.show_page`` setiap kali halaman
        ditampilkan sehingga perubahan stok akibat pencatatan panen
        langsung terlihat pada daftar lot. Pilihan lot yang sedang
        dibuka pengguna dipertahankan bila masih tersedia.
        """
        terpilih = self.opt_panen.get()
        self.load_table()
        self.load_panen()
        if terpilih and terpilih in self._panen_map:
            self.opt_panen.set(terpilih)

    def load_panen(self):
        """Mengisi kotak daftar lot panen beserta sisa stoknya."""
        self._panen_map = {}
        label_pilihan = ["- Pilih Lot Panen -"]

        daftar = sorted(self.controller.get_panen(), key=lambda item: int(item.get("id_panen", 0)))
        for item in daftar:
            id_panen = item.get("id_panen")
            jenis = item.get("jenis_komoditas")
            sisa = item.get("sisa_stok")
            label = "#%s - %s (sisa %s Kg)" % (id_panen, jenis, sisa)
            self._panen_map[label] = id_panen
            label_pilihan.append(label)

        self.opt_panen.configure(values=label_pilihan)
        self.opt_panen.set(label_pilihan[0])

    # ------------------------------------------------------------
    def clear_form(self):
        """Mengosongkan form isian dan membatalkan seleksi baris."""
        self.selected_id = None
        self.e_tujuan.delete(0, "end")
        self.e_jumlah.delete(0, "end")
        self.opt_status.set(STATUS_DIPROSES)
        if self.opt_panen.cget("values"):
            self.opt_panen.set(self.opt_panen.cget("values")[0])

    # ------------------------------------------------------------
    def load_table(self):
        """Menyegarkan isi tabel dengan data terbaru."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = self.controller.get_distribusi()
        for indeks, item in enumerate(data):
            status = item.get("status_pengiriman")
            self.tree.insert(
                "",
                "end",
                values=(
                    item.get("id_distribusi"),
                    item.get("id_panen"),
                    item.get("tujuan_pengiriman"),
                    item.get("jumlah_dikirim"),
                    status,
                ),
                tags=(tag_zebra(indeks), tag_status(status)),
            )

        self.chip_jumlah.configure(text="%d alokasi pengiriman" % len(data))

    # ========================================================
    # Aksi form
    # ========================================================
    def _id_panen_terpilih(self):
        """Mengembalikan id lot panen yang dipilih pada kotak daftar."""
        label = self.opt_panen.get()
        return self._panen_map.get(label)

    # ------------------------------------------------------------
    def simpan(self):
        """Membuat alokasi pengiriman baru."""
        id_panen = self._id_panen_terpilih()
        if not id_panen:
            messagebox.showwarning("Peringatan", "Pilih lot panen terlebih dahulu!")
            return

        sukses, pesan = self.controller.tambah_distribusi(
            id_panen, self.e_tujuan.get(), self.e_jumlah.get()
        )
        if sukses:
            messagebox.showinfo("Sukses", pesan)
            self.clear_form()
            self.load_table()
            self.load_panen()
        else:
            messagebox.showerror("Validasi Stok (BR-02)", pesan)

    # ------------------------------------------------------------
    def on_select(self, _event=None):
        """Memuat data baris terpilih ke dalam form."""
        selected_item = self.tree.focus()
        if not selected_item:
            return

        values = self.tree.item(selected_item, "values")
        if not values:
            return

        self.selected_id = values[0]

        # Pilih lot panen yang sesuai pada kotak daftar.
        id_panen = values[1]
        for label, value in self._panen_map.items():
            if str(value) == str(id_panen):
                self.opt_panen.set(label)
                break

        self.e_tujuan.delete(0, "end")
        self.e_tujuan.insert(0, values[2])
        self.e_jumlah.delete(0, "end")
        self.e_jumlah.insert(0, values[3])
        self.opt_status.set(values[4])

    # ------------------------------------------------------------
    def ubah(self):
        """Memperbarui alokasi beserta statusnya."""
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data distribusi yang ingin diubah!")
            return

        id_panen = self._id_panen_terpilih()
        if not id_panen:
            messagebox.showwarning("Peringatan", "Pilih lot panen terlebih dahulu!")
            return

        sukses, pesan = self.controller.update_distribusi(
            self.selected_id,
            id_panen,
            self.e_tujuan.get(),
            self.e_jumlah.get(),
            self.opt_status.get(),
        )
        if sukses:
            messagebox.showinfo("Sukses", pesan)
            self.clear_form()
            self.load_table()
            self.load_panen()
        else:
            messagebox.showerror("Error", pesan)

    # ------------------------------------------------------------
    def hapus(self):
        """Menghapus alokasi distribusi terpilih."""
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data distribusi yang ingin dihapus!")
            return

        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus alokasi distribusi ini?"):
            sukses, pesan = self.controller.hapus_distribusi(self.selected_id)
            if sukses:
                messagebox.showinfo("Sukses", pesan)
                self.clear_form()
                self.load_table()
                self.load_panen()
            else:
                messagebox.showerror("Error", pesan)
