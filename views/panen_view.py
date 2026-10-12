import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime

class PanenView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f8f9fa")
        self.controller = controller
        self.selected_id = None
        
        ctk.CTkLabel(self, text="Inventori Hasil Panen", font=("Arial", 22, "bold"), text_color="#1b4332").pack(anchor="w", padx=30, pady=20)
        
        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=8)
        form_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(form_frame, text="ID Petani:").grid(row=0, column=0, padx=15, pady=12, sticky="w")
        self.e_id_petani = ctk.CTkEntry(form_frame, width=160)
        self.e_id_petani.grid(row=0, column=1, padx=10, pady=12)
        
        ctk.CTkLabel(form_frame, text="Jenis Komoditas:").grid(row=0, column=2, padx=15, pady=12, sticky="w")
        self.e_komoditas = ctk.CTkEntry(form_frame, width=160)
        self.e_komoditas.grid(row=0, column=3, padx=10, pady=12)
        
        ctk.CTkLabel(form_frame, text="Jumlah Berat (Kg):").grid(row=1, column=0, padx=15, pady=12, sticky="w")
        self.e_berat = ctk.CTkEntry(form_frame, width=160)
        self.e_berat.grid(row=1, column=1, padx=10, pady=12)
        
        ctk.CTkLabel(form_frame, text="Tanggal (YYYY-MM-DD):").grid(row=1, column=2, padx=15, pady=12, sticky="w")
        self.e_tgl = ctk.CTkEntry(form_frame, width=160)
        self.e_tgl.grid(row=1, column=3, padx=10, pady=12)
        
        btn_box = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_box.grid(row=2, column=0, columnspan=4, padx=10, pady=15)
        
        ctk.CTkButton(btn_box, text="Simpan", fg_color="#1b4332", hover_color="#2d6a4f", width=100, command=self.simpan).pack(side="left", padx=8)
        ctk.CTkButton(btn_box, text="Ubah", fg_color="#d97706", hover_color="#b45309", width=100, command=self.ubah).pack(side="left", padx=8)
        ctk.CTkButton(btn_box, text="Hapus", fg_color="#dc2626", hover_color="#b91c1c", width=100, command=self.hapus).pack(side="left", padx=8)
        
        self.tree = ttk.Treeview(self, columns=("id", "id_p", "komoditas", "berat", "tgl"), show="headings")
        self.tree.heading("id", text="ID Panen")
        self.tree.heading("id_p", text="ID Petani")
        self.tree.heading("komoditas", text="Jenis Komoditas")
        self.tree.heading("berat", text="Jumlah Berat (Kg)")
        self.tree.heading("tgl", text="Tanggal Panen")
        self.tree.pack(fill="both", expand=True, padx=30, pady=20)
        self.tree.bind("<ButtonRelease-1>", self.on_select)
        
        self.reset_form()
        self.load_table()

    def reset_form(self):
        self.selected_id = None
        self.e_id_petani.delete(0, 'end'); self.e_komoditas.delete(0, 'end'); self.e_berat.delete(0, 'end'); self.e_tgl.delete(0, 'end')
        self.e_tgl.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def load_table(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        for item in self.controller.get_panen():
            self.tree.insert("", "end", values=(item.get("id_panen"), item.get("id_petani"), item.get("jenis_komoditas"), item.get("jumlah_berat"), item.get("tgl_panen")))

    def simpan(self):
        sukses, pesan = self.controller.tambah_panen(self.e_id_petani.get(), self.e_komoditas.get(), self.e_berat.get(), self.e_tgl.get())
        if sukses:
            messagebox.showinfo("Sukses", pesan); self.reset_form(); self.load_table()
        else: messagebox.showerror("Error", pesan)

    def on_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            self.selected_id = values[0]
            self.e_id_petani.delete(0, 'end'); self.e_id_petani.insert(0, values[1])
            self.e_komoditas.delete(0, 'end'); self.e_komoditas.insert(0, values[2])
            self.e_berat.delete(0, 'end'); self.e_berat.insert(0, values[3])
            self.e_tgl.delete(0, 'end'); self.e_tgl.insert(0, str(values[4]))

    def ubah(self):
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data panen pada tabel yang ingin diubah!"); return
        sukses, pesan = self.controller.update_panen(self.selected_id, self.e_id_petani.get(), self.e_komoditas.get(), self.e_berat.get(), self.e_tgl.get())
        if sukses:
            messagebox.showinfo("Sukses", pesan); self.reset_form(); self.load_table()
        else: messagebox.showerror("Error", pesan)

    def hapus(self):
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data panen pada tabel yang ingin dihapus!"); return
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data panen ini?"):
            sukses, pesan = self.controller.hapus_panen(self.selected_id)
            if sukses:
                messagebox.showinfo("Sukses", pesan); self.reset_form(); self.load_table()