import customtkinter as ctk
from tkinter import ttk, messagebox

class PetaniView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f8f9fa")
        self.controller = controller
        self.selected_id = None
        
        ctk.CTkLabel(self, text="Manajemen Data Petani", font=("Arial", 22, "bold"), text_color="#1b4332").pack(anchor="w", padx=30, pady=20)
        
        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=8)
        form_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(form_frame, text="Nama Petani:").grid(row=0, column=0, padx=15, pady=12, sticky="w")
        self.e_nama = ctk.CTkEntry(form_frame, width=180)
        self.e_nama.grid(row=0, column=1, padx=10, pady=12)
        
        ctk.CTkLabel(form_frame, text="Lokasi Lahan:").grid(row=0, column=2, padx=15, pady=12, sticky="w")
        self.e_lokasi = ctk.CTkEntry(form_frame, width=180)
        self.e_lokasi.grid(row=0, column=3, padx=10, pady=12)
        
        ctk.CTkLabel(form_frame, text="Komoditas Utama:").grid(row=1, column=0, padx=15, pady=12, sticky="w")
        self.e_komoditas = ctk.CTkEntry(form_frame, width=180)
        self.e_komoditas.grid(row=1, column=1, padx=10, pady=12)
        
        btn_box = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_box.grid(row=1, column=2, columnspan=2, padx=10, pady=12, sticky="e")
        
        ctk.CTkButton(btn_box, text="Simpan", fg_color="#1b4332", hover_color="#2d6a4f", width=80, command=self.simpan).pack(side="left", padx=5)
        ctk.CTkButton(btn_box, text="Ubah", fg_color="#d97706", hover_color="#b45309", width=80, command=self.ubah).pack(side="left", padx=5)
        ctk.CTkButton(btn_box, text="Hapus", fg_color="#dc2626", hover_color="#b91c1c", width=80, command=self.hapus).pack(side="left", padx=5)
        
        self.tree = ttk.Treeview(self, columns=("id", "nama", "lokasi", "komoditas"), show="headings")
        self.tree.heading("id", text="ID Petani")
        self.tree.heading("nama", text="Nama Petani")
        self.tree.heading("lokasi", text="Lokasi Lahan")
        self.tree.heading("komoditas", text="Komoditas Utama")
        self.tree.pack(fill="both", expand=True, padx=30, pady=20)
        self.tree.bind("<ButtonRelease-1>", self.on_select)
        
        self.load_table()

    def load_table(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        for p in self.controller.get_petani():
            self.tree.insert("", "end", values=(p["id_petani"], p["nama_petani"], p["lokasi_lahan"], p["komoditas_utama"]))

    def clear_form(self):
        self.selected_id = None
        self.e_nama.delete(0, 'end'); self.e_lokasi.delete(0, 'end'); self.e_komoditas.delete(0, 'end')

    def simpan(self):
        sukses, pesan = self.controller.tambah_petani(self.e_nama.get(), self.e_lokasi.get(), self.e_komoditas.get())
        if sukses:
            messagebox.showinfo("Sukses", pesan); self.clear_form(); self.load_table()
        else: messagebox.showerror("Error", pesan)

    def on_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            self.selected_id = values[0]
            self.e_nama.delete(0, 'end'); self.e_nama.insert(0, values[1])
            self.e_lokasi.delete(0, 'end'); self.e_lokasi.insert(0, values[2])
            self.e_komoditas.delete(0, 'end'); self.e_komoditas.insert(0, values[3])

    def ubah(self):
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data petani pada tabel yang ingin diubah!"); return
        sukses, pesan = self.controller.update_petani(self.selected_id, self.e_nama.get(), self.e_lokasi.get(), self.e_komoditas.get())
        if sukses:
            messagebox.showinfo("Sukses", pesan); self.clear_form(); self.load_table()
        else: messagebox.showerror("Error", pesan)

    def hapus(self):
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data petani pada tabel yang ingin dihapus!"); return
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data ini?"):
            sukses, pesan = self.controller.hapus_petani(self.selected_id)
            if sukses:
                messagebox.showinfo("Sukses", pesan); self.clear_form(); self.load_table()
            else:
                messagebox.showerror("Gagal Menghapus", pesan)