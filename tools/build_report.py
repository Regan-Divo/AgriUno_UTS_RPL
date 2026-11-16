"""
==========================================================
PENYUSUN LAPORAN UAS - AGRIUNO (RPL 2026)
==========================================================
Skrip pembantu yang menyelaraskan dokumen laporan (.docx) dengan
kode sumber AgriUno versi UAS.

Yang dilakukan skrip ini:

1. Membuat salinan cadangan dokumen sebelum perubahan.
2. Mengganti seluruh gambar diagram lama dengan diagram baru pada
   folder ``docs/diagrams``.
3. Memperbarui isi tabel-tabel perancangan agar selaras dengan
   implementasi terbaru (tabel users, aturan bisnis BR-06 s.d. BR-10,
   use case UC-08 dan UC-09, dan seterusnya).
4. Menyelaraskan seluruh narasi paragraf yang sebelumnya masih
   mengacu pada kondisi versi UTS.
5. Menambahkan bagian baru: implementasi modul 1 s.d. modul 8,
   perbandingan UTS dan UAS, pengujian serta pemaketan, dan
   kesimpulan.
6. Menyusun ulang Daftar Isi dan mengisi Lembar Kendali Dokumen.

Jalankan::

    python tools/build_report.py

Berkas sumber dan hasil disimpan pada folder yang sama dengan
berkas laporan sumber.
"""

import contextlib
import os
import shutil
import sys

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import report_content as RC  # noqa: E402
import report_content2 as RC2  # noqa: E402

# ------------------------------------------------------------
# LOKASI BERKAS
# ------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIAGRAM_DIR = os.path.join(BASE_DIR, "docs", "diagrams")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "docs", "screenshots")

DOCX_LAPORAN = os.environ.get(
    "AGRIUNO_LAPORAN",
    os.path.join(
        r"C:\Users\regan\OneDrive\STATISTIKA\UTS RPL PRAK",
        "Laporan_UTS_Kelompok 1 (REVISI Section 1-7.3).docx",
    ),
)

#: Lebar area cetak untuk gambar (A4 dengan margin 3 cm).
LEBAR_GAMBAR = Inches(6.3)


# ============================================================
# HELPER: TEKS DAN TABEL
# ============================================================
def set_paragraph_text(paragraph, text, bold=False, italic=False, size=None):
    """Mengganti isi paragraf sambil mempertahankan format pertamanya.

    Bila paragraf memiliki beberapa run (misalnya karena format parsial),
    format run pertama dipakai sebagai acuan dan run lainnya dibuang.
    """
    runs = paragraph.runs
    if not runs:
        paragraph.add_run(text)
        return paragraph

    template = runs[0]
    template.text = text
    template.bold = bold if bold else template.bold
    template.italic = italic if italic else template.italic
    if size is not None:
        template.font.size = Pt(size)

    for run in runs[1:]:
        run._element.getparent().remove(run._element)
    return paragraph


def set_cell_text(cell, text, bold=False, size=9):
    """Mengganti isi sel tabel dengan satu paragraf berformat seragam.

    Perataan kiri digunakan agar kolom sempit tidak memunculkan
    jarak antar kata yang berlebihan.
    """
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = paragraph.add_run(str(text))
    run.font.size = Pt(size)
    run.bold = bold
    return cell


def fill_table(table, rows, size=9, header_size=9):
    """Mengisi ulang sebuah tabel dengan daftar baris.

    Baris yang tersedia akan ditulis ulang; bila jumlah baris tidak
    cukup, baris baru disalin formatnya dari baris terakhir. Bila
    jumlah baris lebih banyak, baris berlebih dihapus.
    """
    # Hapus seluruh baris selain baris pertama (kepala).
    while len(table.rows) > 1:
        table._tbl.remove(table.rows[-1]._tr)

    data = list(rows)
    if not data:
        return table

    # Tulis kepala tabel pada baris pertama.
    for i, value in enumerate(data[0]):
        if i < len(table.rows[0].cells):
            set_cell_text(table.rows[0].cells[i], value, bold=True, size=size)

    # Tulis baris isi.
    for values in data[1:]:
        cells = table.add_row().cells
        for i, value in enumerate(values):
            if i < len(cells):
                set_cell_text(cells[i], value, size=size)

    return table


