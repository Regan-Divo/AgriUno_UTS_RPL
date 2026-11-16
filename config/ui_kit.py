"""
==========================================================
KIT ANTARMUKA - AGRIUNO
==========================================================
Sistem desain bersama untuk seluruh halaman AgriUno: palet
warna, tipografi, kartu, formulir, tombol, dan tabel data.

Tujuannya agar setiap halaman memiliki bahasa visual yang
konsisten - seperti aplikasi profesional pada umumnya -
tanpa mengubah sedikit pun logika bisnis pada controller
maupun model.
"""

import tkinter.font as tkfont

import customtkinter as ctk
from PIL import Image

from config.constants import (
    COLOR_ACCENT,
    COLOR_DANGER,
    COLOR_INFO,
    COLOR_MUTED,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_SURFACE,
)

# ------------------------------------------------------------
# 1. TOKEN DESAIN
# ------------------------------------------------------------
FONT = "Segoe UI"

#: Skala tipografi (pt).
TS_DISPLAY = 26
TS_JUDUL = 21
TS_SEKSI = 14
TS_BADAN = 12
TS_KECIL = 10

#: Warna permukaan tambahan.
WARNA_LATAR = "#eef3ef"  # latar konten (hijau sangat muda)
WARNA_KARTU = COLOR_SURFACE
WARNA_GARIS = "#e2e8e4"  # bingkai kartu halus
WARNA_TEBEL = "#22312a"  # teks utama
WARNA_REDUP = COLOR_MUTED
WARNA_ZEBRA = "#f6f9f7"  # baris tabel genap
WARNA_TERPILIH = "#dcebe2"  # baris tabel terpilih
WARNA_KEPALA_TABEL = "#f0f5f2"

WARNA_HIJAU_MUDA = "#d8f3dc"
WARNA_AMBER_MUDA = "#fef3c7"
WARNA_BIRU_MUDA = "#dbeafe"
WARNA_MERAH_MUDA = "#fee2e2"

CORNER_KARTU = 16
CORNER_TOMBOL = 10
CORNER_INPUT = 8

TINGGI_INPUT = 38
TINGGI_TOMBOL = 38


# ------------------------------------------------------------
# 2. KARTU
# ------------------------------------------------------------
def kartu(parent):
    """Mengembalikan kartu putih bersudut membulat berbingkai halus."""
    return ctk.CTkFrame(
        parent,
        fg_color=WARNA_KARTU,
        corner_radius=CORNER_KARTU,
        border_width=1,
        border_color=WARNA_GARIS,
    )


# ------------------------------------------------------------
# 3. KEPALA HALAMAN
# ------------------------------------------------------------
def judul_halaman(parent, judul, subjudul):
    """Menyusun kepala halaman: judul besar, subjudul, dan aksen."""
    bingkai = ctk.CTkFrame(parent, fg_color="transparent")
    bingkai.pack(fill="x", padx=32, pady=(24, 14))

    garis = ctk.CTkFrame(bingkai, fg_color=COLOR_PRIMARY, corner_radius=2, width=44, height=4)
    garis.pack(anchor="w")
    garis.pack_propagate(False)

    ctk.CTkLabel(
        bingkai,
        text=judul,
        font=(FONT, TS_JUDUL, "bold"),
        text_color=COLOR_PRIMARY,
    ).pack(anchor="w", pady=(8, 1))

    ctk.CTkLabel(
        bingkai,
        text=subjudul,
        font=(FONT, TS_BADAN),
        text_color=WARNA_REDUP,
    ).pack(anchor="w")
    return bingkai


