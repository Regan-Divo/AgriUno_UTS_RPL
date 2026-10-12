import customtkinter as ctk
from tkinter import ttk, messagebox

class DistribusiView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f8f9fa")
        self.controller = controller
        self.selected_id = None
        
        ctk.CTkLabel(self, text="Alokasi Distribusi Logistik", font=("Arial", 22, "bold"), text_color="#1b4332").pack(anchor="w", padx=30, pady=20)
        
        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=8)
        form_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(form_frame, text="ID Panen:").grid(row=0, column=0, padx=15, pady=12, sticky="w")
        self.e_id_panen = ctk.CTkEntry(form_frame, width=160)
        self.e_id_panen.grid(row=0, column=1, padx=10, pady=12)
        
        ctk.CTkLabel(form_frame, text="Tujuan Pengiriman:").grid(row=0, column=2, padx=15, pady=12, sticky="w")
        self.e_tujuan = ctk.CTkEntry(form_frame, width=160)
        self.e_tujuan.grid(row=0, column=3, padx=10, pady=12)
        
        ctk.CTkLabel(form_frame, text="Jumlah Dikirim (Kg):").grid(row=1, column=0, padx=15, pady=12, sticky="w")
        self.e_jumlah = ctk.CTkEntry(form_frame, width=160)
        self.e_jumlah.grid(row=1, column=1, padx=10, pady=12)
        
        ctk.CTkLabel(form_frame, text="Status Pengiriman:").grid(row=1, column=2, padx=15, pady=12, sticky="w")
        self.opt_status = ctk.CTkOptionMenu(form_frame, values=["Diproses", "Dalam Pengiriman", "Terkirim"], width=160, fg_color="#1b4332", button_color="#2d6a4f")
        self.opt_status.grid(row=1, column=3, padx=10, pady=12)
        self.opt_status.set("Diproses")
        
        btn_box = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_box.grid(row=2, column=0, columnspan=4, padx=10, pady=15)
        
        ctk.CTkButton(btn_box, text="Simpan", fg_color="#1b4332", hover_color="#2d6a4f", width=100, command=self.simpan).pack(side="left", padx=8)
        ctk.CTkButton(btn_box, text="Ubah Status", fg_color="#d97706", hover_color="#b45309", width=100, command=self.ubah).pack(side="left", padx=8)
        ctk.CTkButton(btn_box, text="Hapus", fg_color="#dc2626", hover_color="#b91c1c", width=100, command=self.hapus).pack(side="left", padx=8)
        
        self.tree = ttk.Treeview(self, columns=("id", "id_panen", "tujuan", "jumlah", "status"), show="headings")
        self.tree.heading("id", text="ID Distribusi")
        self.tree.heading("id_panen", text="ID Panen")
        self.tree.heading("tujuan", text="Tujuan Pengiriman")
        self.tree.heading("jumlah", text="Jumlah Dikirim (Kg)")
        self.tree.heading("status", text="Status Pengiriman")
        self.tree.pack(fill="both", expand=True, padx=30, pady=20)
        self.tree.bind("<ButtonRelease-1>", self.on_select)
        
        self.load_table()

    def clear_form(self):
        self.selected_id = None
        self.e_id_panen.delete(0, 'end'); self.e_tujuan.delete(0, 'end'); self.e_jumlah.delete(0, 'end')
        self.opt_status.set("Diproses")

    def load_table(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        for item in self.controller.get_distribusi():
            self.tree.insert("", "end", values=(item.get("id_distribusi"), item.get("id_panen"), item.get("tujuan_pengiriman"), item.get("jumlah_dikirim"), item.get("status_pengiriman")))

    def simpan(self):
        sukses, pesan = self.controller.tambah_distribusi(self.e_id_panen.get(), self.e_tujuan.get(), self.e_jumlah.get())
        if sukses:
            messagebox.showinfo("Sukses", pesan); self.clear_form(); self.load_table()
        else: messagebox.showerror("Validasi Stok (BR-02)", pesan)

    def on_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            self.selected_id = values[0]
            self.e_id_panen.delete(0, 'end'); self.e_id_panen.insert(0, values[1])
            self.e_tujuan.delete(0, 'end'); self.e_tujuan.insert(0, values[2])
            self.e_jumlah.delete(0, 'end'); self.e_jumlah.insert(0, values[3])
            self.opt_status.set(values[4])

    def ubah(self):
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data distribusi pada tabel yang ingin diubah!"); return
        sukses, pesan = self.controller.update_distribusi(self.selected_id, self.e_id_panen.get(), self.e_tujuan.get(), self.e_jumlah.get(), self.opt_status.get())
        if sukses:
            messagebox.showinfo("Sukses", pesan); self.clear_form(); self.load_table()
        else: messagebox.showerror("Error", pesan)

    def hapus(self):
        if not self.selected_id:
            messagebox.showwarning("Peringatan", "Pilih data distribusi pada tabel yang ingin dihapus!"); return
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus alokasi distribusi ini?"):
            sukses, pesan = self.controller.hapus_distribusi(self.selected_id)
            if sukses:
                messagebox.showinfo("Sukses", pesan); self.clear_form(); self.load_table()
            else: messagebox.showerror("Error", pesan)