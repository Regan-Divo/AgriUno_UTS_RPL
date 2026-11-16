"""
==========================================================
PENJAGA DIAGRAM AGRIUNO (UAS RPL 2026)
==========================================================
Titik masuk untuk membangkitkan seluruh diagram AgriUno beserta
ekspor PNG-nya.

Jalankan::

    python tools/generate_diagrams.py                 # hanya .drawio
    python tools/generate_diagrams.py --export-png    # .drawio + PNG

Ekspor PNG memerlukan draw.io desktop (dapat diunduh pada
https://www.drawio.com) dan dijalankan melalui baris perintah::

    draw.io --export --format png --scale 2 --output <tujuan> <sumber>
"""

import argparse
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from diagrams_desain import (  # noqa: E402
    diagram_arsitektur,
    diagram_class,
    diagram_erd,
    diagram_navigasi,
)
from diagrams_dfd import (  # noqa: E402
    diagram_dfd_l2_autentikasi,
    diagram_dfd_l2_distribusi,
    diagram_dfd_l2_panen,
    diagram_dfd_l2_petani,
    diagram_dfd_level1,
    diagram_konteks,
)
from diagrams_uml import (  # noqa: E402
    diagram_activity,
    diagram_activity_splash,
    diagram_seq_distribusi,
    diagram_seq_login,
    diagram_seq_panen,
    diagram_seq_petani,
    diagram_seq_registrasi,
    diagram_use_case,
)

#: Folder keluaran diagram.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "docs", "diagrams")

#: Kandidat lokasi draw.io desktop pada Windows.
DRAWIO_CANDIDATES = [
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "draw.io", "draw.io.exe"),
    r"C:\Program Files\draw.io\draw.io.exe",
    r"C:\Program Files (x86)\draw.io\draw.io.exe",
    shutil.which("drawio") or "",
    shutil.which("draw.io") or "",
]


def daftar_diagram():
    """Mengembalikan daftar (nama berkas, fungsi pembangun)."""
    return [
        ("03_Diagram_Konteks", diagram_konteks),
        ("03_DFD_Level_1", diagram_dfd_level1),
        ("03_DFD_L2_Proses_1_0", diagram_dfd_l2_autentikasi),
        ("03_DFD_L2_Proses_2_0", diagram_dfd_l2_petani),
        ("03_DFD_L2_Proses_3_0", diagram_dfd_l2_panen),
        ("03_DFD_L2_Proses_4_0", diagram_dfd_l2_distribusi),
        ("04_Use_Case_Diagram", diagram_use_case),
        ("04_Sequence_Diagram_UC-01_Login", diagram_seq_login),
        ("04_Sequence_Diagram_UC-03_Petani", diagram_seq_petani),
        ("04_Sequence_Diagram_UC-04_Panen", diagram_seq_panen),
        ("04_Sequence_Diagram_UC-05_Distribusi", diagram_seq_distribusi),
        ("04_Sequence_Diagram_UC-08_Registrasi", diagram_seq_registrasi),
        ("04_Activity_Diagram", diagram_activity),
        ("04_Activity_Diagram_Splash", diagram_activity_splash),
        ("04_Class_Diagram", diagram_class),
        ("05_Entity_Relationship_Diagram", diagram_erd),
        ("06_Arsitektur_Sistem", diagram_arsitektur),
        ("06_Diagram_Navigasi", diagram_navigasi),
    ]


def cari_drawio():
    """Menemukan berkas eksekusi draw.io desktop."""
    for path in DRAWIO_CANDIDATES:
        if path and os.path.exists(path):
            return path
    return None


def ekspor_png(drawio, sumber, tujuan, skala=2):
    """Mengekspor berkas .drawio menjadi PNG menggunakan draw.io."""
    perintah = [
        drawio,
        "--no-sandbox",
        "--export",
        "--format",
        "png",
        "--scale",
        str(skala),
        "--border",
        "10",
        "--output",
        tujuan,
        sumber,
    ]
    try:
        subprocess.run(
            perintah, check=True, timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return os.path.exists(tujuan)
    except (subprocess.SubprocessError, OSError) as exc:
        print("   ! gagal mengekspor %s: %s" % (os.path.basename(sumber), exc))
        return False


def main():
    """Titik masuk skrip."""
    parser = argparse.ArgumentParser(description="Pembangun diagram AgriUno")
    parser.add_argument(
        "--export-png", action="store_true", help="ekspor PNG menggunakan draw.io desktop"
    )
    parser.add_argument("--scale", type=int, default=2, help="skala ekspor PNG (default: 2)")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    print("Membangkitkan diagram AgriUno ke folder: %s\n" % OUT_DIR)

    paths = []
    for nama, builder in daftar_diagram():
        diagram = builder()
        path = os.path.join(OUT_DIR, nama + ".drawio")
        diagram.save(path)
        paths.append(path)
        print("  [OK] %s.drawio" % nama)

    print("\nTotal %d diagram dibangkitkan." % len(paths))

    if not args.export_png:
        print("\nGunakan '--export-png' untuk sekaligus membuat berkas PNG.")
        return 0

    drawio = cari_drawio()
    if not drawio:
        print("\n! draw.io desktop tidak ditemukan. Ekspor PNG dilewati.")
        print("  Unduh dari https://www.drawio.com lalu jalankan ulang.")
        return 1

    print("\nMengekspor PNG menggunakan: %s\n" % drawio)
    gagal = 0
    for path in paths:
        png = path[: -len(".drawio")] + ".png"
        if ekspor_png(drawio, path, png, args.scale):
            print("  [OK] %s.png" % os.path.basename(path[: -len(".drawio")]))
        else:
            gagal += 1

    print("\nEkspor selesai. %d diagram gagal diekspor." % gagal)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
