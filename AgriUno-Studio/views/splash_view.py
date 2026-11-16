"""Tampilan splash animasi logo AgriUno (Edisi Studio)."""

import contextlib
import math
import os
import time
import tkinter as tk

import customtkinter as ctk

from config import constants, ui_kit

class SplashView(ctk.CTkFrame):
    """Tampilan pembuka berisi animasi logo AgriUno.

    Animasi memakai 24 frame PNG pra-render sehingga tidak
    memerlukan pemrosesan gambar tambahan saat dijalankan.
    """

    DURASI_MS = 3000
    JEDA_FRAME = 45
    TITIK_ORBIT = 7
    PESAN_STATUS = (
        "Menyiapkan basis data AgriUno...",
        "Memuat konfigurasi aplikasi...",
        "Menyiapkan modul manajemen pertanian...",
        "Memeriksa koneksi basis data...",
        "Selamat datang di AgriUno",
    )

    def __init__(self, master, on_selesai):
        super().__init__(master, fg_color=ui_kit.LATAR)
        self.on_selesai = on_selesai
        self.frames = []
        self.waktu_mulai = time.monotonic()
        self.orbit_angle = 0.0
        self.status_index = 0
        self.selesai = False
        self._after_id = None

        kartu = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color=ui_kit.GARIS,
        )
        kartu.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(
            kartu,
            width=440,
            height=250,
            bg="white",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(pady=(24, 0))

        self.logo_item = self.canvas.create_image(220, 118, image="")
        self.orbit_items = [
            self.canvas.create_oval(0, 0, 0, 0, fill=ui_kit.HIJAU_HOVER, outline="")
            for _ in range(self.TITIK_ORBIT)
        ]

        self.wordmark_label = tk.Label(kartu, bg="white", bd=0)
        self.wordmark_label.pack(pady=(16, 0))
        self._muat_wordmark()

        self.progress = ctk.CTkProgressBar(
            kartu,
            width=340,
            height=8,
            corner_radius=4,
            fg_color=ui_kit.GARIS,
            progress_color=ui_kit.HIJAU,
        )
        self.progress.set(0)
        self.progress.pack(pady=(24, 0))

        self.status_label = ctk.CTkLabel(
            kartu,
            text="Menyiapkan aplikasi...",
            font=(ui_kit.FONT, 11),
            text_color=ui_kit.HIJAU,
        )
        self.status_label.pack(pady=(14, 0))

        ctk.CTkLabel(
            kartu,
            text="Edisi Studio  |  UAS RPL 2026  |  Universitas Tadulako",
            font=(ui_kit.FONT, 9),
            text_color="#9ca3af",
        ).pack(side="bottom", pady=(0, 16))

        self._muat_frames()
        self._after_id = self.after(self.JEDA_FRAME, self._tick)

    # --------------------------------------------------------
    def _muat_frames(self):
        """Memuat frame animasi; emblem tunggal sebagai cadangan."""
        if os.path.isdir(constants.ANIM):
            nama = sorted(
                n for n in os.listdir(constants.ANIM) if n.startswith("frame_") and n.endswith(".png")
            )
            for n in nama:
                with contextlib.suppress(tk.TclError):
                    self.frames.append(tk.PhotoImage(file=os.path.join(constants.ANIM, n)))
        if not self.frames and os.path.exists(constants.LOGO):
            with contextlib.suppress(tk.TclError):
                from PIL import Image

                im = Image.open(constants.LOGO).convert("RGBA")
                self.frames = [im]

    def _muat_wordmark(self):
        """Memuat wordmark AgriUno; teks sebagai cadangan."""
        if not os.path.exists(constants.WORDMARK):
            self.wordmark_label.configure(
                text="AgriUno", font=(ui_kit.FONT, 26, "bold"), fg=ui_kit.HIJAU
            )
            return
        with contextlib.suppress(tk.TclError):
            photo = tk.PhotoImage(file=constants.WORDMARK)
            self.wordmark_label.configure(image=photo)
            self.wordmark_label.image = photo

    # --------------------------------------------------------
    def _tick(self):
        """Satu langkah animasi, dipanggil berkala."""
        if self.selesai:
            return
        lewat = int((time.monotonic() - self.waktu_mulai) * 1000)
        rasio = min(1.0, lewat / float(self.DURASI_MS))
        self.progress.set(rasio)

        if self.frames:
            tahap = min(1.0, rasio / 0.55)
            indeks = min(len(self.frames) - 1, int(tahap * (len(self.frames) - 1)))
            self.canvas.itemconfigure(self.logo_item, image=self.frames[indeks])

        self._gambar_orbit()
        self._perbarui_status()

        if lewat >= self.DURASI_MS:
            self._akhiri()
            return
        self._after_id = self.after(self.JEDA_FRAME, self._tick)

    def _gambar_orbit(self):
        """Titik-titik hijau yang berputar mengelilingi logo."""
        self.orbit_angle = (self.orbit_angle + 6.0) % 360.0
        cx, cy, rx, ry = 220, 118, 195, 104
        for i, item in enumerate(self.orbit_items):
            sudut = math.radians(self.orbit_angle + i * (360.0 / self.TITIK_ORBIT))
            x = cx + rx * math.cos(sudut)
            y = cy + ry * math.sin(sudut)
            dalam = (math.sin(sudut) + 1) / 2.0
            ukuran = 3 + int(3 * dalam)
            warna = _campur(ui_kit.HIJAU, "#ffffff", 0.55 * (1 - dalam))
            self.canvas.coords(item, x - ukuran, y - ukuran, x + ukuran, y + ukuran)
            self.canvas.itemconfigure(item, fill=warna)

    def _perbarui_status(self):
        """Mengganti pesan status seiring kemajuan animasi."""
        lewat = int((time.monotonic() - self.waktu_mulai) * 1000)
        indeks = min(
            len(self.PESAN_STATUS) - 1,
            int(lewat / self.DURASI_MS * len(self.PESAN_STATUS)),
        )
        if indeks != self.status_index:
            self.status_index = indeks
            self.status_label.configure(text=self.PESAN_STATUS[indeks])

    def _akhiri(self):
        """Mengakhiri animasi dan melanjutkan ke layar login."""
        if self.selesai:
            return
        self.selesai = True
        self.progress.set(1.0)
        self.status_label.configure(text="Selamat datang di AgriUno")
        self.update_idletasks()
        self.after(180, self._tutup)

    def _tutup(self):
        callback = self.on_selesai
        with contextlib.suppress(tk.TclError):
            self.destroy()
        if callable(callback):
            callback()

    def destroy(self):
        """Membatalkan animasi bila tampilan ditutup lebih awal."""
        self.selesai = True
        with contextlib.suppress(Exception):
            self.after_cancel(self._after_id)
        with contextlib.suppress(Exception):
            super().destroy()


def _campur(warna_a, warna_b, rasio):
    """Mencampur dua warna hex dengan rasio 0..1."""

    def ke_rgb(nilai):
        nilai = nilai.lstrip("#")
        return tuple(int(nilai[i : i + 2], 16) for i in (0, 2, 4))

    r1, g1, b1 = ke_rgb(warna_a)
    r2, g2, b2 = ke_rgb(warna_b)
    r = int(r1 + (r2 - r1) * rasio)
    g = int(g1 + (g2 - g1) * rasio)
    b = int(b1 + (b2 - b1) * rasio)
    return "#%02x%02x%02x" % (r, g, b)
