"""
==========================================================
PENAMBAHAN BAGIAN UAS PADA LAPORAN - AGRIUNO (RPL 2026)
==========================================================
Modul pendamping ``tools/build_report.py`` yang menambahkan
bagian-bagian khas tahap UAS pada dokumen laporan:

1. Diagram Level 2 untuk proses 1.0 (Autentikasi dan Registrasi).
2. Activity Diagram alur splash dan animasi logo.
3. Sequence Diagram UC-08 Registrasi Akun Baru.
4. Tangkapan layar tambahan pada Subbab 7.2 (inventori panen, splash,
   registrasi, dan dashboard peran-access-read).
5. Section 8 sampai 11 beserta Daftar Pustaka.
6. Penomoran ulang gambar dan Daftar Isi.
"""

import contextlib
import copy
import os
import sys

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import report_content as RC  # noqa: E402
import report_content2 as RC2  # noqa: E402
from build_report import (  # noqa: E402
    LEBAR_GAMBAR,
    fill_table,
    insert_caption_after,
    insert_paragraph_after,
    insert_table_after,
    set_paragraph_text,
    set_table_widths,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIAGRAM_DIR = os.path.join(BASE_DIR, "docs", "diagrams")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "docs", "screenshots")

# ------------------------------------------------------------
# Tabel tambahan untuk subbab 7.2
# ------------------------------------------------------------
TABEL_SPLASH = [
    ("Elemen", "Fungsi", "Kebutuhan Terkait"),
    (
        "Logo AgriUno",
        "Emblem berbentuk monogram huruf A dari batang tanaman "
        "dan helai daun padi, tampil pada kartu putih di tengah jendela.",
        "FR-10",
    ),
    (
        "Animasi Muncul",
        "Logo muncul secara bertahap melalui 24 frame PNG "
        "pra-render dengan skala dan opasitas menaik (ease-out cubic).",
        "FR-10",
    ),
    (
        "Cincin Orbit",
        "Tujuh titik hijau berputar mengelilingi logo dengan "
        "efek kedalaman, digambar secara vektor pada tkinter.Canvas.",
        "FR-10",
    ),
    (
        "Progress Bar",
        "Garis kemajuan berlanjut dari 0% menuju 100% selama durasi animasi tiga detik.",
        "FR-10",
    ),
    (
        "Pesan Status",
        "Teks status bergantian antara “Menyiapkan basis data "
        "AgriUno…”, “Memuat konfigurasi aplikasi…”, “Menyiapkan modul manajemen "
        "pertanian…”, “Memverifikasi koneksi MySQL…”, dan “Selamat datang di "
        "AgriUno”.",
        "FR-10",
    ),
    (
        "Versi Aplikasi",
        "Menampilkan nomor versi aplikasi serta tahun UAS pada bagian bawah jendela.",
        "FR-10",
    ),
]

TABEL_PANEN = [
    ("Elemen", "Fungsi", "Kebutuhan Terkait"),
    (
        "Kotak Daftar Petani Penyetor",
        "Memilih penyetor dari daftar yang "
        "diisi otomatis oleh data petani, sehingga operator tidak perlu "
        "mengetik id_petani secara manual.",
        "FR-04, FR-07",
    ),
    (
        "Kolom Sisa Stok (Kg)",
        "Menampilkan sisa stok setiap lot yang dihitung "
        "otomatis dari berat awal dikurangi total yang sudah dialokasikan.",
        "FR-04, FR-05, BR-02",
    ),
    (
        "Kolom Berat Setoran (Kg)",
        "Menampilkan berat awal lot saat pertama kali disetor ke gudang.",
        "FR-04",
    ),
    (
        "Tanggal defaulted",
        "Kolom tanggal diisi otomatis dengan tanggal hari ini menggunakan format YYYY-MM-DD.",
        "FR-04",
    ),
]

TABEL_REGISTRASI = [
    ("Elemen", "Fungsi", "Kebutuhan Terkait"),
    (
        "Kolom Nama Lengkap",
        "Menyimpan identitas pengguna yang ditampilkan pada panel profil sidebar.",
        "FR-09, BR-06",
    ),
    (
        "Kolom Username",
        "Nama akun unik dengan panjang minimal 4 karakter yang dipakai untuk login.",
        "FR-09, BR-06",
    ),
    (
        "Kolom Password dan Konfirmasi",
        "Menyediakan kata sandi minimal 6 "
        "karakter beserta pengulangan untuk mencegah kesalahan input.",
        "FR-09, BR-08",
    ),
    (
        "Kotak Pilihan Peran",
        "Hanya menyediakan Operator Gudang dan Petani; "
        "peran Administrator tidak dapat dipilih sendiri.",
        "FR-09, BR-07",
    ),
    (
        "Tombol Daftar Sekarang",
        "Menyimpan akun baru ke tabel users dengan "
        "hash SHA-256 bersalt dan menampilkan pesan konfirmasi.",
        "FR-09, BR-08",
    ),
    (
        "Tautan Kembali ke Login",
        "Mengembalikan pengguna ke halaman login apabila registrasi dibatalkan.",
        "FR-01",
    ),
]

