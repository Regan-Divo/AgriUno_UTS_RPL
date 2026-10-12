import customtkinter as ctk
from tkinter import messagebox

class LoginView(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.title("AgriUno - Login Administrator")
        self.geometry("400x380")
        self.resizable(False, False)
        self.configure(fg_color="#f8f9fa")
        
        frame = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        ctk.CTkLabel(frame, text="🌾 AgriUno", font=("Arial", 24, "bold"), text_color="#1b4332").pack(pady=(35, 5))
        ctk.CTkLabel(frame, text="Sistem Manajemen Pertanian Lokal", font=("Arial", 11), text_color="gray").pack(pady=(0, 25))
        
        self.e_user = ctk.CTkEntry(frame, width=280, height=38, placeholder_text="Username (admin)")
        self.e_user.pack(pady=8)
        self.e_user.insert(0, "admin")
        
        self.e_pass = ctk.CTkEntry(frame, width=280, height=38, placeholder_text="Password (12345)", show="*")
        self.e_pass.pack(pady=8)
        self.e_pass.insert(0, "12345")
        
        ctk.CTkButton(frame, text="Masuk Sistem", fg_color="#1b4332", hover_color="#2d6a4f", width=280, height=40, font=("Arial", 13, "bold"), command=self.proses_login).pack(pady=(20, 35))

    def proses_login(self):
        if self.e_user.get() == "admin" and self.e_pass.get() == "12345":
            messagebox.showinfo("Sukses", "Login Berhasil! Selamat datang, Administrator.")
            self.destroy()
            self.on_login_success()
        else:
            messagebox.showerror("Gagal Login", "Username atau Password salah!")