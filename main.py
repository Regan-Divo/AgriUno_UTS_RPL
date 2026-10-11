import customtkinter as ctk
from tkinter import ttk, messagebox
from controllers.controller import PetaniController, InventoriController, DistribusiController

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

class AgriUnoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AgriUno - Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar Navigasi
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1a4d2e")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="AgriUno", font=ctk.CTkFont(size=26, weight="bold"), text_color="white")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", fg_color="transparent", text_color="white", anchor="w", font=ctk.CTkFont(size=15), command=lambda: self.show_frame("Dashboard"))
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_petani = ctk.CTkButton(self.sidebar_frame, text="Kelola Petani", fg_color="transparent", text_color="white", anchor="w", font=ctk.CTkFont(size=15), command=lambda: self.show_frame("Petani"))
        self.btn_petani.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_panen = ctk.CTkButton(self.sidebar_frame, text="Inventori Panen", fg_color="transparent", text_color="white", anchor="w", font=ctk.CTkFont(size=15), command=lambda: self.show_frame("Panen"))
        self.btn_panen.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_distribusi = ctk.CTkButton(self.sidebar_frame, text="Distribusi", fg_color="transparent", text_color="white", anchor="w", font=ctk.CTkFont(size=15), command=lambda: self.show_frame("Distribusi"))
        self.btn_distribusi.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # Container Utama
        self.container = ctk.CTkFrame(self, fg_color="#f5f7f8", corner_radius=0)
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (DashboardView, PetaniView, PanenView, DistribusiView):
            page_name = F.__name__.replace("View", "")
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Dashboard")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, "load_data"):
            frame.load_data()


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f7f8")
        self.controller = controller

        title = ctk.CTkLabel(self, text="Dashboard Ringkasan Sistem Operasional", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1a4d2e")
        title.pack(anchor="w", padx=30, pady=(30, 20))

        card_frame = ctk.CTkFrame(self, fg_color="transparent")
        card_frame.pack(fill="x", padx=30, pady=10)

        self.lbl_total_petani = self.create_card(card_frame, "Total Petani", "0", 0, "#2b6cb0")
        self.lbl_total_panen = self.create_card(card_frame, "Total Lot Panen", "0", 1, "#d69e2e")
        self.lbl_total_distribusi = self.create_card(card_frame, "Total Distribusi", "0", 2, "#2f855a")

        info_box = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        info_box.pack(fill="both", expand=True, padx=30, pady=20)

        info_title = ctk.CTkLabel(info_box, text="Selamat Datang di Sistem AgriUno", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1a4d2e")
        info_title.pack(anchor="w", padx=20, pady=(20, 10))

        desc = (
            "AgriUno adalah Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal terpadu.\n"
            "Sistem ini dirancang dengan dukungan CRUD penuh untuk memudahkan pencatatan data petani, pemantauan lot hasil panen "
            "berdasarkan tanggal, serta manajemen alokasi distribusi komoditas ke berbagai wilayah dengan validasi stok otomatis.\n\n"
            "• Gunakan menu di sebelah kiri untuk mengelola data petani, mencatat hasil panen masuk, dan memproses distribusi."
        )
        lbl_desc = ctk.CTkLabel(info_box, text=desc, font=ctk.CTkFont(size=15), justify="left", text_color="#333333", wraplength=1050)
        lbl_desc.pack(anchor="w", padx=20, pady=10)

    def create_card(self, parent, title, value, col, accent_color):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, width=320, height=130, border_width=2, border_color="#e2e8f0")
        card.grid(row=0, column=col, padx=(0, 20), sticky="ew")
        card.grid_propagate(False)

        accent_bar = ctk.CTkFrame(card, fg_color=accent_color, height=6, corner_radius=3)
        accent_bar.pack(fill="x", padx=0, pady=(0, 10))

        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="#666666")
        lbl_title.pack(anchor="w", padx=20, pady=(5, 2))

        lbl_val = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=accent_color)
        lbl_val.pack(anchor="w", padx=20, pady=(0, 10))
        return lbl_val

    def load_data(self):
        petani = PetaniController.get_petani()
        panen = InventoriController.get_panen()
        dist = DistribusiController.get_distribusi()
        self.lbl_total_petani.configure(text=str(len(petani)))
        self.lbl_total_panen.configure(text=str(len(panen)))
        self.lbl_total_distribusi.configure(text=str(len(dist)))