def remove_paragraph(paragraph):
    """Menghapus sebuah paragraf beserta elemennya dari dokumen."""
    element = paragraph._element
    parent = element.getparent()
    if parent is not None:
        parent.remove(element)


def set_table_widths(table, widths_cm):
    """Menetapkan lebar kolom tabel dalam sentimeter.

    Word sering kali mengabaikan lebar kolom bila properti tblLayout
    masih berjenis otomatis, sehingga lebar tabel dan lebar kolom
    perlu ditetapkan secara eksplisit.
    """
    from docx.shared import Cm

    tbl_pr = table._tbl.tblPr
    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = tbl_pr.makeelement(qn("w:tblLayout"), {})
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")

    table.autofit = False
    for i, lebar in enumerate(widths_cm):
        if i >= len(table.columns):
            break
        table.columns[i].width = Cm(lebar)
        for row in table.rows:
            if i < len(row.cells):
                row.cells[i].width = Cm(lebar)
    return table


def set_row_count(table, count):
    """Menambah atau mengurangi jumlah baris tabel."""
    while len(table.rows) < count:
        table.add_row()
    while len(table.rows) > count:
        table._tbl.remove(table.rows[-1]._tr)


# ============================================================
# HELPER: GAMBAR
# ============================================================
def replace_image(paragraph, image_path, width=None):
    """Mengganti gambar pada sebuah paragraf dengan berkas gambar lain."""
    blips = paragraph._element.findall(".//" + qn("a:blip"))
    if not blips:
        return False
    if not os.path.exists(image_path):
        print("   ! berkas gambar tidak ditemukan: %s" % image_path)
        return False

    rId, _image = paragraph.part.get_or_add_image(image_path)
    for blip in blips:
        blip.set(qn("r:embed"), rId)

    # Atur ukuran gambar sambil mempertahankan rasio aspek.
    if width is not None:
        from PIL import Image

        with Image.open(image_path) as img:
            ratio = img.height / img.width

        cx = int(width)
        cy = int(cx * ratio)

        for extent in paragraph._element.findall(".//" + qn("wp:extent")):
            extent.set("cx", str(cx))
            extent.set("cy", str(cy))
        for ext in paragraph._element.findall(".//" + qn("a:ext")):
            ext.set("cx", str(cx))
            ext.set("cy", str(cy))
    return True


# ============================================================
# HELPER: PENYISIPAN
# ============================================================
def insert_paragraph_after(paragraph, text="", style=None):
    """Menyisipkan paragraf baru tepat setelah paragraf tertentu."""
    new_p = paragraph._element.makeelement(qn("w:p"), {})
    paragraph._element.addnext(new_p)
    new_para = paragraph.__class__(new_p, paragraph._parent)
    if style is not None:
        new_para.style = style
    if text:
        new_para.add_run(text)
    return new_para


def insert_paragraph_before(paragraph, text="", style=None):
    """Menyisipkan paragraf baru tepat sebelum paragraf tertentu."""
    new_p = paragraph._element.makeelement(qn("w:p"), {})
    paragraph._element.addprevious(new_p)
    new_para = paragraph.__class__(new_p, paragraph._parent)
    if style is not None:
        new_para.style = style
    if text:
        new_para.add_run(text)
    return new_para


def insert_table_after(paragraph, data, style="Table Grid", size=9):
    """Menyisipkan tabel baru setelah sebuah paragraf."""
    doc = paragraph.part.document
    table = doc.add_table(rows=1, cols=len(data[0]))
    with contextlib.suppress(KeyError):
        table.style = style

    fill_table(table, data, size=size)

    paragraph._element.addnext(table._tbl)
    return table


