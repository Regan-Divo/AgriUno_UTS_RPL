"""
==========================================================
APLIKASI UTAMA DESKTOP - AGRIUNO (DENGAN AUTENTIKASI LOGIN)
==========================================================
"""
import customtkinter as ctk
from controllers.controller import AgriUnoController
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.petani_view import PetaniView
from views.panen_view import PanenView
from views.distribusi_view import DistribusiView

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

class AgriUnoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AgriUno - Sistem Informasi Manajemen Rantai Pasok Pertanian")
        self.geometry("1150x680")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Sidebar Kiri
        sidebar = ctk.CTkFrame(self, width=220, fg_color="#1b4332", corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(sidebar, text="🌾 AgriUno", font=ctk.CTkFont(size=22, weight="bold"), text_color="white").pack(pady=(35, 5))
        ctk.CTkLabel(sidebar, text="Manajemen Pertanian Lokal", font=("Arial", 11), text_color="#cbd5e1").pack(pady=(0, 30))
        
        ctk.CTkButton(sidebar, text="Dashboard", fg_color="transparent", text_color="white", hover_color="#2d6a4f", anchor="w", command=lambda: self.show_page("dashboard")).pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(sidebar, text="Kelola Petani", fg_color="transparent", text_color="white", hover_color="#2d6a4f", anchor="w", command=lambda: self.show_page("petani")).pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(sidebar, text="Inventori Panen", fg_color="transparent", text_color="white", hover_color="#2d6a4f", anchor="w", command=lambda: self.show_page("panen")).pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(sidebar, text="Distribusi", fg_color="transparent", text_color="white", hover_color="#2d6a4f", anchor="w", command=lambda: self.show_page("distribusi")).pack(fill="x", padx=15, pady=5)
        
        footer_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", padx=15, pady=20)
        ctk.CTkLabel(footer_frame, text="Status: Aktif (Admin)", font=("Arial", 11), text_color="#cbd5e1").pack(anchor="w")
        ctk.CTkButton(footer_frame, text="Keluar", fg_color="#dc2626", hover_color="#b91c1c", text_color="white", command=self.destroy).pack(fill="x", pady=(8, 0))

        # Konten Utama Kanan
        self.content = ctk.CTkFrame(self, fg_color="#f8f9fa", corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        
        self.pages = {}
        for PageClass in (DashboardView, PetaniView, PanenView, DistribusiView):
            page = PageClass(parent=self.content, controller=AgriUnoController)
            self.pages[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")
            
        self.show_page("dashboard")
        
    def show_page(self, page_name):
        mapping = {
            "dashboard": "DashboardView", 
            "petani": "PetaniView",
            "panen": "PanenView",
            "distribusi": "DistribusiView"
        }
        target = self.pages.get(mapping.get(page_name))
        if target:
            if hasattr(target, 'load_data'): target.load_data()
            elif hasattr(target, 'load_table'): target.load_table()
            target.tkraise()

def run_main_app():
    app = AgriUnoApp()
    app.mainloop()

if __name__ == "__main__":
    login_window = LoginView(on_login_success=run_main_app)
    login_window.mainloop()