class PetaniView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f7f8")
        self.controller = controller
        self.selected_id = None

        title = ctk.CTkLabel(self, text="Manajemen Data Petani", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1a4d2e")
        title.pack(anchor="w", padx=30, pady=(30, 15))

        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        form_frame.pack(fill="x", padx=30, pady=10)

        lbl_nama = ctk.CTkLabel(form_frame, text="Nama Petani:", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_nama.grid(row=0, column=0, padx=25, pady=20, sticky="w")
        self.entry_nama = ctk.CTkEntry(form_frame, width=220, height=35, font=ctk.CTkFont(size=14))
        self.entry_nama.grid(row=0, column=1, padx=10, pady=20, sticky="w")

        lbl_lokasi = ctk.CTkLabel(form_frame, text="Lokasi Lahan:", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_lokasi.grid(row=0, column=2, padx=25, pady=20, sticky="w")
        self.entry_lokasi = ctk.CTkEntry(form_frame, width=220, height=35, font=ctk.CTkFont(size=14))
        self.entry_lokasi.grid(row=0, column=3, padx=10, pady=20, sticky="w")

        lbl_komoditas = ctk.CTkLabel(form_frame, text="Komoditas Utama:", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_komoditas.grid(row=1, column=0, padx=25, pady=(0, 20), sticky="w")
        self.entry_komoditas = ctk.CTkEntry(form_frame, width=220, height=35, font=ctk.CTkFont(size=14))
        self.entry_komoditas.grid(row=1, column=1, padx=10, pady=(0, 20), sticky="w")

        btn_action_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_action_frame.grid(row=1, column=2, columnspan=2, padx=10, pady=(0, 20), sticky="e")

        btn_simpan = ctk.CTkButton(btn_action_frame, text="Simpan", fg_color="#1a4d2e", hover_color="#143b23", width=90, height=38, font=ctk.CTkFont(size=14, weight="bold"), command=self.simpan_petani)
        btn_simpan.pack(side="left", padx=5)

        btn_ubah = ctk.CTkButton(btn_action_frame, text="Ubah", fg_color="#d69e2e", hover_color="#b7791f", width=90, height=38, font=ctk.CTkFont(size=14, weight="bold"), command=self.ubah_petani)
        btn_ubah.pack(side="left", padx=5)

        btn_hapus = ctk.CTkButton(btn_action_frame, text="Hapus", fg_color="#c53030", hover_color="#9b2c2c", width=90, height=38, font=ctk.CTkFont(size=14, weight="bold"), command=self.hapus_petani)
        btn_hapus.pack(side="left", padx=5)

        table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=30, pady=15)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"), background="#1a4d2e", foreground="white", relief="flat")
        style.configure("Treeview", font=("Arial", 13), rowheight=30, fieldbackground="white")
        style.map("Treeview", background=[('selected', '#2f855a')], foreground=[('selected', 'white')])

        columns = ("id", "nama", "lokasi", "komoditas")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        self.tree.heading("id", text="ID Petani")
        self.tree.heading("nama", text="Nama Petani")
        self.tree.heading("lokasi", text="Lokasi Lahan")
        self.tree.heading("komoditas", text="Komoditas Utama")

        self.tree.column("id", width=100, anchor="center")
        self.tree.column("nama", width=250, anchor="w")
        self.tree.column("lokasi", width=250, anchor="w")
        self.tree.column("komoditas", width=250, anchor="w")

        self.tree.tag_configure("evenrow", background="#ffffff")
        self.tree.tag_configure("oddrow", background="#f8fafc")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        scrollbar.pack(side="right", fill="y", pady=15)

    def on_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item[0], 'values')
            self.selected_id = values[0]
            self.entry_nama.delete(0, 'end')
            self.entry_nama.insert(0, values[1])
            self.entry_lokasi.delete(0, 'end')
            self.entry_lokasi.insert(0, values[2])
            self.entry_komoditas.delete(0, 'end')
            self.entry_komoditas.insert(0, values[3])

    def clear_form(self):
        self.selected_id = None
        self.entry_nama.delete(0, 'end')
        self.entry_lokasi.delete(0, 'end')
        self.entry_komoditas.delete(0, 'end')

    def simpan_petani(self):
        success, msg = PetaniController.tambah_petani(self.entry_nama.get(), self.entry_lokasi.get(), self.entry_komoditas.get())
        if success:
            messagebox.showinfo("Sukses", msg)
            self.clear_form()
            self.load_data()
        else:
            messagebox.showerror("Validasi Gagal", msg)

    def ubah_petani(self):
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data petani dari tabel yang ingin diubah terlebih dahulu!")
            return
        success, msg = PetaniController.update_petani(self.selected_id, self.entry_nama.get(), self.entry_lokasi.get(), self.entry_komoditas.get())
        if success:
            messagebox.showinfo("Sukses", msg)
            self.clear_form()
            self.load_data()
        else:
            messagebox.showerror("Validasi Gagal", msg)

    def hapus_petani(self):
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data petani dari tabel yang ingin dihapus terlebih dahulu!")
            return
        if messagebox.askyesno("Konfirmasi Hapus", f"Apakah Anda yakin ingin menghapus data petani ID {self.selected_id}?"):
            success, msg = PetaniController.delete_petani(self.selected_id)
            if success:
                messagebox.showinfo("Sukses", msg)
                self.clear_form()
                self.load_data()
            else:
                messagebox.showerror("Gagal Hapus", msg)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for idx, item in enumerate(PetaniController.get_petani()):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(item['id_petani'], item['nama_petani'], item['lokasi_lahan'], item['komoditas_utama']), tags=(tag,))


class PanenView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f7f8")
        self.controller = controller
        self.selected_id = None

        title = ctk.CTkLabel(self, text="Pencatatan Inventori Panen Masuk", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1a4d2e")
        title.pack(anchor="w", padx=30, pady=(30, 15))

        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        form_frame.pack(fill="x", padx=30, pady=10)

        lbl_id = ctk.CTkLabel(form_frame, text="ID Petani:", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_id.grid(row=0, column=0, padx=25, pady=20, sticky="w")
        self.entry_id_petani = ctk.CTkEntry(form_frame, width=220, height=35, font=ctk.CTkFont(size=14))
        self.entry_id_petani.grid(row=0, column=1, padx=10, pady=20, sticky="w")

        lbl_komoditas = ctk.CTkLabel(form_frame, text="Jenis Komoditas:", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_komoditas.grid(row=0, column=2, padx=25, pady=20, sticky="w")
        self.entry_komoditas = ctk.CTkEntry(form_frame, width=220, height=35, font=ctk.CTkFont(size=14))
        self.entry_komoditas.grid(row=0, column=3, padx=10, pady=20, sticky="w")

        lbl_berat = ctk.CTkLabel(form_frame, text="Jumlah Berat (Kg):", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_berat.grid(row=1, column=0, padx=25, pady=(0, 20), sticky="w")
        self.entry_berat = ctk.CTkEntry(form_frame, width=220, height=35, font=ctk.CTkFont(size=14))
        self.entry_berat.grid(row=1, column=1, padx=10, pady=(0, 20), sticky="w")

        btn_action_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_action_frame.grid(row=1, column=2, columnspan=2, padx=10, pady=(0, 20), sticky="e")

        btn_simpan = ctk.CTkButton(btn_action_frame, text="Catat Panen", fg_color="#1a4d2e", hover_color="#143b23", width=110, height=38, font=ctk.CTkFont(size=14, weight="bold"), command=self.simpan_panen)
        btn_simpan.pack(side="left", padx=5)

        btn_hapus = ctk.CTkButton(btn_action_frame, text="Hapus Lot", fg_color="#c53030", hover_color="#9b2c2c", width=110, height=38, font=ctk.CTkFont(size=14, weight="bold"), command=self.hapus_panen)
        btn_hapus.pack(side="left", padx=5)

        table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=30, pady=15)

        columns = ("id_panen", "nama_petani", "komoditas", "berat", "tgl")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        self.tree.heading("id_panen", text="ID Panen")
        self.tree.heading("nama_petani", text="Nama Petani")
        self.tree.heading("komoditas", text="Jenis Komoditas")
        self.tree.heading("berat", text="Jumlah Berat (Kg)")
        self.tree.heading("tgl", text="Tanggal Panen")

        self.tree.column("id_panen", width=100, anchor="center")
        self.tree.column("nama_petani", width=220, anchor="w")
        self.tree.column("komoditas", width=200, anchor="w")
        self.tree.column("berat", width=160, anchor="center")
        self.tree.column("tgl", width=200, anchor="center")

        self.tree.tag_configure("evenrow", background="#ffffff")
        self.tree.tag_configure("oddrow", background="#f8fafc")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        scrollbar.pack(side="right", fill="y", pady=15)

    def on_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item[0], 'values')
            self.selected_id = values[0]

    def clear_form(self):
        self.selected_id = None
        self.entry_id_petani.delete(0, 'end')
        self.entry_komoditas.delete(0, 'end')
        self.entry_berat.delete(0, 'end')

    def simpan_panen(self):
        success, msg = InventoriController.tambah_panen(self.entry_id_petani.get(), self.entry_komoditas.get(), self.entry_berat.get())
        if success:
            messagebox.showinfo("Sukses", msg)
            self.clear_form()
            self.load_data()
        else:
            messagebox.showerror("Error", msg)

    def hapus_panen(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih data lot panen dari tabel yang ingin dihapus terlebih dahulu!")
            return
        values = self.tree.item(selected_item[0], 'values')
        id_p = values[0]
        if messagebox.askyesno("Konfirmasi Hapus", f"Apakah Anda yakin ingin menghapus Lot Panen ID {id_p}?"):
            success, msg = InventoriController.delete_panen(id_p)
            if success:
                messagebox.showinfo("Sukses", msg)
                self.load_data()
            else:
                messagebox.showerror("Gagal Hapus", msg)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for idx, item in enumerate(InventoriController.get_panen()):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            tgl_str = str(item['tgl_panen']) if item['tgl_panen'] else "-"
            self.tree.insert("", "end", values=(item['id_panen'], item['nama_petani'], item['jenis_komoditas'], f"{item['jumlah_berat']:.2f}", tgl_str), tags=(tag,))


class DistribusiView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f5f7f8")
        self.controller = controller

        title = ctk.CTkLabel(self, text="Alokasi & Status Distribusi Komoditas", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1a4d2e")
        title.pack(anchor="w", padx=30, pady=(30, 15))

        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        form_frame.pack(fill="x", padx=30, pady=10)

        lbl_id_panen = ctk.CTkLabel(form_frame, text="ID Panen:", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_id_panen.grid(row=0, column=0, padx=25, pady=20, sticky="w")
        self.entry_id_panen = ctk.CTkEntry(form_frame, width=220, height=35, font=ctk.CTkFont(size=14))
        self.entry_id_panen.grid(row=0, column=1, padx=10, pady=20, sticky="w")

        lbl_tujuan = ctk.CTkLabel(form_frame, text="Tujuan Pengiriman:", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_tujuan.grid(row=0, column=2, padx=25, pady=20, sticky="w")
        self.entry_tujuan = ctk.CTkEntry(form_frame, width=220, height=35, font=ctk.CTkFont(size=14))
        self.entry_tujuan.grid(row=0, column=3, padx=10, pady=20, sticky="w")

        lbl_jumlah = ctk.CTkLabel(form_frame, text="Jumlah Kirim (Kg):", font=ctk.CTkFont(size=15, weight="bold"))
        lbl_jumlah.grid(row=1, column=0, padx=25, pady=(0, 20), sticky="w")
        self.entry_jumlah = ctk.CTkEntry(form_frame, width=220, height=35, font=ctk.CTkFont(size=14))
        self.entry_jumlah.grid(row=1, column=1, padx=10, pady=(0, 20), sticky="w")

        btn_action_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_action_frame.grid(row=1, column=2, columnspan=2, padx=10, pady=(0, 20), sticky="e")

        btn_simpan = ctk.CTkButton(btn_action_frame, text="Proses Alokasi", fg_color="#1a4d2e", hover_color="#143b23", width=110, height=38, font=ctk.CTkFont(size=14, weight="bold"), command=self.simpan_distribusi)
        btn_simpan.pack(side="left", padx=5)

        btn_hapus = ctk.CTkButton(btn_action_frame, text="Hapus Alokasi", fg_color="#c53030", hover_color="#9b2c2c", width=110, height=38, font=ctk.CTkFont(size=14, weight="bold"), command=self.hapus_distribusi)
        btn_hapus.pack(side="left", padx=5)

        table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=30, pady=15)

        columns = ("id_distribusi", "id_panen", "nama_petani", "komoditas", "tujuan", "jumlah", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        self.tree.heading("id_distribusi", text="ID Distribusi")
        self.tree.heading("id_panen", text="ID Panen")
        self.tree.heading("nama_petani", text="Nama Petani")
        self.tree.heading("komoditas", text="Jenis Komoditas")
        self.tree.heading("tujuan", text="Tujuan Pengiriman")
        self.tree.heading("jumlah", text="Jumlah Kirim (Kg)")
        self.tree.heading("status", text="Status Pengiriman")

        self.tree.column("id_distribusi", width=100, anchor="center")
        self.tree.column("id_panen", width=90, anchor="center")
        self.tree.column("nama_petani", width=180, anchor="w")
        self.tree.column("komoditas", width=160, anchor="w")
        self.tree.column("tujuan", width=180, anchor="w")
        self.tree.column("jumlah", width=140, anchor="center")
        self.tree.column("status", width=140, anchor="center")

        self.tree.tag_configure("evenrow", background="#ffffff")
        self.tree.tag_configure("oddrow", background="#f8fafc")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        scrollbar.pack(side="right", fill="y", pady=15)

    def simpan_distribusi(self):
        success, msg = DistribusiController.tambah_distribusi(self.entry_id_panen.get(), self.entry_tujuan.get(), self.entry_jumlah.get())
        if success:
            messagebox.showinfo("Sukses", msg)
            self.entry_id_panen.delete(0, 'end')
            self.entry_tujuan.delete(0, 'end')
            self.entry_jumlah.delete(0, 'end')
            self.load_data()
        else:
            messagebox.showerror("Validasi Gagal", msg)

    def hapus_distribusi(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih data distribusi dari tabel yang ingin dihapus terlebih dahulu!")
            return
        values = self.tree.item(selected_item[0], 'values')
        id_d = values[0]
        if messagebox.askyesno("Konfirmasi Hapus", f"Apakah Anda yakin ingin menghapus data Distribusi ID {id_d}?"):
            success, msg = DistribusiController.delete_distribusi(id_d)
            if success:
                messagebox.showinfo("Sukses", msg)
                self.load_data()
            else:
                messagebox.showerror("Gagal Hapus", msg)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for idx, item in enumerate(DistribusiController.get_distribusi()):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(item['id_distribusi'], item['id_panen'], item['nama_petani'], item['jenis_komoditas'], item['tujuan_pengiriman'], f"{item['jumlah_dikirim']:.2f}", item['status_pengiriman']), tags=(tag,))


if __name__ == "__main__":
    app = AgriUnoApp()
    app.mainloop()