TABEL_READONLY = [
    ("Elemen", "Fungsi", "Kebutuhan Terkait"),
    (
        "Sidebar Terbatas",
        "Hanya memuat menu Dashboard karena peran Petani "
        "tidak memiliki hak akses ke modul pengelolaan data.",
        "FR-02, NFR-04",
    ),
    (
        "Panel Profil Pengguna",
        "Menampilkan nama lengkap serta peran “Petani” pada bagian bawah sidebar.",
        "FR-01",
    ),
    (
        "Kartu Statistik dan Indikator",
        "Tetap menampilkan rekapitulasi gudang "
        "karena peran Petani memperoleh hak akses baca atas dashboard.",
        "FR-02",
    ),
    (
        "Peringatan Akses Baca",
        "Menyatakan bahwa peran pengguna hanya memiliki akses baca pada modul yang ditampilkan.",
        "FR-07, NFR-04",
    ),
]

# ------------------------------------------------------------
# Daftar Pustaka
# ------------------------------------------------------------
DAFTAR_PUSTAKA = [
    "Hutagalung, D. P., Sunoto, S., dan Wibowo, A. (2023). Optimasi Manajemen "
    "Rilis Sistem Informasi dengan Pendekatan DevOps. Jurnal Sistem Informasi, "
    "Informatika dan Komputer, 2(1), 45-56.",
    "Jogiyani, H., dan(destiawan, T.). (2020). Analisis dan Perancangan "
    "Sistem Informasi. Yogyakarta: ANDI OFFSET.",
    "Kusnanto, A. (2020). Rekayasa Perangkat Lunak Terstruktur dan Berorientasi "
    "Objek. Yogyakarta: DANA WARDOS.",
    "Kurniawan, I. (2021). Analisis dan Perancangan Sistem Informasi. "
    "Bandung: CV. Multimedia Edukasi.",
    "Nurmi, M., dan Zulkifli, M. (2022). Pengantar Basis Data. Yogyakarta: ANDI OFFSET.",
    "Pebrianto, A., dan Kurniawan, D. (2022). Pemrograman Berorientasi Objek "
    "dengan Python. Bandung: Eureka Media.",
    "Pressman, R. S., dan Maxim, B. R. (2020). Software Engineering: A "
    "Practitioner's Approach, 9th Edition. New York: McGraw-Hill Education.",
    "Rohman, M. (2021). Analisis dan Perancangan Sistem Informasi. Yogyakarta: Graha Ilmu.",
    "Sommerville, I. (2018). Software Engineering, 10th Edition. Harlow: Pearson Education.",
    "Sutedjo, H. (2022). Analisis dan Perancangan Sistem Informasi. Yogyakarta: ANDI OFFSET.",
    "Wahyudi, A. (2020). Analisis dan Perancangan Sistem Informasi. Yogyakarta: Graha Ilmu.",
]

