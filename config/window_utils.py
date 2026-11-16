"""
==========================================================
UTILITAS JENDELA - AGRIUNO
==========================================================
Berisi pembantu yang dipakai bersama oleh seluruh kelas view dan
jendela utama, terutama terkait pengaturan ikon jendela.

Ikon jendela AgriUno memakai berkas ``assets/logo_agriuno.ico``
supaya tidak lagi menampilkan kotak biru bawaan Python pada baris
judul (title bar) maupun pada taskbar.
"""

import logging
import os
import tkinter as tk

from config.constants import LOGO_EMBLEM, LOGO_ICON

logger = logging.getLogger(__name__)


def pasang_ikon(jendela):
    """Menetapkan ikon AgriUno pada sebuah jendela Tk.

    Fungsi ini aman dipanggil pada seluruh jenis jendela dan tidak
    akan menghentikan aplikasi apabila berkas ikon tidak ditemukan
    (misalnya ketika aset belum dibangun).
    """
    # 1) Ikon format .ico untuk title bar dan taskbar Windows.
    if os.path.exists(LOGO_ICON):
        try:
            jendela.iconbitmap(LOGO_ICON)
            return True
        except Exception:  # noqa: BLE001
            logger.debug("Gagal memasang iconbitmap pada %s", LOGO_ICON)

    # 2) Cadangan: gunakan berkas PNG melalui iconphoto.
    if os.path.exists(LOGO_EMBLEM):
        try:
            gambar = tk.PhotoImage(master=jendela, file=LOGO_EMBLEM)
            skala = max(1, int(gambar.width() / 64))
            if skala > 1:
                gambar = gambar.subsample(skala, skala)
            jendela.iconphoto(True, gambar)
            jendela._agriuno_icon = gambar  # jaga agar tidak di-GC
            return True
        except Exception:  # noqa: BLE001
            logger.debug("Gagal memasang iconphoto pada %s", LOGO_EMBLEM)

    return False
