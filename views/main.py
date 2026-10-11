import customtkinter as ctk
from tkinter import ttk
from controllers.controller import AgriController

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

class AgriUnoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Sistem Informasi Manajemen AgriUno")
        self.geometry("850x550")
        
        # Label Judul Utama
        self.label_title = ctk.CTkLabel(self, text="Manajemen Data Petani - AgriUno", font=("Arial", 18, "bold"))
        self.label_title.pack(pady=20)
        
        # Tombol untuk memuat data dari database MySQL
        self.btn_load = ctk.CTkButton(self, text="Muat Data Petani", command=self.muat_tabel)
        self.btn_load.pack(pady=10)
        
        # Tabel Tampilan Data (Treeview)
        self.tree = ttk.Treeview(self, columns=("ID", "Nama", "Lokasi", "Komoditas"), show="headings")
        self.tree.heading("ID", text="ID Petani")
        self.tree.heading("Nama", text="Nama Petani")
        self.tree.heading("Lokasi", text="Lokasi Lahan")
        self.tree.heading("Komoditas", text="Komoditas Utama")
        self.tree.pack(pady=10, fill="both", expand=True, padx=20)

    def muat_tabel(self):
        # Bersihkan data lama di tabel
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        # Ambil data dari Controller
        data = AgriController.ambil_data_petani()
        for row in data:
            self.tree.insert("", "end", values=row)

if __name__ == "__main__":
    app = AgriUnoApp()
    app.mainloop()