# ------------------------------------------------------------
# 4. BIDANG ISIAN (label di atas input)
# ------------------------------------------------------------
def bidang_isian(parent, label, placeholder="", lebar=250, wajib=True):
    """Membuat kolom isian: label kecil di atas, entry di bawahnya."""
    kolom = ctk.CTkFrame(parent, fg_color="transparent")

    baris_label = ctk.CTkFrame(kolom, fg_color="transparent")
    baris_label.pack(fill="x")
    ctk.CTkLabel(
        baris_label,
        text=label + (" *" if wajib else ""),
        font=(FONT, TS_KECIL + 1, "bold"),
        text_color=WARNA_TEBEL,
    ).pack(side="left")

    entry = ctk.CTkEntry(
        kolom,
        width=lebar,
        height=TINGGI_INPUT,
        placeholder_text=placeholder,
        corner_radius=CORNER_INPUT,
        font=(FONT, TS_BADAN),
        border_color=WARNA_GARIS,
        fg_color="#fbfcfb",
    )
    entry.pack(fill="x", pady=(5, 0))
    return kolom, entry


# ------------------------------------------------------------
# 5. PILIHAN (dropdown gaya terang)
# ------------------------------------------------------------
def pilihan_isian(parent, label, nilai, lebar=250):
    """Membuat kolom pilihan bergaya terang dan konsisten."""
    kolom = ctk.CTkFrame(parent, fg_color="transparent")

    ctk.CTkLabel(
        kolom,
        text=label + " *",
        font=(FONT, TS_KECIL + 1, "bold"),
        text_color=WARNA_TEBEL,
    ).pack(anchor="w")

    menu = ctk.CTkOptionMenu(
        kolom,
        values=nilai,
        width=lebar,
        height=TINGGI_INPUT,
        corner_radius=CORNER_INPUT,
        font=(FONT, TS_BADAN),
        fg_color="#eef4f0",
        button_color=COLOR_PRIMARY,
        button_hover_color=COLOR_PRIMARY_HOVER,
        dropdown_fg_color="white",
        dropdown_hover_color=WARNA_KEPALA_TABEL,
        dropdown_text_color=WARNA_TEBEL,
        dropdown_font=(FONT, TS_BADAN),
        text_color=WARNA_TEBEL,
    )
    menu.pack(fill="x", pady=(5, 0))
    return kolom, menu


# ------------------------------------------------------------
# 6. TOMBOL
# ------------------------------------------------------------
def _tombol(parent, teks, warna, hover, perintah, lebar=118, garis=None, teks_warna="white"):
    return ctk.CTkButton(
        parent,
        text=teks,
        fg_color=warna,
        hover_color=hover,
        text_color=teks_warna,
        width=lebar,
        height=TINGGI_TOMBOL,
        corner_radius=CORNER_TOMBOL,
        font=(FONT, TS_BADAN, "bold"),
        border_width=1 if garis else 0,
        border_color=garis or warna,
        command=perintah,
    )


def tombol_primer(parent, teks, perintah, lebar=118):
    return _tombol(parent, teks, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, perintah, lebar)


def tombol_sekunder(parent, teks, perintah, lebar=118):
    return _tombol(
        parent,
        teks,
        "transparent",
        WARNA_KEPALA_TABEL,
        perintah,
        lebar,
        garis=COLOR_ACCENT,
        teks_warna=COLOR_ACCENT,
    )


def tombol_bahaya(parent, teks, perintah, lebar=118):
    return _tombol(
        parent,
        teks,
        "transparent",
        WARNA_MERAH_MUDA,
        perintah,
        lebar,
        garis=COLOR_DANGER,
        teks_warna=COLOR_DANGER,
    )


def tombol_tumpah(parent, teks, perintah, lebar=150):
    """Tombol mengambang (floating) untuk panel gelap."""
    return _tombol(parent, teks, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, perintah, lebar)


# ------------------------------------------------------------
# 7. TABEL DATA
# ------------------------------------------------------------
def pasang_gaya_tabel():
    """Menyiapkan gaya ttk.Treeview agar terlihat modern."""
    gaya = ctk.ttk.Style() if hasattr(ctk, "ttk") else None
    if gaya is None:
        import tkinter.ttk as ttk

        gaya = ttk.Style()

    try:
        ukuran = tkfont.Font(family=FONT, size=-12).metrics("linespace")
    except Exception:  # noqa: BLE001
        ukuran = 16

    gaya.theme_use("clam")
    gaya.configure(
        "AgriUno.Treeview",
        background="white",
        foreground=WARNA_TEBEL,
        rowheight=max(30, ukuran + 12),
        fieldbackground="white",
        borderwidth=0,
        font=(FONT, TS_BADAN),
    )
    gaya.configure(
        "AgriUno.Treeview.Heading",
        background=WARNA_KEPALA_TABEL,
        foreground=COLOR_PRIMARY,
        font=(FONT, TS_KECIL + 1, "bold"),
        relief="flat",
        padding=(8, 9),
    )
    gaya.map(
        "AgriUno.Treeview.Heading",
        background=[("active", WARNA_ZEBRA)],
    )
    gaya.map(
        "AgriUno.Treeview",
        background=[("selected", WARNA_TERPILIH)],
        foreground=[("selected", WARNA_TEBEL)],
    )
    return gaya


