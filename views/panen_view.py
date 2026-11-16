"""
==========================================================
HALAMAN INVENTORI PANEN - AGRIUNO
==========================================================
Menyediakan form isian dan tabel data untuk mencatat lot setoran
hasil panen yang masuk ke gudang.

Tampilan dibangun dari kit antarmuka bersama (``config/ui_kit``):
kartu bersudut membulat, label di atas isian, tabel dengan baris
selang-seling, serta hierarki tombol yang konsisten.

Peningkatan terhadap versi UTS:

1. **Pemilihan penyetor memakai kotak daftar (dropdown)** yang
   diisi otomatis dari tabel ``petani``. Pada versi UTS pengguna
   harus mengetik ID Petani secara manual sehingga rawan salah
   input dan referensi ke data yang tidak terdaftar.
2. **Kolom Sisa Stok** ditampilkan pada tabel. Nilai ini dihitung
   otomatis dari berat awal lot dikurangi total berat yang sudah
   dialokasikan ke distributor (BR-02).
3. **Otorisasi berbasis peran** menonaktifkan modul bagi pengguna
   yang hanya memiliki akses baca.
"""

from datetime import datetime
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
    pilihan_isian,
    pita_pemberitahuan,
    tabel_data,
    tag_zebra,
    tombol_bahaya,
    tombol_primer,
    tombol_sekunder,
)
from controllers.auth_controller import AuthController


