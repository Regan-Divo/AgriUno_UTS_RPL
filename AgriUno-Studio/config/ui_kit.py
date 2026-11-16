"""
Kit antarmuka AgriUno Edisi Studio.

Sistem desain bersama untuk seluruh tampilan: kartu, tipografi,
formulir, tombol, tabel data, kerangka halaman, dialog modal, dan
notifikasi toast. Palet warna diambil dari config.constants.
"""

import contextlib
import os
import tkinter.ttk as ttk

import customtkinter as ctk
from PIL import Image

from config.constants import (
    AMBER,
    AMBER_LEMBUT,
    BIRU,
    BIRU_LEMBUT,
    FONT,
    GARIS,
    HIJAU,
    HIJAU_HOVER,
    HIJAU_LEMBUT,
    HIJAU_TEKS,
    IKON,
    KARTU,
    KEPALA_TABEL,
    LATAR,
    LOGO,
    MERAH,
    MERAH_LEMBUT,
    REDUP,
    STATUS_WARNA,
    TEKS,
    TERPILIH,
    ZEBRA,
)

# ------------------------------------------------------------
# 1. TOKEN DESAIN
# ------------------------------------------------------------
R_KARTU = 18
R_INPUT = 10
T_INPUT = 38


# ------------------------------------------------------------
# 2. KOMPONEN DASAR
# ------------------------------------------------------------
def kartu(parent):
    """Kartu putih bersudut membulat berbingkai halus."""
    return ctk.CTkFrame(
        parent, fg_color=KARTU, corner_radius=R_KARTU, border_width=1, border_color=GARIS
    )


def judul_halaman(parent, judul, subjudul):
    """Kepala halaman: penanda aksen, judul besar, dan subjudul."""
    bingkai = ctk.CTkFrame(parent, fg_color="transparent")
    garis = ctk.CTkFrame(bingkai, fg_color=HIJAU, corner_radius=2, width=44, height=4)
    garis.pack(anchor="w")
    garis.pack_propagate(False)
    ctk.CTkLabel(bingkai, text=judul, font=(FONT, 21, "bold"), text_color=HIJAU).pack(
        anchor="w", pady=(8, 1)
    )
    ctk.CTkLabel(bingkai, text=subjudul, font=(FONT, 12), text_color=REDUP).pack(anchor="w")
    return bingkai


def bidang(parent, label, placeholder="", lebar=300, wajib=True):
    """Kolom isian: label kecil di atas, entry di bawahnya."""
    kolom = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(
        kolom,
        text=label + (" *" if wajib else ""),
        font=(FONT, 11, "bold"),
        text_color=TEKS,
    ).pack(anchor="w")
    entry = ctk.CTkEntry(
        kolom,
        width=lebar,
        height=T_INPUT,
        placeholder_text=placeholder,
        corner_radius=R_INPUT,
        font=(FONT, 12),
        border_color=GARIS,
        fg_color="#fbfcfb",
    )
    entry.pack(fill="x", pady=(5, 0))
    return kolom, entry


def pilihan(parent, label, nilai, lebar=300):
    """Kolom dropdown bergaya terang."""
    kolom = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(kolom, text=label + " *", font=(FONT, 11, "bold"), text_color=TEKS).pack(
        anchor="w"
    )
    menu = ctk.CTkOptionMenu(
        kolom,
        values=nilai or ["-"],
        width=lebar,
        height=T_INPUT,
        corner_radius=R_INPUT,
        font=(FONT, 12),
        fg_color="#eef4f0",
        button_color=HIJAU,
        button_hover_color=HIJAU_HOVER,
        dropdown_fg_color="white",
        dropdown_hover_color=KEPALA_TABEL,
        dropdown_text_color=TEKS,
        dropdown_font=(FONT, 12),
        text_color=TEKS,
    )
    menu.pack(fill="x", pady=(5, 0))
    return kolom, menu


