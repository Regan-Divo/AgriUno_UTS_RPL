import customtkinter as ctk
from tkinter import ttk, messagebox
from controllers.controller import AgriUnoController

# Konfigurasi Tema Estetik Profesional
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

class AgriUnoApp(ctk.CTk):
    """
    Kelas Utama Tampilan (View) Aplikasi Desktop AgriUno.
    Menyediakan navigasi tab modern, form input tervalidasi, dan tabel rekapitulasi interaktif.
    """
    def __init__(self):
        super().__init__()
        
        self.title("AgriUno v1.0 - Sistem Informasi Manajemen Rantai Pasok & Inventori Pertanian")
        self.geometry("1150x700")
        self.minsize(1000, 620)
        
        # --- HEADER UTAMA ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=15)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🌾 AGRIUNO ENTERPRISE DASHBOARD", 
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="Modul Operasional Gudang: Petani, Inventori & Logistik", 
            font=("Segoe UI", 13), text_color="#666666"
        )
        subtitle_label.pack(side="right", pady=5)

        # --- TAB VIEW UTAMA (Navigasi Modul) ---
        self.tab_view = ctk.CTkTabview(self, width=1100, height=580)
        self.tab_view.pack(padx=25, pady=5, fill="both", expand=True)
        
        # Inisialisasi Tab Modul
        self.tab_petani = self.tab_view.add("Manajemen Petani")
        self.tab_inventori = self.tab_view.add("Inventori Panen Gudang")
        self.tab_distribusi = self.tab_view.add("Distribusi & Logistik")
        
        self.setup_tab_petani()
        self.setup_tab_inventori()
        self.setup_tab_distribusi()

    # ==================== MODUL TAB 1: PETANI ====================
    def setup_tab_petani(self):
        form_frame = ctk.CTkFrame(self.tab_petani, width=300)
        form_frame.pack(side="left", fill="y", padx=15, pady=15, ipadx=10)
        
        ctk.CTkLabel(form_frame, text="Form Data Petani", font=("Segoe UI", 16, "bold")).pack(pady=15)
        
        self.e_nama = ctk.CTkEntry(form_frame, placeholder_text="Nama Lengkap Petani", width=260, height=38)
        self.e_nama.pack(pady=10, padx=10)
        
        self.e_lokasi = ctk.CTkEntry(form_frame, placeholder_text="Lokasi / Wilayah Lahan", width=260, height=38)
        self.e_lokasi.pack(pady=10, padx=10)
        
        self.e_komoditas = ctk.CTkEntry(form_frame, placeholder_text="Komoditas Utama", width=260, height=38)
        self.e_komoditas.pack(pady=10, padx=10)
        
        btn_simpan = ctk.CTkButton(
            form_frame, text="Simpan Data Petani", fg_color="#2D5A27", hover_color="#1E3D1A",
            height=40, font=("Segoe UI", 13, "bold"), command=self.aksi_simpan_petani
        )
        btn_simpan.pack(pady=20, padx=10, fill="x")

        # Tabel Tampilan Data
        table_frame = ctk.CTkFrame(self.tab_petani)
        table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)
        
        columns = ("ID", "Nama Petani", "Lokasi Lahan", "Komoditas Utama")
        self.tree_petani = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.tree_petani.heading(col, text=col)
            self.tree_petani.column(col, width=170, anchor="center")
            
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_petani.yview)
        self.tree_petani.configure(yscrollcommand=scrollbar.set)
        
        self.tree_petani.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.muat_tabel_petani()

    def muat_tabel_petani(self):
        for row in self.tree_petani.get_children():
            self.tree_petani.delete(row)
        for data in AgriUnoController.ambil_semua_petani():
            self.tree_petani.insert("", "end", values=(
                data['id_petani'], data['nama_petani'], data['lokasi_lahan'], data['komoditas_utama']
            ))

    def aksi_simpan_petani(self):
        sukses, pesan = AgriUnoController.simpan_petani(
            self.e_nama.get(), self.e_lokasi.get(), self.e_komoditas.get()
        )
        if sukses:
            messagebox.showinfo("Informasi Sukses", pesan)
            self.e_nama.delete(0, 'end')
            self.e_lokasi.delete(0, 'end')
            self.e_komoditas.delete(0, 'end')
            self.muat_tabel_petani()
        else:
            messagebox.showerror("Kesalahan Validasi", pesan)

    # ==================== MODUL TAB 2: INVENTORI PANEN ====================
    def setup_tab_inventori(self):
        form_frame = ctk.CTkFrame(self.tab_inventori, width=300)
        form_frame.pack(side="left", fill="y", padx=15, pady=15, ipadx=10)
        
        ctk.CTkLabel(form_frame, text="Pencatatan Panen Masuk", font=("Segoe UI", 16, "bold")).pack(pady=15)
        
        self.e_id_petani = ctk.CTkEntry(form_frame, placeholder_text="ID Petani Penyetor", width=260, height=38)
        self.e_id_petani.pack(pady=10, padx=10)
        
        self.e_jenis_kom = ctk.CTkEntry(form_frame, placeholder_text="Jenis Komoditas", width=260, height=38)
        self.e_jenis_kom.pack(pady=10, padx=10)
        
        self.e_berat = ctk.CTkEntry(form_frame, placeholder_text="Jumlah Berat (Kg)", width=260, height=38)
        self.e_berat.pack(pady=10, padx=10)
        
        self.e_tanggal = ctk.CTkEntry(form_frame, placeholder_text="Tanggal (YYYY-MM-DD)", width=260, height=38)
        self.e_tanggal.pack(pady=10, padx=10)
        
        btn_simpan_inv = ctk.CTkButton(
            form_frame, text="Catat Setoran Panen", fg_color="#2D5A27", hover_color="#1E3D1A",
            height=40, font=("Segoe UI", 13, "bold"), command=self.aksi_simpan_inventori
        )
        btn_simpan_inv.pack(pady=20, padx=10, fill="x")

        # Tabel Inventori
        table_frame = ctk.CTkFrame(self.tab_inventori)
        table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)
        
        columns = ("ID Panen", "Nama Petani", "Komoditas", "Sisa Berat (Kg)", "Tanggal Panen")
        self.tree_inv = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.tree_inv.heading(col, text=col)
            self.tree_inv.column(col, width=150, anchor="center")
            
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_inv.yview)
        self.tree_inv.configure(yscrollcommand=scrollbar.set)
        
        self.tree_inv.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.muat_tabel_inventori()

    def muat_tabel_inventori(self):
        for row in self.tree_inv.get_children():
            self.tree_inv.delete(row)
        for data in AgriUnoController.ambil_semua_inventori():
            self.tree_inv.insert("", "end", values=(
                data['id_panen'], data['nama_petani'], data['jenis_komoditas'], data['jumlah_berat'], data['tgl_panen']
            ))

    def aksi_simpan_inventori(self):
        sukses, pesan = AgriUnoController.catat_setoran_panen(
            self.e_id_petani.get(), self.e_jenis_kom.get(), self.e_berat.get(), self.e_tanggal.get()
        )
        if sukses:
            messagebox.showinfo("Informasi Sukses", pesan)
            self.muat_tabel_inventori()
        else:
            messagebox.showerror("Kesalahan Validasi", pesan)

    # ==================== MODUL TAB 3: DISTRIBUSI ====================
    def setup_tab_distribusi(self):
        form_frame = ctk.CTkFrame(self.tab_distribusi, width=300)
        form_frame.pack(side="left", fill="y", padx=15, pady=15, ipadx=10)
        
        ctk.CTkLabel(form_frame, text="Alokasi Pengiriman Logistik", font=("Segoe UI", 16, "bold")).pack(pady=15)
        
        self.e_id_panen_dis = ctk.CTkEntry(form_frame, placeholder_text="ID Panen Asal", width=260, height=38)
        self.e_id_panen_dis.pack(pady=10, padx=10)
        
        self.e_tujuan = ctk.CTkEntry(form_frame, placeholder_text="Tujuan Pengiriman / Toko", width=260, height=38)
        self.e_tujuan.pack(pady=10, padx=10)
        
        self.e_jml_kirim = ctk.CTkEntry(form_frame, placeholder_text="Jumlah Kirim (Kg)", width=260, height=38)
        self.e_jml_kirim.pack(pady=10, padx=10)
        
        self.e_status = ctk.CTkEntry(form_frame, placeholder_text="Status (Diproses/Terkirim)", width=260, height=38)
        self.e_status.pack(pady=10, padx=10)
        
        btn_alokasi = ctk.CTkButton(
            form_frame, text="Proses Alokasi & Kirim", fg_color="#2D5A27", hover_color="#1E3D1A",
            height=40, font=("Segoe UI", 13, "bold"), command=self.aksi_alokasi_distribusi
        )
        btn_alokasi.pack(pady=20, padx=10, fill="x")

        # Tabel Distribusi
        table_frame = ctk.CTkFrame(self.tab_distribusi)
        table_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)
        
        columns = ("ID Distribusi", "ID Panen", "Tujuan Pengiriman", "Jumlah Kirim", "Status")
        self.tree_dis = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.tree_dis.heading(col, text=col)
            self.tree_dis.column(col, width=150, anchor="center")
            
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_dis.yview)
        self.tree_dis.configure(yscrollcommand=scrollbar.set)
        
        self.tree_dis.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.muat_tabel_distribusi()

    def muat_tabel_distribusi(self):
        for row in self.tree_dis.get_children():
            self.tree_dis.delete(row)
        for data in AgriUnoController.ambil_semua_distribusi():
            self.tree_dis.insert("", "end", values=(
                data['id_distribusi'], data['id_panen'], data['tujuan_pengiriman'], data['jumlah_dikirim'], data['status_pengiriman']
            ))

    def aksi_alokasi_distribusi(self):
        sukses, pesan = AgriUnoController.alokasikan_pengiriman(
            self.e_id_panen_dis.get(), self.e_tujuan.get(), self.e_jml_kirim.get(), self.e_status.get()
        )
        if sukses:
            messagebox.showinfo("Informasi Sukses", pesan)
            self.muat_tabel_distribusi()
            self.muat_tabel_inventori()  # Refresh stok inventori secara otomatis
        else:
            messagebox.showerror("Gagal Alokasi Distribusi", pesan)

if __name__ == "__main__":
    app = AgriUnoApp()
    app.mainloop()