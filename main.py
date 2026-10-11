# ==========================================================
# APLIKASI UTAMA DESKTOP - AGRIUNO 
# Kelompok 1 | Praktikum Rekayasa Perangkat Lunak 
# ==========================================================
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from controllers.controller import AgriUnoController

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

class AgriUnoEnterpriseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AgriUno - Sistem Informasi Pengelolaan Rantai Pasok Hasil Panen")
        self.geometry("1150x700")
        self.minsize(1000, 600)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar Navigasi
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1b4332")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Logo / Branding Header (Tertulis "AgriUno" dengan huruf A & U kapital)
        logo_box = ctk.CTkFrame(self.sidebar_frame, fg_color="#143224", corner_radius=6)
        logo_box.grid(row=0, column=0, padx=15, pady=(25, 15), sticky="ew")
        ctk.CTkLabel(logo_box, text="AgriUno", font=ctk.CTkFont(size=16, weight="bold"), text_color="white").pack(pady=10)

        # Menu Navigasi Sidebar (Langsung ke Dashboard sebagai halaman utama)
        ctk.CTkButton(self.sidebar_frame, text="Dashboard", fg_color="transparent", text_color="white", hover_color="#2d6a4f", anchor="w", command=lambda: self.switch_frame("dashboard")).grid(row=1, column=0, padx=15, pady=8, sticky="ew")
        ctk.CTkButton(self.sidebar_frame, text="Kelola Petani", fg_color="transparent", text_color="white", hover_color="#2d6a4f", anchor="w", command=lambda: self.switch_frame("petani")).grid(row=2, column=0, padx=15, pady=8, sticky="ew")
        ctk.CTkButton(self.sidebar_frame, text="Inventori Panen", fg_color="transparent", text_color="white", hover_color="#2d6a4f", anchor="w", command=lambda: self.switch_frame("panen")).grid(row=3, column=0, padx=15, pady=8, sticky="ew")
        ctk.CTkButton(self.sidebar_frame, text="Distribusi", fg_color="transparent", text_color="white", hover_color="#2d6a4f", anchor="w", command=lambda: self.switch_frame("distribusi")).grid(row=4, column=0, padx=15, pady=8, sticky="ew")

        self.content_frame = ctk.CTkFrame(self, fg_color="#f8f9fa", corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (DashboardView, PetaniView, PanenView, DistribusiView):
            frame = F(parent=self.content_frame, controller=AgriUnoController, main_app=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.switch_frame("dashboard")

    def switch_frame(self, page_name_short):
        mapping = {
            "dashboard": "DashboardView",
            "petani": "PetaniView",
            "panen": "PanenView",
            "distribusi": "DistribusiView"
        }
        frame = self.frames[mapping.get(page_name_short, "DashboardView")]
        frame.tkraise()
        if hasattr(frame, "load_data"): frame.load_data()


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller, main_app):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        ctk.CTkLabel(self, text="Dashboard Gudang AgriUno", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1b4332").pack(anchor="w", padx=30, pady=(30, 5))
        ctk.CTkLabel(self, text="Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal", font=ctk.CTkFont(size=14), text_color="#555555").pack(anchor="w", padx=30, pady=(0, 15))

        # Kartu Statistik Ringkasan
        card_frame = ctk.CTkFrame(self, fg_color="transparent")
        card_frame.pack(fill="x", padx=30, pady=10)

        self.val_petani_lbl, c1 = self.create_card(card_frame, "Total Petani Terdaftar", "0", "#2d6a4f")
        c1.pack(side="left", padx=(0, 15), expand=True, fill="both")

        self.val_panen_lbl, c2 = self.create_card(card_frame, "Lot Panen Masuk", "0", "#40916c")
        c2.pack(side="left", padx=(0, 15), expand=True, fill="both")

        self.val_dist_lbl, c3 = self.create_card(card_frame, "Alokasi Distribusi", "0", "#52b788")
        c3.pack(side="left", expand=True, fill="both")

        # Kotak Informasi & Identitas Kelompok (Aman dari teks terpotong)
        info_box = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        info_box.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(info_box, text="Selamat Datang - Praktikum RPL Kelompok 1", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1b4332").pack(anchor="w", padx=25, pady=(20, 10))

        desc = (
            "Aplikasi AgriUno dikembangkan untuk tugas UTS Rekayasa Perangkat Lunak. "
            "Sistem ini menerapkan pola MVC dan basis data MySQL untuk pengelolaan rantai pasok.\n\n"
            "Anggota Kelompok 1 (Kelas B):\n"
            "1. Sinaan Az Zufar (F5212520043)\n"
            "2. Aura Qadriandhara (F5212520053)\n"
            "3. Musholli Regan Divo Rasjid (F5212520064)\n"
            "4. Yuda Pramesta (F5212520066)\n"
            "5. Widyo Prabowo (F5212520068)\n"
            "6. Kissya Syahluna R (F5212520074)"
        )
        ctk.CTkLabel(info_box, text=desc, font=ctk.CTkFont(size=13), justify="left", text_color="#333333").pack(anchor="w", padx=25, pady=(0, 20))

    def create_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, height=100)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13, weight="bold"), text_color="white").pack(pady=(12, 0), padx=20, anchor="w")
        lbl_v = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=26, weight="bold"), text_color="white")
        lbl_v.pack(pady=(2, 12), padx=20, anchor="w")
        return lbl_v, card

    def load_data(self):
        try:
            self.val_petani_lbl.configure(text=str(len(self.controller.get_petani())))
            self.val_panen_lbl.configure(text=str(len(self.controller.get_panen())))
            self.val_dist_lbl.configure(text=str(len(self.controller.get_distribusi())))
        except Exception:
            pass