def insert_caption_after(paragraph, text):
    """Menyisipkan paragraf keterangan gambar setelah paragraf tertentu."""
    new_para = insert_paragraph_after(paragraph, text)
    with contextlib.suppress(Exception):
        new_para.style = paragraph.style
    new_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in new_para.runs:
        run.italic = True
        run.font.size = Pt(10)
    return new_para


def add_image_paragraph_after(paragraph, image_path, caption, width=LEBAR_GAMBAR):
    """Menyisipkan paragraf gambar beserta keterangannya."""
    img_para = insert_paragraph_after(paragraph)
    img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = img_para.add_run()
    run.add_picture(image_path, width=width)

    cap = insert_caption_after(img_para, caption)
    return img_para, cap


# ============================================================
# PROSES UTAMA
# ============================================================
def backup(path):
    """Membuat salinan cadangan dokumen sumber."""
    if not os.path.exists(path):
        return None
    base, ext = os.path.splitext(path)
    backup_path = "%s_BACKUP-SEBELUM-UAS%s" % (base, ext)
    shutil.copy2(path, backup_path)
    print("Cadangan dokumen: %s" % os.path.basename(backup_path))
    return backup_path


def _perbarui_footer(doc):
    """Mengganti keterangan kaki dokumen dari UTS menjadi UAS.

    Teks diubah langsung pada simpul ``w:t`` (bukan melalui
    ``run.text``) karena penetrationi ``run.text`` akan menghapus
    field ``PAGE`` beserta penandanya sehingga nomor halaman
    menjadi angka statis.
    """
    digubah = 0
    for section in doc.sections:
        for footer in (section.footer, section.first_page_footer, section.even_page_footer):
            if footer is None:
                continue
            for paragraf in footer.paragraphs:
                for simpul in paragraf._element.findall(".//" + qn("w:t")):
                    if simpul.text and "Proyek UTS" in simpul.text:
                        simpul.text = simpul.text.replace("Proyek UTS", "Proyek UAS")
                        digubah += 1
    print("   %d baris kaki dokumen diperbarui" % digubah)