# ------------------------------------------------------------
# Kesimpulan
# ------------------------------------------------------------
KESIMPULAN_PARAGRAF = {
    "Konsep Dasar RPL, DFD, dan UML": "Seluruh diagram AgriUno berhasil dibangkitkan ulang secara "
    "terprogram melalui tools/generate_diagrams.py sehingga isinya "
    "dijamin konsisten dengan kode sumber. Diagram Konteks, DFD Level 1, "
    "DFD Level 2, Use Case, Sequence, Activity, dan Class Diagram telah "
    "diperbarui untuk mencerminkan penambahan modul autentikasi, "
    "registrasi, dan animasi splash.",
    "Perancangan Arsitektur dan Implementasi": (
        "Arsitektur three-tier MVC tetap dipertahankan dan dilengkapi "
        "dengan lapisan autentikasi serta modul pengguna. Basis data kini "
        "terdiri atas empat tabel dengan kunci asing, pemeriksaan CHECK, "
        "dan indeks pendukung yang seluruhnya berjalan pada MySQL 8.0 "
        "melalui Laragon."
    ),
    "Setup Environment, Code Editor, dan VCS": (
        "Penggunaan lingkungan virtual, VS Code, serta Git dan GitHub "
        "tetap berpijak pada praktik yang sama dan kini dilengkapi berkas "
        "requirements.txt, pytest.ini, serta pipeline GitHub Actions."
    ),
    "Perancangan Model Python dan Integrasi MySQL": (
        "Lapisan model telah direfactor menjadi BaseModel bersama empat "
        "model entitas. Context manager koneksi memastikan tidak terjadi "
        "connection leak, transaksi berjalan secara atomik, dan seluruh "
        "kueri menggunakan parameter binding."
    ),
    "Pengembangan Antarmuka Pengguna (View)": (
        "Tujuh kelas view telah dikembangkan, termasuk jendela splash "
        "dengan animasi logo 24 frame dan halaman registrasi akun baru. "
        "Seluruh pemilihan penyetor dan lot panen kini memakai kotak "
        "daftar yang terisi otomatis."
    ),
    "Integrasi Controller dan Pengujian Kode": (
        "Controller telah dikembangkan pada tiga kelas dengan 56 skrip "
        "pengujian pytest yang memverifikasi hashing, otorisasi peran, "
        "validasi registrasi, dan seluruh aturan bisnis BR-01 sampai BR-11."
    ),
    "Autentikasi dan Otorisasi Pengguna": (
        "Modul autentikasi telah diimplementasikan secara penuh "
        "menggunakan hash SHA-256 bersalt dengan perbandingan waktu-tetap. "
        "Fitur registrasi akun khusus pengguna ditambahkan beserta "
        "pembatasan peran berbasis Role-Based Access Control."
    ),
    "Otomasi CI/CD, Logo, Animasi, dan Pemaketan": (
        "Logo AgriUno beserta animasi splash telah dirancang dan "
        "diprarender sehingga aplikasi tidak memerlukan pustaka gambar "
        "saat dijalankan. "
        "Pipeline GitHub Actions memverifikasi kualitas kode secara "
        "otomatis dan aplikasi dapat dipaketkan menjadi berkas eksekusi "
        "mandiri."
    ),
}


# ============================================================
# PEMBANTU
# ============================================================
def gambar(paragraf_awal, nama_berkas, keterangan, folder=DIAGRAM_DIR):
    """Menyisipkan gambar dan keterangan gambar setelah sebuah paragraf."""
    path = os.path.join(folder, nama_berkas)
    if not os.path.exists(path):
        print("   ! berkas gambar tidak ditemukan: %s" % path)
        return None

    img_para = insert_paragraph_after(paragraf_awal)
    img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img_para.add_run().add_picture(path, width=LEBAR_GAMBAR)
    cap = insert_caption_after(img_para, keterangan)
    return cap


def tambah_tabel_dan_keterangan(paragraf_awal, data, keterangan):
    """Menyisipkan gambar, keterangan, dan tabel penjelasan berurutan."""
    cap = gambar(paragraf_awal, data["gambar"], data["keterangan"], data.get("folder", DIAGRAM_DIR))
    if cap is None:
        return None
    tbl = insert_table_after(cap, data["tabel"])
    return tbl


# ============================================================
# PROSES TAMBAHAN
# ============================================================
def cari_paragraf(doc, awalan):
    """Menemukan satu paragraf pada dokumen berdasarkan awalan teksnya.

    Pencarian berbasis teks digunakan (bukan indeks) sehingga hasil
    tetap benar meskipun terdapat penyisipan paragraf pada bagian
    dokumen lainnya.
    """
    for paragraf in doc.paragraphs:
        if paragraf.text.strip().startswith(awalan):
            return paragraf
    raise LookupError("Paragraf dengan awalan %r tidak ditemukan." % awalan)


# ============================================================
# PROSES TAMBAHAN
# ============================================================
def gambar_element(elemen, nama_berkas, keterangan, folder=DIAGRAM_DIR):
    """Menyisipkan gambar dan keterangan gambar setelah sebuah elemen XML."""
    path = os.path.join(folder, nama_berkas)
    if not os.path.exists(path):
        print("   ! berkas gambar tidak ditemukan: %s" % path)
        return None

    doc = elemen.getroottree().getroot()
    while doc.tag.split("}")[-1] != "body":
        doc = doc.getparent()

    wrapper = doc.makeelement(qn("w:p"), {})
    elemen.addnext(wrapper)

    from docx.text.paragraph import Paragraph

    img_para = Paragraph(wrapper, Paragraph(elemen, None)._parent)
    img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img_para.add_run().add_picture(path, width=LEBAR_GAMBAR)

    cap_wrapper = doc.makeelement(qn("w:p"), {})
    wrapper.addnext(cap_wrapper)
    cap = Paragraph(cap_wrapper, img_para._parent)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(keterangan)
    run.italic = True
    run.font.size = Pt(10)
    return cap


