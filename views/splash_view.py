"""
==========================================================
LAPIS PEMUATAN (SPLASH SCREEN) - AGRIUNO
==========================================================
Jendela pembuka aplikasi AgriUno.

Sesuai ketentuan UAS Praktikum RPL 2026, aplikasi wajib memiliki
logo dan animasi saat dibuka. Jendela ini menampilkan:

1. **Logo AgriUno** yang muncul secara bertahap melalui 24 frame
   PNG pra-render (skala dan opasitas menaik) sehingga aplikasi
   tidak memerlukan Pillow saat dijalankan.
2. **Cincin orbit** berupa titik-titik hijau yang berputar mengelilingi
   logo, digambar secara vektor langsung pada ``tkinter.Canvas``.
3. **Progress bar** yang menunjukkan kemajuan proses pemuatan.
4. **Pesan status** yang bergantian seiring proses persiapan.

Setelah animasi selesai, jendela splash ditutup secara otomatis dan
fungsi ``on_finish`` dipanggil untuk membuka jendela login.
"""

import contextlib
import logging
import math
import os
import time
import tkinter as tk

import customtkinter as ctk

from config.constants import (
    ANIM_DIR,
    APP_NAME,
    APP_RELEASE,
    APP_VERSION,
    COLOR_BORDER,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_SURFACE,
    LOGO_EMBLEM,
    LOGO_WORDMARK_SMALL,
    WIN_SPLASH,
)
from config.window_utils import pasang_ikon

#: Warna latar splash dan kartu.
BG_SPLASH = "#eef3ef"
CARD_BG = COLOR_SURFACE

#: Durasi animasi dalam milidetik.
DURATION_MS = 3000

#: Jeda antarspine frame logo (ms).
FRAME_INTERVAL = 45

#: Jumlah titik pada cincin orbit.
ORBIT_DOTS = 7

logger = logging.getLogger(__name__)


