"""Halaman pengelolaan akun pengguna (khusus Administrator)."""

import customtkinter as ctk

from config import ui_kit
from controllers.auth_controller import AuthController
from controllers.controller import AgriUnoController
from controllers.user_controller import UserController
from models.user_model import UserModel
from views.base_view import HalamanDasar

STATUS_WARNA = {
    "admin": (ui_kit.HIJAU_LEMBUT, ui_kit.HIJAU_TEKS),
    "operator": (ui_kit.BIRU_LEMBUT, ui_kit.BIRU),
    "petani": (ui_kit.AMBER_LEMBUT, "#92400e"),
}


class PenggunaView(HalamanDasar):
    """Daftar akun pengguna beserta tindakan pemeliharaan."""

    _LABEL_TAMBAH = "+  Tambah Akun"

    def __init__(self, parent, app):
        super().__init__(
            parent,
            app,
            "Kelola Pengguna",
            "Pemeliharaan akun pengguna pada tabel users: profil, status aktif, dan kata sandi.",
        )
        # Halaman khusus Administrator tanpa tombol tambah akun.
        if hasattr(self, "tombol_tambah"):
            self.tombol_tambah.destroy()
        self.tombol_tambah = None

    # --------------------------------------------------------
    def _buka_form_tambah(self):
        """Akun dibuat melalui formulir registrasi mandiri (FR-08)."""
        ui_kit.toast(
            self.app,
            "Akun baru dibuat melalui halaman Registrasi pada tampilan login.",
            jenis="info",
        )

    # --------------------------------------------------------
    def _bangun_tabel(self, kartu_tabel):
        kepala = ctk.CTkFrame(kartu_tabel, fg_color="transparent")
        kepala.pack(fill="x", padx=20, pady=(16, 4))
        ctk.CTkLabel(
            kepala, text="Daftar Akun Pengguna", font=(ui_kit.FONT, 13, "bold"), text_color=ui_kit.TEKS
        ).pack(side="left")

        kolom = (
            ("id", "ID", 48, "center"),
            ("username", "Username", 140, "w"),
            ("nama", "Nama Lengkap", 190, "w"),
            ("role", "Peran", 120, "center"),
            ("status", "Status", 110, "center"),
            ("dibuat", "Dibuat", 120, "center"),
        )
        wadah, self.tree = ui_kit.tabel(kartu_tabel, kolom, tinggi=13)
        wadah.pack(fill="both", expand=True, padx=20, pady=(4, 16))
        self.tree.bind("<ButtonRelease-1>", self._saat_pilih)

    # --------------------------------------------------------
    def muat(self):
        """Menyegarkan tabel akun pengguna."""
        for baris in self.tree.get_children():
            self.tree.delete(baris)

        data = UserController.daftar_akun(self.e_cari.get())
        for idx, item in enumerate(data):
            aktif = int(item["is_active"] or 0)
            self.tree.insert(
                "",
                "end",
                iid=str(item["id_user"]),
                values=(
                    item["id_user"],
                    item["username"],
                    item["full_name"] or "-",
                    item["role"],
                    "Aktif" if aktif else "Nonaktif",
                    str(item["created_at"] or "-")[:10],
                ),
                tags=(ui_kit.tag_zebra(idx),),
            )
        self.chip_jumlah.configure(text="%d akun" % len(data))

        if self.terpilih is not None:
            if self.tree.exists(str(self.terpilih)):
                self.tree.selection_set(str(self.terpilih))
                self._muat_detail()
            else:
                self.terpilih = None
                self._detail_kosong()

    # --------------------------------------------------------
    def _saat_pilih(self, _event=None):
        fokus = self.tree.focus()
        if not fokus:
            return
        self.terpilih = int(fokus)
        self._muat_detail()

    def _cari_data(self):
        for item in UserController.daftar_akun():
            if int(item["id_user"]) == self.terpilih:
                return item
        return None

    # --------------------------------------------------------
    def _muat_detail(self):
        """Panel rincian akun beserta tindakan pemeliharaan."""
        data = self._cari_data()
        if not data:
            self.terpilih = None
            self._detail_kosong()
            return

        for anak in self.kartu_detail.winfo_children():
            anak.destroy()

        tubuh = ctk.CTkFrame(self.kartu_detail, fg_color="transparent")
        tubuh.pack(fill="both", expand=True, padx=18, pady=16)

        ctk.CTkLabel(
            tubuh,
            text="Akun #%s" % data["id_user"],
            font=(ui_kit.FONT, 16, "bold"),
            text_color=ui_kit.TEKS,
        ).pack(anchor="w")
        latar, warna = STATUS_WARNA.get(data["role"], (ui_kit.KEPALA_TABEL, ui_kit.REDUP))
        ui_kit.chip(tubuh, data["role"], latar, warna).pack(anchor="w", pady=(4, 10))

        for label, nilai in (
            ("Username", data["username"]),
            ("Nama Lengkap", data["full_name"] or "-"),
            ("Status", "Aktif" if int(data["is_active"] or 0) else "Nonaktif"),
        ):
            ctk.CTkLabel(tubuh, text=label, font=(ui_kit.FONT, 10), text_color=ui_kit.REDUP).pack(
                anchor="w", pady=(8, 0)
            )
            ctk.CTkLabel(
                tubuh,
                text=str(nilai),
                font=(ui_kit.FONT, 12, "bold"),
                text_color=ui_kit.TEKS,
                wraplength=240,
                justify="left",
            ).pack(anchor="w")

        aksi = ctk.CTkFrame(tubuh, fg_color="transparent")
        aksi.pack(side="bottom", fill="x", pady=(12, 0))
        ui_kit.tombol(aksi, "Ubah Profil", self._ubah_profil, jenis="sekunder", lebar=110).pack(
            side="right"
        )
        ui_kit.tombol(
            aksi,
            "Nonaktifkan" if int(data["is_active"] or 0) else "Aktifkan",
            self._toggle_aktif,
            jenis="lembut",
            lebar=110,
        ).pack(side="right", padx=(0, 8))
        ui_kit.tombol(aksi, "Hapus", self._hapus, jenis="bahaya", lebar=90).pack(
            side="left", padx=(0, 8)
        )
        ui_kit.tombol(
            aksi, "Reset Sandi", self._reset_sandi, jenis="sekunder", lebar=110
        ).pack(side="left")

    # --------------------------------------------------------
    def _ubah_profil(self):
        """Mengubah nama lengkap pengguna terpilih."""
        if self.terpilih is None:
            ui_kit.toast(self.app, "Pilih data pengguna yang ingin diubah!", jenis="galat")
            return
        data = self._cari_data()
        if not data:
            return
        baru = ctk.CTkInputDialog(
            title="Ubah Profil",
            text="Nama lengkap pengguna:",
            input_text=data["full_name"] or "",
        ).get_input()
        if not baru:
            return
        ok, pesan = UserController.ubah_profil(self.terpilih, baru)
        ui_kit.toast(self.app, pesan, jenis="sukses" if ok else "galat")
        self.muat()

    def _toggle_aktif(self):
        """Mengaktifkan atau menonaktifkan akun terpilih."""
        if self.terpilih is None:
            ui_kit.toast(self.app, "Pilih data pengguna yang ingin diubah!", jenis="galat")
            return
        data = self._cari_data()
        if not data:
            return
        if self.terpilih == self.app.user.get("id_user"):
            ui_kit.toast(self.app, "Akun yang sedang digunakan tidak dapat dinonaktifkan!", jenis="galat")
            return
        aktif = not int(data["is_active"] or 0)
        ok, pesan = (
            UserController.aktifkan(self.terpilih)
            if aktif
            else UserController.nonaktifkan(self.terpilih)
        )
        ui_kit.toast(self.app, pesan, jenis="sukses" if ok else "galat")
        self.muat()

    def _reset_sandi(self):
        """Menetapkan kata sandi baru untuk pengguna terpilih."""
        if self.terpilih is None:
            ui_kit.toast(self.app, "Pilih data pengguna yang ingin diubah!", jenis="galat")
            return
        baru = ctk.CTkInputDialog(
            title="Reset Kata Sandi",
            text="Kata sandi baru (minimal 6 karakter):",
            input_text="",
        ).get_input()
        if not baru:
            return
        if len(baru) < 6:
            ui_kit.toast(self.app, "Password baru minimal 6 karakter!", jenis="galat")
            return
        data = self._cari_data()
        if not data:
            return
        ok, pesan = UserModel.change_password(
            {"id_user": self.terpilih}, baru, baru, baru
        )
        ui_kit.toast(self.app, pesan, jenis="sukses" if ok else "galat")
        self.muat()

    def _hapus(self):
        """Menghapus akun pengguna terpilih."""
        if self.terpilih is None:
            ui_kit.toast(self.app, "Pilih data pengguna yang ingin dihapus!", jenis="galat")
            return
        if self.terpilih == self.app.user.get("id_user"):
            ui_kit.toast(self.app, "Akun yang sedang digunakan tidak dapat dihapus!", jenis="galat")
            return
        dari = ctk.CTkInputDialog(
            title="Hapus Akun",
            text="Ketik username akun untuk konfirmasi:",
            input_text="",
        ).get_input()
        data = self._cari_data()
        if not data or (dari or "").strip() != data["username"]:
            ui_kit.toast(self.app, "Konfirmasi tidak sesuai, akun tidak dihapus.", jenis="galat")
            return
        ok, pesan = UserController.hapus(self.terpilih)
        ui_kit.toast(self.app, pesan, jenis="sukses" if ok else "galat")
        self.terpilih = None
        self.muat()