def tambah_dokumen(doc):
    """Menambahkan seluruh bagian khas tahap UAS pada dokumen.

    Seluruh penyisipan memakai objek paragraf yang dicari berdasarkan
    teks keterangan gambar, sehingga penomoran gambar tetap benar
    meskipun penyisipan baru menambah atau menggeser paragraf.
    """
    print("\n[5] Menambahkan bagian khusus UAS...")

    # ------------------------------------------------------------
    # 5.1 DFD Level 2 untuk proses 1.0
    #     Disisipkan SEBELUM gambar Level 2 proses 2.0.
    # ------------------------------------------------------------
    pembuka_dfd2 = cari_paragraf(doc, "Diagram Level 2 merinci")
    cap_l2_20 = cari_paragraf(doc, "Gambar 3.4 DFD Level 2 Proses 2.0")
    cap_l2_30 = cari_paragraf(doc, "Gambar 3.5 DFD Level 2 Proses 3.0")
    cap_l2_40 = cari_paragraf(doc, "Gambar 3.6 DFD Level 2 Proses 4.0")

    gambar(
        pembuka_dfd2,
        "03_DFD_L2_Proses_1_0.png",
        "Gambar 3.3 DFD Level 2 Proses 1.0 Autentikasi dan Registrasi Pengguna",
    )
    print("   [OK] DFD Level 2 Proses 1.0")

    set_paragraph_text(cap_l2_20, "Gambar 3.4 DFD Level 2 Proses 2.0 Kelola Data Petani")
    set_paragraph_text(cap_l2_30, "Gambar 3.5 DFD Level 2 Proses 3.0 Kelola Setoran Panen")
    set_paragraph_text(cap_l2_40, "Gambar 3.6 DFD Level 2 Proses 4.0 Kelola Alokasi Distribusi")

    # ------------------------------------------------------------
    # 5.2 Activity Diagram alur splash
    #     Disisipkan SETELAH keterangan Activity Diagram alokasi.
    # ------------------------------------------------------------
    cap_act = cari_paragraf(doc, "Gambar 4.2 Activity Diagram AgriUno")
    cap_seq_01 = cari_paragraf(doc, "Gambar 4.4 Sequence Diagram UC-01")
    cap_seq_03 = cari_paragraf(doc, "Gambar 4.5 Sequence Diagram UC-03")
    cap_seq_04 = cari_paragraf(doc, "Gambar 4.6 Sequence Diagram UC-04")
    cap_seq_05 = cari_paragraf(doc, "Gambar 4.7 Sequence Diagram UC-05")
    cap_class = cari_paragraf(doc, "Gambar 4.9 Class Diagram AgriUno")

    gambar(
        cap_act,
        "04_Activity_Diagram_Splash.png",
        "Gambar 4.3 Activity Diagram AgriUno \u2014 Alur Splash dan Animasi Logo",
    )
    print("   [OK] Activity Diagram Splash")

    set_paragraph_text(cap_seq_01, "Gambar 4.4 Sequence Diagram UC-01 Login ke Sistem AgriUno")
    set_paragraph_text(cap_seq_03, "Gambar 4.5 Sequence Diagram UC-03 Mengelola Data Petani")
    set_paragraph_text(cap_seq_04, "Gambar 4.6 Sequence Diagram UC-04 Mencatat Setoran Panen")
    set_paragraph_text(cap_seq_05, "Gambar 4.7 Sequence Diagram UC-05 Mengalokasikan Pengiriman")

    # ------------------------------------------------------------
    # 5.3 Sequence Diagram UC-08
    # ------------------------------------------------------------
    gambar(
        cap_seq_05,
        "04_Sequence_Diagram_UC-08_Registrasi.png",
        "Gambar 4.8 Sequence Diagram UC-08 Registrasi Akun Baru",
    )
    print("   [OK] Sequence Diagram UC-08")

    set_paragraph_text(cap_class, "Gambar 4.9 Class Diagram AgriUno")

    # ------------------------------------------------------------
    # 5.4 Tangkapan layar tambahan pada Subbab 7.2
    #     Disisipkan setelah keterangan Gambar 7.4. Karena setiap
    #     penyisipan selalu berada tepat setelah jangkar, penulisan
    #     dilakukan terbalik agar urutan akhir benar.
    # ------------------------------------------------------------
    anchor = cari_paragraf(doc, "Gambar 7.4 Wireframe/Mockup Halaman Daftar Data Distribusi")
    tambahan = [
        {
            "gambar": "06_panen.png",
            "keterangan": "Gambar 7.5 Tangkapan Layar Halaman Inventori Panen AgriUno",
            "tabel": TABEL_PANEN,
        },
        {
            "gambar": "01_splash.png",
            "keterangan": "Gambar 7.6 Tangkapan Layar Splash dan Animasi Logo AgriUno",
            "tabel": TABEL_SPLASH,
        },
        {
            "gambar": "03_register.png",
            "keterangan": "Gambar 7.7 Tangkapan Layar Halaman Registrasi Akun AgriUno",
            "tabel": TABEL_REGISTRASI,
        },
        {
            "gambar": "08_dashboard_petani.png",
            "keterangan": "Gambar 7.8 Tangkapan Layar Dashboard dengan Peran Petani (Akses Baca)",
            "tabel": TABEL_READONLY,
        },
    ]

    for item in reversed(tambahan):
        cap = gambar(anchor, item["gambar"], item["keterangan"], SCREENSHOT_DIR)
        if cap is None:
            continue
        tbl_baru = insert_table_after(cap, item["tabel"])
        set_table_widths(tbl_baru, [3.4, 8.6, 3.8])
        print("   [OK] %s" % item["gambar"])

    # ------------------------------------------------------------
    # 5.5 Spesifikasi use case dan katalog kelas
    # ------------------------------------------------------------
    _selaraskan_spesifikasi_use_case(doc)
    _selaraskan_katalog_kelas(doc)

    # ------------------------------------------------------------
    # 5.6 Section 8 sampai 11 dan Daftar Pustaka
    # ------------------------------------------------------------
    _tambah_bagian_akhir(doc)

    # ------------------------------------------------------------
    # 5.6 Daftar Isi
    # ------------------------------------------------------------
    _perbarui_daftar_isi(doc)

    return doc