def tabel_data(parent, kolom_lebar, tinggi=13):
    """Membuat Treeview + scrollbar dengan gaya AgriUno.

    ``kolom_lebar`` berupa pasangan (id_kolom, judul, lebar, rata).
    """
    import tkinter.ttk as ttk

    pasang_gaya_tabel()

    wadah = ctk.CTkFrame(parent, fg_color="white", corner_radius=0)

    ids = [k[0] for k in kolom_lebar]
    tree = ttk.Treeview(
        wadah, columns=ids, show="headings", height=tinggi, style="AgriUno.Treeview"
    )

    for id_k, judul_k, lebar, rata in kolom_lebar:
        tree.heading(id_k, text=judul_k, anchor="center")
        tree.column(
            id_k,
            width=lebar,
            anchor=rata,
            stretch=(lebar >= 260),
        )

    # Baris selang-seling dan penanda status.
    tree.tag_configure("genap", background="white")
    tree.tag_configure("ganjil", background=WARNA_ZEBRA)
    tree.tag_configure("terkirim", foreground="#15803d", font=(FONT, TS_BADAN, "bold"))
    tree.tag_configure("diproses", foreground="#b45309")
    tree.tag_configure("pengiriman", foreground=COLOR_INFO)

    gulir = ttk.Scrollbar(wadah, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=gulir.set)

    tree.pack(side="left", fill="both", expand=True)
    gulir.pack(side="right", fill="y")
    return wadah, tree


def tag_zebra(indeks):
    """Mengembalikan nama tag baris selang-seling."""
    return "genap" if indeks % 2 == 0 else "ganjil"


def tag_status(status):
    """Mengembalikan nama tag pewarnaan untuk status pengiriman."""
    if status == "Terkirim":
        return "terkirim"
    if status == "Diproses":
        return "diproses"
    if status == "Dalam Pengiriman":
        return "pengiriman"
    return ""


# ------------------------------------------------------------
# 8. BAGDE / CHIP
# ------------------------------------------------------------
def chip(parent, teks, warna_latar, warna_teks):
    """Label kecil berbentuk pil untuk informasi ringkas."""
    return ctk.CTkLabel(
        parent,
        text=teks,
        font=(FONT, TS_KECIL, "bold"),
        text_color=warna_teks,
        fg_color=warna_latar,
        corner_radius=999,
        height=26,
        padx=12,
    )


def pita_pemberitahuan(parent, teks):
    """Pita peringatan akses baca-saja untuk peran tanpa hak kelola."""
    pita = ctk.CTkFrame(
        parent,
        fg_color=WARNA_AMBER_MUDA,
        corner_radius=CORNER_INPUT,
    )
    ctk.CTkLabel(
        pita,
        text="  " + teks,
        font=(FONT, TS_BADAN),
        text_color="#92400e",
        anchor="w",
    ).pack(fill="x", padx=4, pady=6)
    return pita


# ------------------------------------------------------------
# 9. GAMBAR LOGO (CTkImage)
# ------------------------------------------------------------
def gambar_logo(ukuran):
    """Memuat logo emblem sebagai CTkImage dengan ukuran tertentu."""
    import os

    from config.constants import LOGO_EMBLEM

    if not os.path.exists(LOGO_EMBLEM):
        return None
    im = Image.open(LOGO_EMBLEM).convert("RGBA")
    return ctk.CTkImage(light_image=im, dark_image=im, size=(ukuran, ukuran))
