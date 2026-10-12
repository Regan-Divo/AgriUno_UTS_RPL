import customtkinter as ctk

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#f8f9fa")
        self.controller = controller
        
        ctk.CTkLabel(self, text="Dashboard Ringkasan Sistem Operasional", font=("Arial", 22, "bold"), text_color="#1b4332").pack(anchor="w", padx=30, pady=20)
        
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(anchor="w", padx=30, pady=5)
        
        self.lbl_p = self.create_stat_card(cards_frame, "Total Petani", "0", "#1d4ed8", 0)
        self.lbl_h = self.create_stat_card(cards_frame, "Total Lot Panen", "0", "#d97706", 1)
        self.lbl_d = self.create_stat_card(cards_frame, "Total Distribusi", "0", "#2d6a4f", 2)
        
        chart_box = ctk.CTkFrame(self, fg_color="white", corner_radius=8)
        chart_box.pack(fill="x", padx=30, pady=20)
        ctk.CTkLabel(chart_box, text="Indikator Kinerja Rantai Pasok Pertanian", font=("Arial", 14, "bold"), text_color="#1b4332").pack(anchor="w", padx=20, pady=(15, 10))
        
        self.create_progress_indicator(chart_box, "Aktivasi Petani Terdaftar", 0.75)
        self.create_progress_indicator(chart_box, "Kapasitas Serapan Gudang", 0.50)
        self.create_progress_indicator(chart_box, "Efisiensi Logistik Distribusi", 0.85)

        info_box = ctk.CTkFrame(self, fg_color="white", corner_radius=8)
        info_box.pack(fill="x", padx=30, pady=5)
        ctk.CTkLabel(info_box, text="Tentang Sistem AgriUno", font=("Arial", 14, "bold"), text_color="#1b4332").pack(anchor="w", padx=20, pady=(12, 5))
        desc = "AgriUno adalah platform manajemen hasil panen pertanian lokal terpadu untuk pencatatan data petani, inventori gudang, dan logistik distribusi secara real-time."
        ctk.CTkLabel(info_box, text=desc, font=("Arial", 12), text_color="#555555", justify="left", wraplength=700).pack(anchor="w", padx=20, pady=(0, 15))

        self.load_data()

    def create_stat_card(self, parent, title, val, color, col):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8, width=220, height=85)
        card.pack_propagate(False)
        card.grid(row=0, column=col, padx=(0, 15))
        ctk.CTkLabel(card, text=title, font=("Arial", 11), text_color="gray").pack(anchor="w", padx=15, pady=(10, 0))
        lbl = ctk.CTkLabel(card, text=val, font=("Arial", 22, "bold"), text_color=color)
        lbl.pack(anchor="w", padx=15)
        return lbl

    def create_progress_indicator(self, parent, label_text, progress_val):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(row, text=label_text, font=("Arial", 12), width=200, anchor="w").pack(side="left")
        pbar = ctk.CTkProgressBar(row, width=450, progress_color="#2d6a4f")
        pbar.set(progress_val)
        pbar.pack(side="left", padx=10)

    def load_data(self):
        self.lbl_p.configure(text=str(len(self.controller.get_petani())))
        self.lbl_h.configure(text=str(len(self.controller.get_panen())))
        self.lbl_d.configure(text=str(len(self.controller.get_distribusi())))