def _selaraskan_spesifikasi_use_case(doc):
    """Menyelaraskan tabel spesifikasi use case serta menambah UC-08 dan UC-09."""
    print("\n[5.5] Menyelaraskan spesifikasi use case...")

    # Deteksi tabel gabungan UC-06 dan UC-07 (20 baris) SEBELUM tabel
    # lain dimodifikasi, karena jumlah barisnya berubah setelah diisi.
    tbl_gabungan = None
    for tbl in doc.tables:
        if len(tbl.rows) >= 18 and len(tbl.columns) == 2:
            tbl_gabungan = tbl
            break

    # Petakan tabel spesifikasi satu use case.
    tabel_uc = {}
    for tbl in doc.tables:
        if tbl is tbl_gabungan:
            continue
        if len(tbl.rows) >= 2 and len(tbl.columns) == 2:
            if tbl.rows[0].cells[0].text.strip() != "Elemen":
                continue
            kedua = tbl.rows[1].cells[1].text.strip() if len(tbl.rows[1].cells) > 1 else ""
            if kedua.startswith("UC-"):
                kunci = kedua.split()[0]
                if kunci not in tabel_uc:
                    tabel_uc[kunci] = tbl

    for kunci in ("UC-01", "UC-02", "UC-03", "UC-04", "UC-05"):
        tbl = tabel_uc.get(kunci)
        if tbl is None:
            print("   ! tabel spesifikasi %s tidak ditemukan" % kunci)
            continue
        isi = [["Elemen", "Isi"]] + [list(r) for r in RC2.SPESIFIKASI_UC[kunci]]
        fill_table(tbl, isi)
        set_table_widths(tbl, [3.4, 12.4])
        print("   [OK] spesifikasi %s" % kunci)

    # Tabel gabungan UC-06 dan UC-07.
    if tbl_gabungan is not None:
        isi = [["Elemen", "Isi"]] + [list(r) for r in RC2.SPESIFIKASI_UC["UC-06"]]
        isi += [["Elemen", "Isi"]] + [list(r) for r in RC2.SPESIFIKASI_UC["UC-07"]]
        fill_table(tbl_gabungan, isi)
        set_table_widths(tbl_gabungan, [3.4, 12.4])
        print("   [OK] spesifikasi UC-06 dan UC-07")

        # Tambahkan tabel spesifikasi UC-08 dan UC-09 setelahnya.
        for kunci in ("UC-08", "UC-09"):
            tbl_baru = insert_table_after(
                tbl_gabungan.rows[0].cells[1].paragraphs[0],
                [["Elemen", "Isi"]] + [list(r) for r in RC2.SPESIFIKASI_UC[kunci]],
            )
            set_table_widths(tbl_baru, [3.4, 12.4])
            tbl_gabungan._tbl.addnext(tbl_baru._tbl)
            print("   [OK] spesifikasi %s" % kunci)
    else:
        print("   ! tabel gabungan UC-06 dan UC-07 tidak ditemukan")