def main():
    """Titik masuk skrip."""
    if not os.path.exists(DOCX_LAPORAN):
        print("Berkas laporan tidak ditemukan: %s" % DOCX_LAPORAN)
        return 1

    print("Membuka dokumen: %s" % os.path.basename(DOCX_LAPORAN))
    backup(DOCX_LAPORAN)

    doc = docx.Document(DOCX_LAPORAN)

    # ------------------------------------------------------------
    # 1. LEMBAR KENDALI DOKUMEN
    # ------------------------------------------------------------
    print("\n[1] Menyusun lembar kendali dokumen...")
    tbl = doc.tables[1]
    for i, (key, value) in enumerate(RC.KENDALI.items()):
        if i + 1 < len(tbl.rows):
            set_cell_text(tbl.rows[i + 1].cells[0], key, bold=True, size=10)
            set_cell_text(tbl.rows[i + 1].cells[1], value, size=10)

    # Riwayat perubahan.
    tbl = doc.tables[2]
    fill_table(
        tbl,
        [["Versi", "Tanggal", "Penulis", "Perubahan"]] + [list(r) for r in RC.RIWAYAT_PERUBAHAN],
        size=10,
    )

    # ------------------------------------------------------------
    # 2. GAMBAR DIAGRAM
    # ------------------------------------------------------------
    print("\n[2] Mengganti gambar diagram...")
    pemetaan_gambar = {
        73: ("03_Diagram_Konteks.png", "Gambar 3.1 Diagram Konteks AgriUno"),
        78: ("03_DFD_Level_1.png", "Gambar 3.2 DFD Level 1 AgriUno"),
        83: ("03_DFD_L2_Proses_2_0.png", "Gambar 3.3 DFD Level 2 Proses 2.0 Kelola Data Petani"),
        85: ("03_DFD_L2_Proses_3_0.png", "Gambar 3.4 DFD Level 2 Proses 3.0 Kelola Setoran Panen"),
        87: (
            "03_DFD_L2_Proses_4_0.png",
            "Gambar 3.5 DFD Level 2 Proses 4.0 Kelola Alokasi Distribusi",
        ),
        94: ("04_Use_Case_Diagram.png", "Gambar 4.1 Use Case Diagram AgriUno"),
        107: (
            "04_Activity_Diagram.png",
            "Gambar 4.2 Activity Diagram AgriUno — Alur Alokasi Pengiriman",
        ),
        111: (
            "04_Sequence_Diagram_UC-01_Login.png",
            "Gambar 4.3 Sequence Diagram UC-01 Login ke Sistem AgriUno",
        ),
        113: (
            "04_Sequence_Diagram_UC-03_Petani.png",
            "Gambar 4.4 Sequence Diagram UC-03 Mengelola Data Petani",
        ),
        115: (
            "04_Sequence_Diagram_UC-04_Panen.png",
            "Gambar 4.5 Sequence Diagram UC-04 Mencatat Setoran Panen",
        ),
        117: (
            "04_Sequence_Diagram_UC-05_Distribusi.png",
            "Gambar 4.6 Sequence Diagram UC-05 Mengalokasikan Pengiriman",
        ),
        121: ("04_Class_Diagram.png", "Gambar 4.7 Class Diagram AgriUno"),
        127: (
            "05_Entity_Relationship_Diagram.png",
            "Gambar 5.1 Entity Relationship Diagram AgriUno",
        ),
        140: ("06_Arsitektur_Sistem.png", "Gambar 6.1 Arsitektur Sistem AgriUno"),
        178: ("06_Diagram_Navigasi.png", "Gambar 6.2 Diagram Navigasi AgriUno"),
    }

    for index, (nama, _) in sorted(pemetaan_gambar.items()):
        path = os.path.join(DIAGRAM_DIR, nama)
        if replace_image(doc.paragraphs[index], path, width=LEBAR_GAMBAR):
            print("   [OK] %s" % nama)

    # Tangkapan layar antarmuka.
    tangkapan = {
        185: ("02_login.png", "Gambar 7.1 Tangkapan Layar Halaman Login AgriUno"),
        188: ("04_dashboard.png", "Gambar 7.2 Tangkapan Layar Halaman Dashboard AgriUno"),
        191: ("05_petani.png", "Gambar 7.3 Tangkapan Layar Halaman Data Petani AgriUno"),
        194: ("07_distribusi.png", "Gambar 7.4 Tangkapan Layar Halaman Data Distribusi AgriUno"),
    }
    for index, (nama, _) in sorted(tangkapan.items()):
        path = os.path.join(SCREENSHOT_DIR, nama)
        if replace_image(doc.paragraphs[index], path, width=LEBAR_GAMBAR):
            print("   [OK] %s" % nama)

    # ------------------------------------------------------------
    # 3. TABEL PERANCANGAN
    # ------------------------------------------------------------
    print("\n[3] Menyelaraskan tabel perancangan...")
    isi_tabel = {
        4: RC.IDENTITAS,
        5: RC.TUJUAN,
        6: RC.RUANG_LINGKUP,
        7: RC.STAKEHOLDER,
        8: RC.AKTOR,
        9: RC.FUNGSIONAL,
        10: RC.NON_FUNGSIONAL,
        11: RC.ATURAN_BISNIS,
        12: RC.ASUMSI,
        13: RC.KONTEKS_TABEL,
        14: RC.DFD1_TABEL,
        15: RC.KESEIMBANGAN,
        16: RC.USE_CASE_DAFTAR,
        24: RC.DAFTAR_TABEL,
        25: RC.KAMUS_DATA,
        26: RC.VALIDASI,
        27: RC.TEKNOLOGI,
        28: RC.DOKUMENTASI_MVC,
        29: RC.PEDOMAN_ANTARMUKA,
        30: RC2.WIREFRAME_LOGIN,
        31: RC2.WIREFRAME_DASHBOARD,
        32: RC2.WIREFRAME_PETANI,
    }
    # Lebar kolom (sentimeter) untuk tiap tabel.
    lebar_kolom = {
        4: [3.6, 12.2],
        5: [2.0, 6.6, 7.2],
        6: [7.9, 7.9],
        7: [1.7, 3.4, 4.2, 6.5],
        8: [1.7, 2.7, 4.4, 7.0],
        9: [1.4, 2.7, 3.6, 2.4, 1.6, 4.1],
        10: [1.4, 2.2, 6.6, 5.6],
        11: [1.5, 9.4, 4.9],
        12: [2.2, 7.4, 6.2],
        13: [3.6, 6.3, 5.9],
        14: [1.6, 3.4, 3.8, 4.0, 2.9],
        15: [4.4, 1.6, 9.8],
        16: [1.6, 3.3, 4.2, 5.2, 1.5],
        24: [1.2, 2.4, 5.0, 2.4, 4.8],
        25: [2.4, 2.6, 2.8, 1.2, 1.3, 2.0, 3.5],
        26: [3.4, 6.4, 6.0],
        27: [2.8, 3.8, 4.6, 4.6],
        28: [1.8, 3.6, 4.6, 3.0, 2.6, 1.8],
        29: [2.4, 13.4],
        30: [3.4, 8.6, 3.8],
        31: [3.4, 8.6, 3.8],
        32: [3.4, 8.6, 3.8],
    }

    for index, data in sorted(isi_tabel.items()):
        table = doc.tables[index]
        header = [c.text.strip() for c in table.rows[0].cells]
        fill_table(table, [header] + [list(r) for r in data])
        if index in lebar_kolom:
            set_table_widths(table, lebar_kolom[index])
        print("   [OK] tabel indeks %d (%d baris)" % (index, len(data)))

    # ------------------------------------------------------------
    # 4. NARASI PARAGRAF
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # 4b. Footer dokumen
    # ------------------------------------------------------------
    _perbarui_footer(doc)

    print("\n[4] Menyelaraskan narasi...")
    narasi = {
        31: "Bagian ini menguraikan kondisi operasional pengelolaan hasil "
        "panen pada gudang penampungan lokal, kendala pencatatan manual "
        "yang dihadapi, solusi perangkat lunak yang ditawarkan oleh "
        "aplikasi AgriUno, serta perkembangan dari versi UTS menuju versi "
        "UAS berupa autentikasi berbasis peran, registrasi akun, dan "
        "antarmuka pembuka berlogo.",
        33: "Pengelolaan hasil panen pada gudang penampungan pertanian lokal "
        "sering mengalami ketidaksesuaian data antara jumlah komoditas yang "
        "disetorkan petani dan jumlah komoditas yang dialokasikan kepada "
        "pembeli. Data setoran dan data pengiriman dicatat pada media "
        "yang berbeda sehingga sulit ditelusuri kembali. Selain itu, "
        "pengguna baru tidak memiliki jalan untuk memperoleh akses ke "
        "sistem, dan aplikasi belum memiliki identitas visual yang "
        "membedakan produk dari aplikasi manajemen gudang lain.",
        35: "Pencatatan penyerahan hasil panen dari petani masih dilakukan "
        "secara manual menggunakan buku log fisik oleh admin gudang. "
        "Selanjutnya, alokasi komoditas yang akan dikirim kepada pembeli "
        "dicatat secara terpisah menggunakan nota kertas, dan perubahan "
        "status pengiriman tidak memiliki catatan riwayat yang tertata. "
        "Akses ke aplikasi hanya diberikan kepada satu operator "
        "administrator dengan kredensial yang disimpan langsung di dalam "
        "kode sumber.",
        37: "Proses manual ini berisiko menyebabkan lembar pencatatan hilang "
        "atau terselip, menyulitkan admin gudang mengetahui ketersediaan "
        "sisa stok panen secara akurat, serta memicu selisih perhitungan "
        "berat komoditas antara barang yang masuk dan barang yang keluar "
        "dari gudang. Selain itu, kredensial yang tertanam di dalam kode "
        "sumber dan tidak adanya mekanisme pendaftaran membuat "
        "sistem sulit dikembangkan ke varian multi-pengguna.",
        39: "Untuk mengatasi kendala tersebut, dibangun aplikasi desktop "
        "AgriUno menggunakan bahasa Python dengan pustaka CustomTkinter "
        "dan basis data MySQL dengan arsitektur Model-View-Controller. "
        "AgriUno menyediakan sarana terpusat untuk mencatat data master "
        "petani penyetor, merekam lot setoran panen masuk, menampilkan "
        "rekapitulasi stok gudang, serta mengelola alokasi dan pembaruan "
        "status pengiriman ke distributor. Pada versi UAS, aplikasi "
        "dilengkapi autentikasi terhadap tabel pengguna, registrasi akun "
        "khusus bagi pengguna baru, pembatasan akses berbasis peran, "
        "serta logo dan animasi pembukaan aplikasi. Aplikasi secara "
        "sengaja tidak menangani transaksi pembayaran maupun perhitungan "
        "keuangan.",
        49: "AgriUno berkedudukan sebagai sistem informasi pengelolaan data "
        "internal untuk gudang penampungan hasil panen lokal. Aplikasi "
        "menghubungkan tiga proses operasional utama di gudang, yaitu "
        "pendataan identitas petani penyetor, pencatatan lot panen masuk, "
        "serta pengelolaan alokasi pengiriman kepada distributor, "
        "serta menambah dua proses baru pada versi UAS, yaitu "
        "autentikasi dan registrasi pengguna serta penyajian rekapitulasi "
        "operasional pada Dashboard.",
        51: "Aplikasi dirancang untuk penggunaan internal di area operasional "
        "gudang. Sistem dijalankan secara terpusat pada satu perangkat PC "
        "atau laptop berbasis Windows. Pada versi UTS aplikasi hanya "
        "digunakan oleh satu operator; pada versi UAS aplikasi dapat "
        "digunakan oleh beberapa pengguna dengan peran berbeda, yaitu "
        "Administrator, Operator Gudang, dan Petani Terdaftar.",
        53: "AgriUno membutuhkan lingkungan eksekusi Python 3.10 atau versi "
        "di atasnya. Untuk antarmuka, sistem bergantung pada pustaka "
        "CustomTkinter serta komponen tkinter (ttk.Treeview, messagebox, "
        "dan Canvas untuk animasi splash). Untuk koneksi data, sistem "
        "menggunakan pustaka mysql-connector-python yang terhubung ke "
        "server MySQL lokal melalui parameter yang dapat dioverride "
        "melalui environment variable pada kelas DatabaseConnection di "
        "berkas config/database.py. Seluruh aset visual aplikasi telah "
        "diprarender pada folder assets sehingga pustaka Pillow tidak "
        "diperlukan saat aplikasi dijalankan.",
        55: "Pengguna aplikasi diasumsikan memiliki kemampuan dasar dalam "
        "mengoperasikan komputer desktop. Layanan basis data MySQL pada "
        "Laragon diasumsikan selalu aktif sebelum aplikasi dijalankan. "
        "Pengguna baru diasumsikan memahami syarat password minimal enam "
        "karakter dan mampu mengingatnya sendiri. Seluruh berkas dan "
        "folder dijalankan dari direktori utama proyek agar impor paket "
        "lokal berhasil.",
        57: "Aplikasi berupa perangkat lunak desktop lokal tanpa akses "
        "berbasis web maupun mobile. Akun Administrator hanya dapat "
        "dibuat oleh pengelola basis data melalui skrip database.sql, "
        "sedangkan pengguna lain mendaftar secara mandiri dengan peran "
        "operator atau petani. Aplikasi secara tegas tidak mencakup "
        "pelacakan kendaraan/GPS, transaksi keuangan, pembayaran digital, "
        "maupun modul akuntansi.",
        70: "Data Flow Diagram menggambarkan aliran informasi, transformasi "
        "data, dan data store secara logis. Diagram Konteks menampilkan "
        "sistem sebagai satu proses bernomor 0, DFD Level 1 menguraikannya "
        "menjadi lima proses utama dan empat data store, dan DFD Level 2 "
        "merinci proses yang masih kompleks. Seluruh diagram dibangkitkan "
        "ulang secara terprogram oleh skrip tools/generate_diagrams.py "
        "sehingga isinya selalu selaras dengan kode sumber.",
        72: "Diagram Konteks menampilkan AgriUno sebagai satu proses bernomor "
        "0 dengan empat entitas eksternal, yaitu Admin Gudang, Pengguna "
        "Baru, Petani, dan Distributor. Entitas Pengguna Baru merupakan "
        "penambahan tahap UAS yang merepresentasikan kemampuan pengguna "
        "baru untuk melakukan pendaftaran akun. Nama aliran pada diagram "
        "berupa data, bukan aktivitas.",
        77: "DFD Level 1 menguraikan proses 0.0 menjadi lima proses utama dan "
        "empat data store. Setiap aliran dari Diagram Konteks memiliki "
        "representasi pada level ini, dan tidak ada aliran yang berasal "
        "dari entitas eksternal secara langsung ke data store. Data store "
        "D4 users merupakan tambahan tahap UAS untuk mendukung autentikasi "
        "dan registrasi akun.",
        82: "Diagram Level 2 merinci proses yang masih kompleks pada Level 1. "
        "Nomor proses turunan mengikuti proses induk, misalnya 1.1–1.3 "
        "untuk proses 1.0. Penambahan tahap UAS diwujudkan melalui "
        "Level 2 untuk proses 1.0 Autentikasi dan Registrasi Pengguna, "
        "sehingga alur verifikasi login dan pendaftaran akun dapat "
        "dilacak secara rinci.",
        92: "Bagian ini memodelkan AgriUno dengan diagram UML. Use Case "
        "Diagram menggambarkan layanan sistem dari sudut pandang aktor, "
        "Activity Diagram mendokumentasikan alur kerja beserta keputusan "
        "dan percabangan, Sequence Diagram menunjukkan pesan antar objek "
        "berdasarkan urutan waktu, dan Class Diagram mendokumentasikan "
        "struktur kelas yang benar-benar terdapat pada kode sumber.",
        106: "Activity Diagram di bawah ini mendokumentasikan dua alur kerja "
        "penting pada sistem. Alur pertama adalah alur alokasi "
        "pengiriman yang memuat dua keputusan, yaitu kelengkapan "
        "masukan dan ketersediaan sisa stok. Alur kedua adalah alur "
        "pembukaan aplikasi berupa splash yang menampilkan logo AgriUno "
        "dengan animasi bertahap. Keduanya menggunakan swimlane karena "
        "tanggung jawab melibatkan pengguna dan sistem AgriUno.",
        110: "Sequence Diagram di bawah ini menunjukkan pesan antar aktor dan "
        "objek berdasarkan urutan waktu untuk lima use case utama. "
        "Seluruh nama lifeline dan nama metode merujuk langsung pada "
        "kelas dan fungsi yang terdapat pada kode sumber AgriUno. Lima "
        "use case yang memiliki Sequence Diagram adalah UC-01, UC-03, "
        "UC-04, UC-05, dan UC-08, sedangkan use case UC-02, UC-06, dan "
        "UC-09 sudah dijelaskan lengkap pada Subbab 4.3 dan alurnya "
        "merupakan kelanjutan dari kelima use case tersebut.",
        120: "Class Diagram di bawah ini menampilkan seluruh kelas yang "
        "benar-benar terdapat pada kode sumber AgriUno beserta atribut "
        "dan metodenya. Tidak ada kelas Entitas Petani atau Database "
        "yang khas pada pemodelan berorientasi objek berbasis domain; "
        "seluruh akses data dilakukan melalui kelas model yang bersifat "
        "utilitas dengan metode statis, dengan objek Session sebagai "
        "penyimpan state sesi pengguna.",
        138: "Arsitektur AgriUno menggunakan pola three-tier yang memisahkan "
        "lapisan presentasi, lapisan logika, dan lapisan akses data "
        "sesuai pola Model-View-Controller. Pada versi UAS ditambahkan "
        "jendela splash sebagai lapisan presentasi pembuka dan lapisan "
        "autentikasi serta pengguna sebagai lapisan logika tambahan.",
        139: "Komunikasi antar lapisan berlangsung satu arah. Lapisan View "
        "hanya menyampaikan masukan pengguna dan menampilkan keluaran; "
        "seluruh keputusan logis berada pada AgriUnoController, "
        "AuthController, dan UserController; dan hanya kelas model yang "
        "membuka koneksi serta mengeksekusi kueri SQL. Dengan demikian, "
        "perubahan antarmuka tidak memengaruhi logika bisnis maupun "
        "struktur basis data.",
        147: "Struktur direktori AgriUno beserta penjelasan fungsi folder dan "
        "berkas utama adalah sebagai berikut.",
        177: "Struktur navigasi aplikasi bersifat dua tingkat. Tingkat "
        "pertama menangani siklus splash, login, dan registrasi, "
        "sedangkan tingkat kedua menangani perpindahan antar halaman "
        "melalui tombol sidebar pada jendela utama.",
        184: "Gambar pada subbab ini merupakan tangkapan layar dari aplikasi "
        "AgriUno yang benar-benar berjalan pada versi UAS. Rincian "
        "elemen antarmuka tiap halaman diuraikan pada tabel di bawah "
        "setiap gambar.",
    }

    for index, teks in sorted(narasi.items()):
        set_paragraph_text(doc.paragraphs[index], teks)
    print("   %d paragraf diperbarui" % len(narasi))

    # ------------------------------------------------------------
    # Struktur folder (6.4) dibangun ulang secara utuh.
    # ------------------------------------------------------------
    intro_folder = doc.paragraphs[147]
    gaya_pohon = doc.paragraphs[148].style

    # Hapus seluruh paragraf pohon lama beserta penjelasannya.
    for paragraf_lama in list(doc.paragraphs)[148:176]:
        remove_paragraph(paragraf_lama)

    # Sisipkan pohon folder baru.
    anchor = intro_folder
    for baris in RC.STRUKTUR_FOLDER.split("\n"):
        baru = insert_paragraph_after(anchor, baris)
        with contextlib.suppress(Exception):
            baru.style = gaya_pohon
        anchor = baru

    # Sisipkan judul penjelasan dan daftar penjelasan folder.
    judul = insert_paragraph_after(anchor, "Penjelasan Fungsi Folder dan Berkas Utama:")
    anchor = judul
    for teks in RC.PENJELASAN_FOLDER:
        baru = insert_paragraph_after(anchor, teks)
        with contextlib.suppress(Exception):
            baru.style = gaya_pohon
        anchor = baru
    print("   [OK] Struktur folder proyek (%d baris)" % len(RC.STRUKTUR_FOLDER.split("\n")))

    # ------------------------------------------------------------
    # 5. BAGIAN KHUSUS UAS (diagram tambahan, section 8 s.d. 11,
    #    daftar pustaka, dan Daftar Isi)
    # ------------------------------------------------------------
    import build_report_uas

    build_report_uas.tambah_dokumen(doc)

    print("\nMenyimpan dokumen...")
    doc.save(DOCX_LAPORAN)
    print("Selesai: %s" % DOCX_LAPORAN)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