class PetaniView(ctk.CTkFrame):
    def __init__(self, parent, controller, main_app):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        ctk.CTkLabel(self, text="Manajemen Data Petani", font=ctk.CTkFont(size=22, weight="bold"), text_color="#1b4332").pack(anchor="w", padx=30, pady=(30, 15))
        
        form = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        form.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(form, text="Nama Petani:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        self.ent_nama = ctk.CTkEntry(form, width=200)
        self.ent_nama.grid(row=0, column=1, padx=10, pady=15)
        ctk.CTkLabel(form, text="Lokasi Lahan:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, padx=20, pady=15, sticky="w")
        self.ent_lokasi = ctk.CTkEntry(form, width=200)
        self.ent_lokasi.grid(row=0, column=3, padx=10, pady=15)
        ctk.CTkLabel(form, text="Komoditas Utama:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=20, pady=15, sticky="w")
        self.ent_komoditas = ctk.CTkEntry(form, width=200)
        self.ent_komoditas.grid(row=1, column=1, padx=10, pady=15)
        ctk.CTkButton(form, text="Simpan Petani", fg_color="#2d6a4f", hover_color="#1b4332", command=self.simpan).grid(row=1, column=3, padx=10, pady=15, sticky="e")

        table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=30, pady=20)
        columns = ("ID", "Nama Petani", "Lokasi Lahan", "Komoditas Utama")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        for col in columns: self.tree.heading(col, text=col); self.tree.column(col, width=150, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

    def simpan(self):
        if self.controller.simpan_petani(self.ent_nama.get().strip(), self.ent_lokasi.get().strip(), self.ent_komoditas.get().strip()):
            messagebox.showinfo("Sukses", "Data petani berhasil disimpan!")
            self.ent_nama.delete(0, 'end'); self.ent_lokasi.delete(0, 'end'); self.ent_komoditas.delete(0, 'end')
            self.load_data()

    def load_data(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        for p in self.controller.get_petani(): self.tree.insert("", "end", values=(p['id_petani'], p['nama_petani'], p['lokasi_lahan'], p['komoditas_utama']))


class PanenView(ctk.CTkFrame):
    def __init__(self, parent, controller, main_app):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        ctk.CTkLabel(self, text="Pencatatan Inventori Panen Masuk", font=ctk.CTkFont(size=22, weight="bold"), text_color="#1b4332").pack(anchor="w", padx=30, pady=(30, 15))
        
        form = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        form.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(form, text="ID Petani:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        self.ent_id_petani = ctk.CTkEntry(form, width=150)
        self.ent_id_petani.grid(row=0, column=1, padx=10, pady=15)
        ctk.CTkLabel(form, text="Jenis Komoditas:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, padx=20, pady=15, sticky="w")
        self.ent_komoditas = ctk.CTkEntry(form, width=150)
        self.ent_komoditas.grid(row=0, column=3, padx=10, pady=15)
        ctk.CTkLabel(form, text="Jumlah Berat (Kg):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=20, pady=15, sticky="w")
        self.ent_berat = ctk.CTkEntry(form, width=150)
        self.ent_berat.grid(row=1, column=1, padx=10, pady=15)
        ctk.CTkButton(form, text="Catat Panen Masuk", fg_color="#2d6a4f", hover_color="#1b4332", command=self.simpan).grid(row=1, column=3, padx=10, pady=15, sticky="e")

        table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=30, pady=20)
        columns = ("ID Panen", "Nama Petani", "Jenis Komoditas", "Jumlah Berat (Kg)", "Tanggal Panen")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        for col in columns: self.tree.heading(col, text=col); self.tree.column(col, width=140, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

    def simpan(self):
        if self.controller.simpan_panen(self.ent_id_petani.get().strip(), self.ent_komoditas.get().strip(), self.ent_berat.get().strip(), datetime.now().strftime("%Y-%m-%d")):
            messagebox.showinfo("Sukses", "Data inventori panen berhasil dicatat!")
            self.ent_id_petani.delete(0, 'end'); self.ent_komoditas.delete(0, 'end'); self.ent_berat.delete(0, 'end')
            self.load_data()

    def load_data(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        for p in self.controller.get_panen(): self.tree.insert("", "end", values=(p['id_panen'], p['nama_petani'], p['jenis_komoditas'], p['jumlah_berat'], p['tgl_panen']))


class DistribusiView(ctk.CTkFrame):
    def __init__(self, parent, controller, main_app):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        ctk.CTkLabel(self, text="Alokasi & Status Distribusi Komoditas", font=ctk.CTkFont(size=22, weight="bold"), text_color="#1b4332").pack(anchor="w", padx=30, pady=(30, 15))
        
        form = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        form.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(form, text="ID Petani:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        self.ent_id_petani = ctk.CTkEntry(form, width=150)
        self.ent_id_petani.grid(row=0, column=1, padx=10, pady=15)
        ctk.CTkLabel(form, text="Tujuan Pengiriman:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, padx=20, pady=15, sticky="w")
        self.ent_tujuan = ctk.CTkEntry(form, width=150)
        self.ent_tujuan.grid(row=0, column=3, padx=10, pady=15)
        ctk.CTkLabel(form, text="Jumlah Kirim (Kg):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=20, pady=15, sticky="w")
        self.ent_jumlah = ctk.CTkEntry(form, width=150)
        self.ent_jumlah.grid(row=1, column=1, padx=10, pady=15)
        ctk.CTkButton(form, text="Proses Alokasi", fg_color="#2d6a4f", hover_color="#1b4332", command=self.simpan).grid(row=1, column=3, padx=10, pady=15, sticky="e")

        table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=30, pady=20)
        columns = ("ID Distribusi", "Jenis Komoditas", "Tujuan Pengiriman", "Jumlah Kirim (Kg)", "Status Pengiriman")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        for col in columns: self.tree.heading(col, text=col); self.tree.column(col, width=140, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

    def simpan(self):
        if self.controller.simpan_distribusi(self.ent_id_petani.get().strip(), self.ent_tujuan.get().strip(), self.ent_jumlah.get().strip(), "Diproses"):
            messagebox.showinfo("Sukses", "Alokasi distribusi berhasil disimpan!")
            self.ent_id_petani.delete(0, 'end'); self.ent_tujuan.delete(0, 'end'); self.ent_jumlah.delete(0, 'end')
            self.load_data()

    def load_data(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        for d in self.controller.get_distribusi(): self.tree.insert("", "end", values=(d['id_distribusi'], d['jenis_komoditas'], d['tujuan_pengiriman'], d['jumlah_dikirim'], d['status_pengiriman']))


if __name__ == "__main__":
    app = AgriUnoEnterpriseApp()
    app.mainloop()