def _selaraskan_katalog_kelas(doc):
    """Menyelaraskan tabel katalog kelas dengan kode sumber versi UAS."""
    print("\n[5.6] Menyelaraskan katalog kelas...")
    for tbl in doc.tables:
        if len(tbl.columns) != 5:
            continue
        if tbl.rows[0].cells[0].text.strip() != "Kelas":
            continue
        fill_table(
            tbl,
            [["Kelas", "Tanggung Jawab", "Atribut Utama", "Metode Utama", "Relasi"]]
            + [list(r) for r in RC2.KATALOG_KELAS],
        )
        set_table_widths(tbl, [2.9, 4.1, 2.9, 4.2, 2.7])
        print("   [OK] katalog kelas (%d kelas)" % len(RC2.KATALOG_KELAS))
        return
    print("   ! tabel katalog kelas tidak ditemukan")


def _tambah_bagian_akhir(doc):
    """Menambahkan bagian 8 s.d. 11 beserta Daftar Pustaka."""
    # ---------------- Section 8 ----------------
    doc.add_heading("8. IMPLEMENTASI MODUL 1 SAMPAI MODUL 8 (UAS)", level=1)
    doc.add_paragraph(
        "Bagian ini memetakan kembali seluruh modul praktikum 1 sampai dengan "
        "modul 8 terhadap artefak yang benar-benar ada di dalam repositori "
        "AgriUno versi UAS. Pemetaan ini menjadi bukti keselarasan antara "
        "dokumen, kode sumber, dan hasil pengujian."
    )
    doc.add_paragraph(
        "Tabel 8.1 Implementasi Setiap Modul Praktikum"
    ).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_table(rows=1, cols=5)
    tabel_modul = doc.tables[-1]
    with contextlib.suppress(KeyError):
        tabel_modul.style = "Table Grid"
    fill_table(
        tabel_modul,
        [["Modul", "Judul Modul", "Implementasi", "Artefak", "Catatan"]]
        + [list(r) for r in RC.MODUL_IMPLEMENTASI],
    )
    set_table_widths(tabel_modul, [1.7, 2.9, 4.6, 3.1, 3.5])
    print("   [OK] Section 8 — Implementasi Modul 1 s.d. 8")

    # ---------------- Section 9 ----------------
    doc.add_heading("9. PERBANDINGAN APLIKASI UTS DAN UAS", level=1)
    doc.add_paragraph(
        "Bagian ini menjelaskan secara rinci perbedaan antara aplikasi dan "
        "dokumen yang dihasilkan pada tahap UTS dengan tahap UAS. "
        "Perbedaan tersebut mencakup fitur baru yang ditambahkan, cacat "
        "logika yang ditemukan serta diperbaiki, dan penyelaraskan kembali "
        "seluruh diagram dan tabel pada laporan agar tidak lagi berbeda "
        "dengan sistem aslinya."
    )
    doc.add_paragraph(
        "Tabel 9.1 Perbandingan Fitur dan Perbaikan antara UTS dan UAS"
    ).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_table(rows=1, cols=4)
    tabel_banding = doc.tables[-1]
    with contextlib.suppress(KeyError):
        tabel_banding.style = "Table Grid"
    fill_table(
        tabel_banding,
        [["Aspek", "Kondisi pada UTS", "Kondisi pada UAS", "Sumber Perubahan"]]
        + [list(r) for r in RC.PERBANDINGAN],
    )
    set_table_widths(tabel_banding, [2.6, 5.0, 5.6, 2.6])
    print("   [OK] Section 9 — Perbandingan UTS dan UAS")

    # ---------------- Section 10 ----------------
    doc.add_heading("10. PENGUJIAN, PEMAKETAN, DAN RILIS", level=1)

    doc.add_heading("10.1 Hasil Pengujian", level=2)
    doc.add_paragraph(
        "Seluruh pengujian otomatis ditulis dengan kerangka kerja pytest dan "
        "dijalankan melalui pipeline GitHub Actions pada setiap perubahan "
        "kode. Pengujian yang membutuhkan server MySQL ditandai dengan "
        "penanda db dan otomatis dilewati apabila server tidak tersedia, "
        "sehingga pipeline tetap dapat dijalankan pada runner tanpa basis "
        "data."
    )
    doc.add_paragraph(
        "Tabel 10.1 Rekapitulasi Hasil Pengujian"
    ).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_table(rows=1, cols=4)
    tabel_uji = doc.tables[-1]
    with contextlib.suppress(KeyError):
        tabel_uji.style = "Table Grid"
    fill_table(
        tabel_uji,
        [["Pengujian", "Ruang Lingkup", "Berkas", "Hasil"]] + [list(r) for r in RC.PENGUJIAN],
    )
    set_table_widths(tabel_uji, [3.2, 5.6, 4.4, 2.6])
    print("   [OK] Section 10.1 — Hasil Pengujian")

    doc.add_heading("10.2 Pemaketan dan Pelepasan Versi", level=2)
    doc.add_paragraph(
        "Aplikasi dikemas menjadi satu berkas eksekusi mandiri (.exe) "
        "menggunakan PyInstaller agar dapat dijalankan pengguna akhir tanpa "
        "perlu memasang Python. Ikon berkas eksekusi menggunakan logo "
        "AgriUno. Langkah berikut bersifat berurutan dan menjadi rujukan "
        "operasional saat presentasi."
    )
    doc.add_paragraph(
        "Tabel 10.2 Langkah Pemaketan dan Pelepasan Versi"
    ).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_table(rows=1, cols=2)
    tabel_rilis = doc.tables[-1]
    with contextlib.suppress(KeyError):
        tabel_rilis.style = "Table Grid"
    fill_table(
        tabel_rilis,
        [["Langkah", "Uraian"]]
        + [[str(i + 1), t[0] + " " + t[1]] for i, t in enumerate(RC.DISTRIBUSI_LANGKAH)],
    )
    set_table_widths(tabel_rilis, [1.8, 14.0])
    print("   [OK] Section 10.2 — Pemaketan dan Rilis")

    # ---------------- Section 11 ----------------
    doc.add_heading("11. KESIMPULAN", level=1)
    doc.add_paragraph(
        "Secara umum, kelanjutan proyek AgriUno dari tahap UTS menuju tahap "
        "UAS berhasil diwujudkan tanpa meninggalkan kerangka arsitektur "
        "yang telah dibangun. Berikut simpulan per modul praktikum."
    )
    for judul, isi in KESIMPULAN_PARAGRAF.items():
        doc.add_heading(judul, level=2)
        doc.add_paragraph(isi)
    print("   [OK] Section 11 — Kesimpulan")

    # ---------------- Daftar Pustaka ----------------
    doc.add_heading("DAFTAR PUSTAKA", level=1)
    for entri in DAFTAR_PUSTAKA:
        p = doc.add_paragraph(entri)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    print("   [OK] Daftar Pustaka")


