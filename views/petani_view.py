"""
=========================================================
HALAMAN KELOLA PETANI - AGRIUNO
=========================================================
Menyediakan form isian dan tabel data untuk mengelola identitas
petani penyetor hasil panen.

Tampilan dibangun dari kit antarmuka bersama (``config/ui_kit``):
kartu bersudut membulat, label di atas isian, tabel dengan baris
selang-seling, serta hierarki tombol yang konsisten.

Otorisasi (RBAC): halaman ini merupakan modul pengelolaan data.
Apabila pengguna yang sedang login hanya memiliki peran read-only
(misalnya peran ``petani``), seluruh kolom isian dan tombol aksi
dinonaktifkan sehingga antarmuka hanya berfungsi sebagai tampilan
data.
"""

from tkinter import messagebox

import customtkinter as ctk

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
    pita_pemberitahuan,
    tabel_data,
    tag_zebra,
    tombol_bahaya,
    tombol_primer,
    tombol_sekunder,
)
from controllers.auth_controller import AuthController


class PetaniView(ctk.CTkFrame):
    """Halaman pengelolaan data petani."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=WARNA_LATAR)
        self.controller = controller
        self.selected_id = None
        self.bisa_ubah = AuthController.boleh("bisa_kelola_petani")

        # --------------------------------------------------------
        # Kepala halaman
        # --------------------------------------------------------
        judul_halaman(
            self,
            "Kelola Data Petani",
            "Master data penyetor hasil panen yang tercatat pada gudang.",
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
            text="Formulir Data Petani",
            font=(FONT, TS_SEKSI, "bold"),
            text_color=WARNA_TEBEL,
        ).pack(anchor="w", padx=22, pady=(16, 2))

        isi_form = ctk.CTkFrame(form_card, fg_color="transparent")
        isi_form.pack(fill="x", padx=22)
        isi_form.grid_columnconfigure(0, weight=1)
        isi_form.grid_columnconfigure(1, weight=1)
        isi_form.grid_columnconfigure(2, weight=1)

        kolom_nama, self.e_nama = bidang_isian(isi_form, "Nama Petani", "Contoh: Siti Halmah")
        kolom_nama.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        kolom_lokasi, self.e_lokasi = bidang_isian(
            isi_form, "Lokasi Lahan", "Contoh: Desa Wonosari, Kec. Poncowati", wajib=False
        )
        kolom_lokasi.grid(row=0, column=1, sticky="ew", padx=12)

        kolom_komo, self.e_komoditas = bidang_isian(
            isi_form, "Komoditas Utama", "Contoh: Beras Organik", wajib=False
        )
        kolom_komo.grid(row=0, column=2, sticky="ew", padx=(12, 0))

        # --- Baris tombol aksi ---
        btn_row = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=22, pady=(16, 18))

        self.btn_simpan = tombol_primer(btn_row, "Simpan Data", self.simpan, lebar=132)
        self.btn_simpan.pack(side="right")

        self.btn_hapus = tombol_bahaya(btn_row, "Hapus", self.hapus, lebar=110)
        self.btn_hapus.pack(side="right", padx=(0, 10))

        self.btn_ubah = tombol_sekunder(btn_row, "Ubah", self.ubah, lebar=110)
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
            text="Daftar Petani Terdaftar",
            font=(FONT, TS_SEKSI, "bold"),
            text_color=WARNA_TEBEL,
        ).pack(side="left")

        self.chip_jumlah = chip(kepala, "0 petani", "#f0f5f2", WARNA_REDUP)
        self.chip_jumlah.pack(side="right")

        kolom = (
            ("id", "ID", 70, "center"),
            ("nama", "Nama Petani", 260, "w"),
            ("lokasi", "Lokasi Lahan", 320, "w"),
            ("komoditas", "Komoditas Utama", 240, "w"),
        )
        wadah_tabel, self.tree = tabel_data(table_card, kolom, tinggi=12)
        wadah_tabel.pack(fill="both", expand=True, padx=22, pady=(4, 18))

        self.tree.bind("<ButtonRelease-1>", self.on_select)

        # --------------------------------------------------------
        # Terapkan batasan hak akses
        # --------------------------------------------------------
        self._terapkan_otorisasi()
        # Penghapusan data hanya untuk Administrator (matriks RBAC).
        if not AuthController.boleh("bisa_hapus_data"):
            self.btn_hapus.configure(state="disabled")
        self.load_table()

    # ========================================================
    # Otorisasi
    # ========================================================
    def _terapkan_otorisasi(self):
        """Menonaktifkan elemen form ketika pengguna tidak berhak mengelola."""
        if self.bisa_ubah:
            return

        state = "disabled"
        self.e_nama.configure(state=state)
        self.e_lokasi.configure(state=state)
        self.e_komoditas.configure(state=state)
        self.btn_simpan.configure(state=state)
        self.btn_ubah.configure(state=state)
        self.btn_hapus.configure(state=state)

    # ========================================================
    # Pemuatan data
    # ========================================================
    def refresh_data(self):
        """Menyegarkan isi tabel saat halaman ditampilkan kembali."""
        self.load_table()

    def load_table(self):
        """Menyegarkan isi tabel dengan data terbaru."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = self.controller.get_petani()
        for indeks, item in enumerate(data):
            self.tree.insert(
                "",
                "end",
                values=(
                    item["id_petani"],
                    item["nama_petani"],
                    item["lokasi_lahan"],
                    item["komoditas_utama"],
                ),
                tags=(tag_zebra(indeks),),
            )

        self.chip_jumlah.configure(text="%d petani terdaftar" % len(data))

    # ========================================================
    # Aksi form
    # ========================================================
    def clear_form(self):
        """Mengosongkan form isian dan membatalkan seleksi baris."""
        self.selected_id = None
        self.e_nama.delete(0, "end")
        self.e_lokasi.delete(0, "end")
        self.e_komoditas.delete(0, "end")

    # ------------------------------------------------------------
    def simpan(self):
        """Menyimpan data petani baru."""
        sukses, pesan = self.controller.tambah_petani(
            self.e_nama.get(), self.e_lokasi.get(), self.e_komoditas.get()
        )
        if sukses:
            messagebox.showinfo("Sukses", pesan)
            self.clear_form()
            self.load_table()
        else:
            messagebox.showerror("Error", pesan)

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
        self.e_nama.delete(0, "end")
        self.e_nama.insert(0, values[1])
        self.e_lokasi.delete(0, "end")
        self.e_lokasi.insert(0, values[2])
        self.e_komoditas.delete(0, "end")
        self.e_komoditas.insert(0, values[3])

    # ------------------------------------------------------------
    def ubah(self):
        """Memperbarui data petani terpilih."""
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data petani pada tabel yang ingin diubah!")
            return

        sukses, pesan = self.controller.update_petani(
            self.selected_id,
            self.e_nama.get(),
            self.e_lokasi.get(),
            self.e_komoditas.get(),
        )
        if sukses:
            messagebox.showinfo("Sukses", pesan)
            self.clear_form()
            self.load_table()
        else:
            messagebox.showerror("Error", pesan)

    # ------------------------------------------------------------
    def hapus(self):
        """Menghapus data petani terpilih."""
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data petani pada tabel yang ingin dihapus!")
            return

        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data ini?"):
            sukses, pesan = self.controller.hapus_petani(self.selected_id)
            if sukses:
                messagebox.showinfo("Sukses", pesan)
                self.clear_form()
                self.load_table()
            else:
                messagebox.showerror("Gagal Menghapus", pesan)