def tombol(parent, teks, perintah, jenis="primer", lebar=120):
    """Tombol dengan hierarki: primer / sekunder / bahaya / lembut."""
    gaya = {
        "primer": (HIJAU, HIJAU_HOVER, "white", 0),
        "sekunder": ("transparent", KEPALA_TABEL, HIJAU, 1),
        "bahaya": ("transparent", MERAH_LEMBUT, MERAH, 1),
        "lembut": (HIJAU_LEMBUT, "#d5e8dc", HIJAU, 0),
    }[jenis]
    fg, hover, teks_warna, garis = gaya
    return ctk.CTkButton(
        parent,
        text=teks,
        fg_color=fg,
        hover_color=hover,
        text_color=teks_warna,
        border_width=garis,
        border_color=HIJAU if jenis == "sekunder" else (MERAH if jenis == "bahaya" else fg),
        width=lebar,
        height=38,
        corner_radius=10,
        font=(FONT, 12, "bold"),
        command=perintah,
    )


def pil_status(status):
    """Teks gaya pil untuk status (dipakai di label detail)."""
    latar, teks = STATUS_WARNA.get(status, (KEPALA_TABEL, REDUP))
    return latar, teks


# ------------------------------------------------------------
# 3. TABEL DATA
# ------------------------------------------------------------
_gaya_terpasang = False


def pasang_gaya_tabel():
    """Menyiapkan gaya ttk.Treeview AgriUno Studio."""
    global _gaya_terpasang
    if _gaya_terpasang:
        return
    gaya = ttk.Style()
    gaya.theme_use("clam")
    gaya.configure(
        "Studio.Treeview",
        background="white",
        foreground=TEKS,
        rowheight=32,
        fieldbackground="white",
        borderwidth=0,
        font=(FONT, 12),
    )
    gaya.configure(
        "Studio.Treeview.Heading",
        background=KEPALA_TABEL,
        foreground=HIJAU,
        font=(FONT, 11, "bold"),
        relief="flat",
        padding=(8, 10),
    )
    gaya.map("Studio.Treeview.Heading", background=[("active", ZEBRA)])
    gaya.map(
        "Studio.Treeview",
        background=[("selected", TERPILIH)],
        foreground=[("selected", TEKS)],
    )
    _gaya_terpasang = True


def tabel(parent, kolom_lebar, tinggi=13):
    """Treeview + scrollbar bergaya Studio.

    ``kolom_lebar`` berupa pasangan (id, judul, lebar, rata).
    Setiap kolom memakai ``lebar`` sebagai ukuran minimum dan sisa
    ruang kartu dibagikan secara proporsional, sehingga tabel selalu
    mengisi penuh lebar halaman tanpa area kosong di kanan.
    """
    pasang_gaya_tabel()
    wadah = ctk.CTkFrame(parent, fg_color="white", corner_radius=0)

    ids = [k[0] for k in kolom_lebar]
    tree = ttk.Treeview(wadah, columns=ids, show="headings", height=tinggi, style="Studio.Treeview")
    for id_k, judul_k, lebar, rata in kolom_lebar:
        tree.heading(id_k, text=judul_k, anchor="center")
        tree.column(
            id_k,
            width=lebar,
            minwidth=lebar,
            anchor=rata,
            # Kolom teks (rata kiri) ikut merenggang mengisi sisa lebar
            # kartu; kolom angka/tanggal tetap padat di posisinya.
            stretch=(rata == "w"),
        )

    tree.tag_configure("genap", background="white")
    tree.tag_configure("ganjil", background=ZEBRA)

    gulir = ttk.Scrollbar(wadah, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=gulir.set)
    tree.pack(side="left", fill="both", expand=True)
    gulir.pack(side="right", fill="y")
    return wadah, tree


def tag_zebra(indeks):
    """Nama tag baris selang-seling."""
    return "genap" if indeks % 2 == 0 else "ganjil"


# ------------------------------------------------------------
# 4. KOMPONEN KECIL
# ------------------------------------------------------------
def chip(parent, teks, warna_latar=KEPALA_TABEL, warna_teks=REDUP):
    """Label pil kecil untuk informasi ringkas."""
    return ctk.CTkLabel(
        parent,
        text=teks,
        font=(FONT, 11, "bold"),
        text_color=warna_teks,
        fg_color=warna_latar,
        corner_radius=999,
        height=26,
        padx=12,
    )