def _perbarui_daftar_isi(doc):
    """Menyusun ulang Daftar Isi (field TOC) pada dokumen.

    Entri yang sudah ada diperbarui teksnya melalui simpul di dalam
    ``w:hyperlink``, sedangkan entri baru untuk bagian 8 s.d. 11 dan
    Daftar Pustaka disalin dari entri terakhir agar mewarisi gaya
    TOC1. Field TOC ditandai untuk diperbarui otomatis oleh Word
    sehingga nomor halaman ikut menyesuaikan.
    """
    sdt_daftar_isi = None
    for anak in doc.element.body.iterchildren():
        if anak.tag.endswith("}sdt"):
            teks = "".join(anak.itertext())
            if "LEMBAR KENDALI DOKUMEN" in teks or "INFORMASI UMUM PROYEK" in teks:
                sdt_daftar_isi = anak
                break

    if sdt_daftar_isi is None:
        print("   ! Daftar Isi (field TOC) tidak ditemukan, dilewati.")
        return

    # Entri yang sudah ada pada dokumen.
    entri_lama = [
        "LEMBAR KENDALI DOKUMEN",
        "Riwayat Perubahan",
        "Persetujuan",
        "1. INFORMASI UMUM PROYEK",
        "1.1 Identitas Proyek",
        "1.2 Ringkasan Masalah dan Solusi",
        "1.3 Tujuan Sistem",
        "1.4 Ruang Lingkup",
        "1.5 Stakeholder",
        "2. SOFTWARE REQUIREMENTS SPECIFICATION (SRS)",
        "2.1 Gambaran Produk",
        "2.2 Daftar Aktor dan Hak Akses",
        "2.3 Kebutuhan Fungsional",
        "2.4 Kebutuhan Non-Fungsional",
        "2.5 Aturan Bisnis",
        "2.6 Asumsi, Kendala, dan Dependensi",
        "3. PEMODELAN ALIRAN DATA",
        "3.1 Diagram Konteks",
        "3.2 DFD Level 1",
        "3.3 DFD Level 2",
        "3.4 Pemeriksaan Keseimbangan DFD",
        "4. PEMODELAN UML",
        "4.1 Use Case Diagram",
        "4.2 Daftar Use Case",
        "4.3 Spesifikasi Use Case",
        "4.4 Activity Diagram",
        "4.5 Sequence Diagram",
        "4.6 Class Diagram",
        "4.7 Katalog Kelas",
        "5. DATA DAN BASIS DATA",
        "5.1 Entity Relationship Diagram",
        "5.2 Daftar Tabel",
        "5.3 Kamus Data",
        "5.4 Validasi Data",
        "6. ARSITEKTUR DAN PERANCANGAN SISTEM",
        "6.1 Arsitektur Sistem",
        "6.2 Teknologi yang Digunakan",
        "6.3 Dokumentasi Model, View, dan Controller",
        "6.4 Struktur Folder Proyek",
        "6.5 Diagram Navigasi",
        "7. RANCANGAN ANTARMUKA",
        "7.1 Pedoman Antarmuka",
        "7.2 Wireframe dan Mockup",
    ]

    entri_baru = [
        "8. IMPLEMENTASI MODUL 1 SAMPAI MODUL 8 (UAS)",
        "9. PERBANDINGAN APLIKASI UTS DAN UAS",
        "10. PENGUJIAN, PEMAKETAN, DAN RILIS",
        "10.1 Hasil Pengujian",
        "10.2 Pemaketan dan Pelepasan Versi",
        "11. KESIMPULAN",
        "DAFTAR PUSTAKA",
    ]

    paragraf_toc = list(sdt_daftar_isi.iter(qn("w:p")))

    # Lewati paragraf judul "DAFTAR ISI" (gaya Heading1).
    paragraf_entri = []
    for p in paragraf_toc:
        hyperlink = p.find(qn("w:hyperlink"))
        if hyperlink is not None:
            paragraf_entri.append((p, hyperlink))

    # Perbarui entri yang sudah ada.
    for (_p, hyperlink), teks in zip(paragraf_entri, entri_lama, strict=False):
        simpul_teks = hyperlink.find(".//" + qn("w:t"))
        if simpul_teks is not None:
            simpul_teks.text = teks

    # Buang entri sisa yang tidak lagi dipakai (misalnya entri ganda
    # "7.2 Wireframe dan Mockup" yang tersisa pada dokumen asli).
    for p, _hyperlink in paragraf_entri[len(entri_lama) :]:
        p.getparent().remove(p)
    paragraf_entri = paragraf_entri[: len(entri_lama)]

    # Tambahkan entri baru dengan menyalin entri terakhir.
    if paragraf_entri:
        p_contoh, _ = paragraf_entri[-1]
        for teks in entri_baru:
            p_baru = copy.deepcopy(p_contoh)
            hyperlink = p_baru.find(qn("w:hyperlink"))
            if hyperlink is not None:
                # Hapus field PAGEREF agar tidak menunjuk bookmark yang salah.
                for run in list(hyperlink.findall(qn("w:r"))):
                    jenis = run.find(qn("w:fldChar"))
                    instr = run.find(qn("w:instrText"))
                    if jenis is not None or instr is not None or run.find(qn("w:tab")) is not None:
                        hyperlink.remove(run)
                simpul_teks = hyperlink.find(".//" + qn("w:t"))
                if simpul_teks is not None:
                    simpul_teks.text = teks
            p_contoh.addnext(p_baru)
            p_contoh = p_baru

    # Tandai agar Word memperbarui seluruh field saat dokumen dibuka.
    _aktifkan_pembaruan_field(doc)

    print("   [OK] Daftar Isi (%d entri lama + %d entri baru)" % (len(entri_lama), len(entri_baru)))


def _aktifkan_pembaruan_field(doc):
    """Menyatakan agar Word memperbarui seluruh field (termasuk TOC)."""
    try:
        settings = doc.settings.element
    except Exception:
        return
    if settings.find(qn("w:updateFields")) is not None:
        return
    elem = settings.makeelement(qn("w:updateFields"), {})
    elem.set(qn("w:val"), "true")
    settings.append(elem)