class SplashView(ctk.CTk):
    """Jendela pemuatan AgriUno dengan animasi logo."""

    def __init__(self, on_finish=None, duration_ms=DURATION_MS):
        super().__init__()
        self.on_finish = on_finish
        self.duration_ms = duration_ms

        self.title("%s - Memuat" % APP_NAME)
        self.configure(fg_color=BG_SPLASH)
        self.resizable(False, False)
        pasang_ikon(self)

        # Hilangkan bingkai jendela supaya tampil seperti splash screen.
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        width, height = WIN_SPLASH
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        # --------------------------------------------------------
        # State animasi
        # --------------------------------------------------------
        self.frames = []
        self.frame_index = 0
        self.elapsed = 0
        self._start_time = time.monotonic()
        self.orbit_angle = 0.0
        self.status_index = 0
        self._finished = False
        self._after_id = None

        self._build_ui()
        self._load_frames()

        self._after_id = self.after(FRAME_INTERVAL, self._tick)
        self.after(60, self.lift)

    # ========================================================
    # Menyusun antarmuka splash
    # ========================================================
    def _build_ui(self):
        """Menyusun elemen antarmuka splash."""
        card = ctk.CTkFrame(
            self,
            fg_color=CARD_BG,
            corner_radius=20,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        card.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Kanvas animasi logo ---
        self.canvas = tk.Canvas(
            card,
            width=440,
            height=250,
            bg=CARD_BG,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(pady=(24, 0))

        self.logo_item = self.canvas.create_image(220, 118, image="")
        self.orbit_items = []
        for _ in range(ORBIT_DOTS):
            oval = self.canvas.create_oval(0, 0, 0, 0, fill=COLOR_PRIMARY_HOVER, outline="")
            self.orbit_items.append(oval)

        # --- Wordmark AgriUno (sudah memuat tagline pada gambarnya) ---
        self.wordmark_label = tk.Label(card, bg=CARD_BG, bd=0)
        self.wordmark_label.pack(pady=(16, 0))
        self._load_wordmark()

        # --- Progress bar ---
        self.progress = ctk.CTkProgressBar(
            card,
            width=340,
            height=8,
            corner_radius=4,
            fg_color="#e5e7eb",
            progress_color=COLOR_PRIMARY,
        )
        self.progress.pack(pady=(24, 0))
        self.progress.set(0)

        # --- Pesan status ---
        self.status_label = ctk.CTkLabel(
            card,
            text="Menyiapkan aplikasi...",
            font=("Arial", 11),
            text_color=COLOR_PRIMARY,
        )
        self.status_label.pack(pady=(14, 0))

        # --- Footer versi ---
        ctk.CTkLabel(
            card,
            text="Versi %s  |  %s" % (APP_VERSION, APP_RELEASE),
            font=("Arial", 9),
            text_color="#9ca3af",
        ).pack(side="bottom", pady=(0, 16))

    # ========================================================
    # Pemuatan aset
    # ========================================================
    def _load_frames(self):
        """Memuat frame animasi logo (PNG pra-render)."""
        if not os.path.isdir(ANIM_DIR):
            return
        names = sorted(
            n for n in os.listdir(ANIM_DIR) if n.startswith("frame_") and n.endswith(".png")
        )
        for name in names:
            try:
                self.frames.append(tk.PhotoImage(file=os.path.join(ANIM_DIR, name)))
            except tk.TclError:
                continue

        # Bila frame animasi tidak tersedia, gunakan emblem tunggal
        # sebagai fallback supaya jendela splash tetap tampil.
        if not self.frames and os.path.exists(LOGO_EMBLEM):
            try:
                photo = tk.PhotoImage(master=self.canvas, file=LOGO_EMBLEM)
                self.frames = [photo]
            except tk.TclError:
                pass

    def _load_wordmark(self):
        """Memuat berkas wordmark AgriUno ke dalam label."""
        if not os.path.exists(LOGO_WORDMARK_SMALL):
            self.wordmark_label.configure(
                text=APP_NAME,
                font=("Arial", 26, "bold"),
                fg=COLOR_PRIMARY,
            )
            return
        try:
            photo = tk.PhotoImage(master=self.wordmark_label, file=LOGO_WORDMARK_SMALL)
        except tk.TclError:
            self.wordmark_label.configure(
                text=APP_NAME,
                font=("Arial", 26, "bold"),
                fg=COLOR_PRIMARY,
            )
            return

        self.wordmark_label.configure(image=photo)
        self.wordmark_label.image = photo  # cegah garbage collection

    # ========================================================
    # Loop animasi
    # ========================================================
    def _tick(self):
        """Satu langkah animasi; dipanggil berkala oleh ``after``."""
        if self._finished:
            return

        # Kemajuan dihitung dari waktu nyata, bukan jumlah frame, sehingga
        # durasi animasi tetap tepat 3 detik walaupun komputer sedang
        # sibuk atau aplikasi dijalankan dari berkas .exe.
        self.elapsed = int((time.monotonic() - self._start_time) * 1000)

        # 1) Progress bar 0..100
        ratio = min(1.0, self.elapsed / float(self.duration_ms))
        self.progress.set(ratio)

        # 2) Frame logo: seluruh frame diputar pada 55% durasi awal.
        if self.frames:
            tahap = min(1.0, (self.elapsed / float(self.duration_ms)) / 0.55)
            self.frame_index = min(len(self.frames) - 1, int(tahap * (len(self.frames) - 1)))
            self.canvas.itemconfigure(self.logo_item, image=self.frames[self.frame_index])

        # 3) Cincin orbit
        self._draw_orbit()

        # 4) Pesan status
        self._update_status()

        # 5) Selesai?
        if self.elapsed >= self.duration_ms:
            self._finish()
            return

        self._after_id = self.after(FRAME_INTERVAL, self._tick)

    # ------------------------------------------------------------
    def _draw_orbit(self):
        """Menggambar titik-titik cincin orbit yang berputar."""
        self.orbit_angle = (self.orbit_angle + 6.0) % 360.0
        cx, cy = 220, 118
        rx, ry = 195, 104

        for i, item in enumerate(self.orbit_items):
            angle = math.radians(self.orbit_angle + i * (360.0 / ORBIT_DOTS))
            x = cx + rx * math.cos(angle)
            y = cy + ry * math.sin(angle)

            # Ukuran titik mengecil seiring posisi (efek kedalaman).
            depth = (math.sin(angle) + 1) / 2.0
            size = 3 + int(3 * depth)
            shade = _blend(COLOR_PRIMARY, "#ffffff", 0.55 * (1 - depth))
            self.canvas.coords(item, x - size, y - size, x + size, y + size)
            self.canvas.itemconfigure(item, fill=shade)

    # ------------------------------------------------------------
    def _update_status(self):
        """Memperbarui pesan status sesuai kemajuan animasi."""
        statuses = [
            "Menyiapkan basis data AgriUno...",
            "Memuat konfigurasi aplikasi...",
            "Menyiapkan modul manajemen pertanian...",
            "Memverifikasi koneksi MySQL...",
            "Selamat datang di AgriUno",
        ]
        index = min(len(statuses) - 1, int(self.elapsed / self.duration_ms * len(statuses)))
        if index != self.status_index:
            self.status_index = index
            self.status_label.configure(text=statuses[index])

    # ------------------------------------------------------------
    def _finish(self):
        """Menyelesaikan animasi dan menutup jendela splash.

        Jendela baru ditutup terlebih dahulu, baru callback
        ``on_finish`` dijalankan. Urutan ini penting karena
        ``self.destroy()`` menghapus default root window Tkinter,
        sehingga pemanggilan ``after`` setelah penghancuran akan
        menyebabkan galat.
        """
        if self._finished:
            return
        self._finished = True
        self.progress.set(1.0)
        self.status_label.configure(text="Selamat datang di AgriUno")
        self.update_idletasks()

        # Tutup jendela pada siklus event berikutnya agar frame
        # terakhir sempat tergambar.
        with contextlib.suppress(tk.TclError):
            self.after(180, self._close)
            return
        self._close()

    # ------------------------------------------------------------
    def _close(self):
        """Menghancurkan jendela splash lalu menjalankan callback."""
        callback = self.on_finish
        with contextlib.suppress(tk.TclError):
            self.destroy()

        if callable(callback):
            try:
                callback()
            except Exception as exc:  # noqa: BLE001
                logger.error("Galat pada callback splash: %s", exc)

    # ========================================================
    # Utilitas
    # ========================================================
    def skip(self):
        """Membatalkan animasi dan langsung membuka jendela berikutnya."""
        self._finish()

    # ------------------------------------------------------------
    def destroy(self):
        """Menutup jendela dengan aman.

        Penutupan manual (misalnya pengguna menekan tombol X)
        membatalkan animasi yang masih berjalan agar tidak terjadi
        galat "invalid command name" pada callback ``after``.
        """
        self._finished = True
        with contextlib.suppress(Exception):
            self.after_cancel(self._after_id)
        with contextlib.suppress(Exception):
            super().destroy()


# ------------------------------------------------------------
# Helper matematika sederhana
# ------------------------------------------------------------
def _blend(color_a, color_b, ratio):
    """Mencampur dua warna hex dengan rasio 0..1."""

    def to_rgb(value):
        value = value.lstrip("#")
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))

    r1, g1, b1 = to_rgb(color_a)
    r2, g2, b2 = to_rgb(color_b)
    r = int(r1 + (r2 - r1) * ratio)
    g = int(g1 + (g2 - g1) * ratio)
    b = int(b1 + (b2 - b1) * ratio)
    return "#%02x%02x%02x" % (r, g, b)