class PanenView(ctk.CTkFrame):
    """Halaman pencatatan lot setoran panen."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=WARNA_LATAR)
        self.controller = controller
        self.selected_id = None
        self.bisa_ubah = AuthController.boleh("bisa_kelola_panen")

        # --------------------------------------------------------
        # Kepala halaman
        # --------------------------------------------------------
        judul_halaman(
            self,
            "Inventori Hasil Panen",
            "Pencatatan lot setoran panen yang masuk ke gudang beserta sisa stoknya.",
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
            text="Formulir Lot Setoran Panen",
            font=(FONT, TS_SEKSI, "bold"),
            text_color=WARNA_TEBEL,
        ).pack(anchor="w", padx=22, pady=(16, 2))

        isi_form = ctk.CTkFrame(form_card, fg_color="transparent")
        isi_form.pack(fill="x", padx=22)
        for kolom in range(4):
            isi_form.grid_columnconfigure(kolom, weight=1)

        kolom_petani, self.opt_petani = pilihan_isian(
            isi_form, "Petani Penyetor", ["- Pilih Petani -"]
        )
        kolom_petani.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.opt_petani.configure(command=self._saat_pilih_petani)

        kolom_komo, self.e_komoditas = bidang_isian(
            isi_form, "Jenis Komoditas", "Contoh: Beras Organik"
        )
        kolom_komo.grid(row=0, column=1, sticky="ew", padx=12)

        kolom_berat, self.e_berat = bidang_isian(isi_form, "Jumlah Berat (Kg)", "Contoh: 120")
        kolom_berat.grid(row=0, column=2, sticky="ew", padx=12)

        kolom_tgl, self.e_tgl = bidang_isian(isi_form, "Tanggal Panen", "YYYY-MM-DD", wajib=False)
        kolom_tgl.grid(row=0, column=3, sticky="ew", padx=(12, 0))

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
            text="Daftar Lot Setoran Panen",
            font=(FONT, TS_SEKSI, "bold"),
            text_color=WARNA_TEBEL,
        ).pack(side="left")

        self.chip_jumlah = chip(kepala, "0 lot", "#f0f5f2", WARNA_REDUP)
        self.chip_jumlah.pack(side="right")

        kolom = (
            ("id", "ID Panen", 90, "center"),
            ("id_p", "ID Petani", 90, "center"),
            ("komoditas", "Jenis Komoditas", 300, "w"),
            ("berat", "Berat Setoran (Kg)", 150, "center"),
            ("sisa", "Sisa Stok (Kg)", 150, "center"),
            ("tgl", "Tanggal Panen", 130, "center"),
        )
        wadah_tabel, self.tree = tabel_data(table_card, kolom, tinggi=12)
        wadah_tabel.pack(fill="both", expand=True, padx=22, pady=(4, 18))

        self.tree.bind("<ButtonRelease-1>", self.on_select)

        # --------------------------------------------------------
        # Inisialisasi
        # --------------------------------------------------------
        self._petani_map = {}
        self._petani_komo = {}
        self._terapkan_otorisasi()
        # Penghapusan data hanya untuk Administrator (matriks RBAC).
        if not AuthController.boleh("bisa_hapus_data"):
            self.btn_hapus.configure(state="disabled")
        self.reset_form()
        self.load_table()
        self.load_petani()

    # ========================================================
    # Otorisasi
    # ========================================================
    def _terapkan_otorisasi(self):
        """Menonaktifkan elemen form bagi pengguna tanpa hak kelola."""
        if self.bisa_ubah:
            return

        state = "disabled"
        self.opt_petani.configure(state=state)
        self.e_komoditas.configure(state=state)
        self.e_berat.configure(state=state)
        self.e_tgl.configure(state=state)
        self.btn_simpan.configure(state=state)
        self.btn_ubah.configure(state=state)
        self.btn_hapus.configure(state=state)

    # ========================================================
    # Pemuatan data
    # ========================================================
    def refresh_data(self):
        """Menyegarkan tabel dan daftar penyetor saat halaman dibuka.

        Dipanggil oleh ``AgriUnoApp.show_page`` setiap kali pengguna
        berpindah ke halaman ini sehingga petani yang baru ditambahkan
        pada halaman Kelola Petani langsung muncul pada daftar. Pilihan
        yang sedang dibuka pengguna dipertahankan bila masih tersedia.
        """
        terpilih = self.opt_petani.get()
        self.load_table()
        self.load_petani()
        if terpilih and terpilih in self._petani_map:
            self.opt_petani.set(terpilih)

    def load_petani(self):
        """Mengisi kotak daftar penyetor dari data petani."""
        self._petani_map = {}
        self._petani_komo = {}
        label_pilihan = ["- Pilih Petani -"]

        daftar = sorted(self.controller.get_petani(), key=lambda item: int(item["id_petani"]))
        for item in daftar:
            id_petani = item["id_petani"]
            nama = item["nama_petani"]
            label = "%s - %s" % (id_petani, nama)
            self._petani_map[label] = id_petani
            self._petani_komo[label] = item.get("komoditas_utama", "")
            label_pilihan.append(label)

        self.opt_petani.configure(values=label_pilihan)
        self.opt_petani.set(label_pilihan[0])

    # ------------------------------------------------------------
    def reset_form(self):
        """Mengosongkan form dan mengisi tanggal hari ini."""
        self.selected_id = None
        self.e_komoditas.delete(0, "end")
        self.e_berat.delete(0, "end")
        self.e_tgl.delete(0, "end")
        self.e_tgl.insert(0, datetime.now().strftime("%Y-%m-%d"))
        if self.opt_petani.cget("values"):
            self.opt_petani.set(self.opt_petani.cget("values")[0])

    # ------------------------------------------------------------
    def load_table(self):
        """Menyegarkan isi tabel dengan data terbaru."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = self.controller.get_panen()
        for indeks, item in enumerate(data):
            self.tree.insert(
                "",
                "end",
                values=(
                    item.get("id_panen"),
                    item.get("id_petani"),
                    item.get("jenis_komoditas"),
                    item.get("jumlah_berat"),
                    item.get("sisa_stok"),
                    item.get("tgl_panen"),
                ),
                tags=(tag_zebra(indeks),),
            )

        self.chip_jumlah.configure(text="%d lot panen" % len(data))

    # ========================================================
    # Aksi form
    # ========================================================
    def _saat_pilih_petani(self, _pilihan=None):
        """Mengisi jenis komoditas otomatis dari master data petani.

        Sesuai alur bisnis, jenis komoditas pada lot setoran mengacu
        pada komoditas utama petani yang tercatat di halaman Kelola
        Petani sehingga pengguna tidak perlu mengetik ulang dan data
        tidak menyimpang dari master data.
        """
        komoditas = self._petani_komo.get(self.opt_petani.get())
        if komoditas:
            self.e_komoditas.delete(0, "end")
            self.e_komoditas.insert(0, komoditas)

    def _id_petani_terpilih(self):
        """Mengembalikan id petani yang dipilih pada kotak daftar."""
        label = self.opt_petani.get()
        return self._petani_map.get(label)

    # ------------------------------------------------------------
    def simpan(self):
        """Mencatat lot setoran panen baru."""
        id_petani = self._id_petani_terpilih()
        if not id_petani:
            messagebox.showwarning("Peringatan", "Pilih petani penyetor terlebih dahulu!")
            return

        sukses, pesan = self.controller.tambah_panen(
            id_petani,
            self.e_komoditas.get(),
            self.e_berat.get(),
            self.e_tgl.get(),
        )
        if sukses:
            messagebox.showinfo("Sukses", pesan)
            self.reset_form()
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

        # Pilih penyetor yang sesuai pada kotak daftar.
        id_petani = values[1]
        for label, value in self._petani_map.items():
            if str(value) == str(id_petani):
                self.opt_petani.set(label)
                break

        self.e_komoditas.delete(0, "end")
        self.e_komoditas.insert(0, values[2])
        self.e_berat.delete(0, "end")
        self.e_berat.insert(0, values[3])
        self.e_tgl.delete(0, "end")
        self.e_tgl.insert(0, str(values[5]))

    # ------------------------------------------------------------
    def ubah(self):
        """Memperbarui lot panen terpilih."""
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data panen pada tabel yang ingin diubah!")
            return

        id_petani = self._id_petani_terpilih()
        if not id_petani:
            messagebox.showwarning("Peringatan", "Pilih petani penyetor terlebih dahulu!")
            return

        sukses, pesan = self.controller.update_panen(
            self.selected_id,
            id_petani,
            self.e_komoditas.get(),
            self.e_berat.get(),
            self.e_tgl.get(),
        )
        if sukses:
            messagebox.showinfo("Sukses", pesan)
            self.reset_form()
            self.load_table()
        else:
            messagebox.showerror("Error", pesan)

    # ------------------------------------------------------------
    def hapus(self):
        """Menghapus lot panen terpilih."""
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data panen pada tabel yang ingin dihapus!")
            return

        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data panen ini?"):
            sukses, pesan = self.controller.hapus_panen(self.selected_id)
            if sukses:
                messagebox.showinfo("Sukses", pesan)
                self.reset_form()
                self.load_table()
            else:
                messagebox.showerror("Gagal", pesan)