def status_kosong(parent, pesan):
    """Panel keadaan kosong yang ramah."""
    box = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(box, text="◌", font=(FONT, 34), text_color=GARIS).pack(pady=(24, 2))
    ctk.CTkLabel(box, text=pesan, font=(FONT, 12), text_color=REDUP).pack()
    return box


# ------------------------------------------------------------
# 5. TOAST (notifikasi mengambang)
# ------------------------------------------------------------
def toast(jendela, pesan, jenis="sukses", durasi=2600):
    """Menampilkan notifikasi kecil di pojok kanan-bawah jendela."""
    warna = {
        "sukses": (HIJAU_LEMBUT, HIJAU_TEKS),
        "galat": (MERAH_LEMBUT, MERAH),
        "info": (BIRU_LEMBUT, BIRU),
    }[jenis]
    latar, teks = warna
    kotak = ctk.CTkFrame(
        jendela,
        fg_color=latar,
        corner_radius=12,
        border_width=1,
        border_color=teks,
    )
    kotak.place(relx=0.995, rely=0.985, anchor="se", x=-8, y=-8)

    ikon = {"sukses": "✓", "galat": "!", "info": "i"}[jenis]
    ctk.CTkLabel(
        kotak,
        text="%s  %s" % (ikon, pesan),
        font=(FONT, 12),
        text_color=teks,
        justify="left",
        wraplength=360,
    ).pack(padx=14, pady=10)

    jendela.after(durasi, lambda: kotak.winfo_exists() and kotak.destroy())


# ------------------------------------------------------------
# 6. LOGO
# ------------------------------------------------------------
def gambar_logo(ukuran):
    """Memuat logo sebagai CTkImage bila berkas tersedia."""
    if not os.path.exists(LOGO):
        return None
    from PIL import Image

    im = Image.open(LOGO).convert("RGBA")
    return ctk.CTkImage(light_image=im, dark_image=im, size=(ukuran, ukuran))


# ------------------------------------------------------------
# 7. DIALOG MODAL
# ------------------------------------------------------------
class DialogModal(ctk.CTkToplevel):
    """Dasar jendela dialog modal yang terpusat di jendela induk."""

    def __init__(self, master, judul, lebar=520):
        super().__init__(master)
        self.title(judul)
        self.configure(fg_color="white")
        self.transient(master)
        self.resizable(False, False)
        self.grab_set()
        if os.path.exists(IKON):
            with contextlib.suppress(Exception):
                self.iconbitmap(IKON)
        # Pemusatan ditunda hingga seluruh isi dialog tersusun, agar
        # tinggi yang dihitung sesuai ukuran akhir jendela.
        self.after(60, lambda: self._pusatkan(lebar))

    def _pusatkan(self, lebar):
        """Menempatkan dialog di tengah jendela induk."""
        # Dialog berukuran otomatis mengikuti isinya; kita hanya
        # memusatkan posisinya terhadap jendela induk.
        self.update_idletasks()
        induk = self.master
        lebar_k = self.winfo_reqwidth()
        tinggi_k = self.winfo_reqheight()
        x = induk.winfo_rootx() + max(0, (induk.winfo_width() - lebar_k) // 2)
        y = induk.winfo_rooty() + max(0, (induk.winfo_height() - tinggi_k) // 3)
        self.geometry("+%d+%d" % (x, y))

    def _baris_aksi(self, parent, teks_ok, perintah):
        """Baris tombol aksi dialog: Batal + Simpan."""
        baris = ctk.CTkFrame(parent, fg_color="transparent")
        baris.pack(fill="x", pady=(18, 0))
        tombol(baris, "Batal", self.destroy, jenis="sekunder", lebar=120).pack(side="right")
        tombol(baris, teks_ok, perintah, jenis="primer", lebar=140).pack(
            side="right", padx=(0, 10)
        )