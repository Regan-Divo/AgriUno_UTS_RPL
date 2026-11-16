"""
==========================================================
DIAGRAM DFD AGRIUNO (UAS RPL 2026)
==========================================================
Pembangkitan Diagram Konteks, DFD Level 1, dan DFD Level 2
berdasarkan implementasi kode AgriUno yang terbaru.

Sumber kebenaran:
  * Tabel  : database.sql (users, petani, inventori_panen, distribusi)
  * Proses : controllers/controller.py dan controllers/auth_controller.py
  * Aktor  : views/login_view.py, views/register_view.py, views/*_view.py
"""

from diagram_builder import (
    S_AKTOR,
    S_CATATAN,
    S_EDGE,
    S_ENTITAS,
    S_JUDUL,
    S_LABEL,
    S_LINE,
    S_NAMA_PROSES,
    S_PROSES,
    S_STORE,
    S_STORE_TERBUKA,
    S_SUBJUDUL,
    Diagram,
)

# ------------------------------------------------------------
# Konstanta bersama
# ------------------------------------------------------------
NAMA_SISTEM = "AgriUno"
JUDUL_SISTEM = "Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal"


def _judul(diag, judul, subjudul, width):
    """Menambahkan judul dan subjudul diagram."""
    diag.text(judul, 0, 16, width, 34, S_JUDUL)
    if subjudul:
        diag.text(subjudul, 0, 48, width, 22, S_SUBJUDUL)


def _store(diag, x, y, w, h, kode, nama):
    """Menyusun data store berbentuk garis sejajar ganda.

    Mengembalikan id simpul data store.
    """
    store_id = diag.node("", S_STORE, x, y, w, h)
    diag.node("", S_STORE_TERBUKA, x, y, w, h)
    diag.line(x, y + h, x + w, y + h, S_LINE)
    diag.text(kode, x + 12, y + 8, 120, 22, S_LABEL)
    diag.text(
        nama,
        x + 12,
        y + 40,
        w - 24,
        30,
        S_CATATAN.replace("align=left", "align=left").replace("fontSize=14", "fontSize=15"),
    )
    return store_id


def _proses(diag, x, y, w, h, nomor, nama):
    """Menyusun kotak proses bernomor beserta namanya.

    Mengembalikan id simpul proses.
    """
    proses_id = diag.node(nomor, S_PROSES, x, y, w, h)
    diag.line(x + 8, y + 34, x + w - 8, y + 34, S_LINE)
    diag.text(nama, x + 8, y + 38, w - 16, h - 44, S_NAMA_PROSES)
    return proses_id


# ============================================================
# 1. DIAGRAM KONTEKS (LEVEL 0)
# ============================================================
def diagram_konteks():
    """Diagram Konteks AgriUno."""
    d = Diagram("Diagram Konteks AgriUno", 1460, 800, "Diagram Konteks AgriUno")
    _judul(
        d,
        "Diagram Konteks AgriUno  \u2014  " + JUDUL_SISTEM,
        "Batas sistem digambarkan sebagai satu proses bernomor 0.0",
        1460,
    )

    # --- Aktor dan entitas eksternal ---
    pengguna_baru = d.node("Pengguna Baru<br>(ACT-04)", S_AKTOR, 1000, 100, 210, 84)
    petani = d.node("Petani<br>(ACT-02)", S_ENTITAS, 600, 100, 210, 84)
    admin = d.node("Admin Gudang<br>(ACT-01)", S_ENTITAS, 60, 300, 200, 200)
    distributor = d.node("Distributor<br>(ACT-03)", S_ENTITAS, 1140, 320, 210, 100)

    # --- Proses tunggal sistem ---
    proses = d.node("0.0", S_PROSES, 500, 250, 380, 280)
    d.line(512, 284, 868, 284, S_LINE)
    d.text("%s<br>%s" % (NAMA_SISTEM, JUDUL_SISTEM), 520, 320, 340, 100, S_NAMA_PROSES)

    # ==========================================================
    # Aliran data dari Admin Gudang ke sistem
    # Titik keluar tersebar pada sisi kanan kotak Admin Gudang.
    # ==========================================================
    keluar = [(1.0, 0.06), (1.0, 0.26), (1.0, 0.46), (1.0, 0.66), (1.0, 0.86)]
    masuk = [(0.0, 0.08), (0.0, 0.26), (0.0, 0.44), (0.0, 0.62), (0.0, 0.80)]

    d.edge(admin, proses, "Data Login Pengguna", S_EDGE(), exit_xy=keluar[0], entry_xy=masuk[0])
    d.edge(admin, proses, "Data Master Petani", S_EDGE(), exit_xy=keluar[1], entry_xy=masuk[1])
    d.edge(admin, proses, "Data Setoran Panen", S_EDGE(), exit_xy=keluar[2], entry_xy=masuk[2])
    d.edge(admin, proses, "Data Alokasi Pengiriman", S_EDGE(), exit_xy=keluar[3], entry_xy=masuk[3])
    d.edge(
        admin, proses, "Update Status Pengiriman", S_EDGE(), exit_xy=keluar[4], entry_xy=masuk[4]
    )

    # ==========================================================
    # Aliran data dari sistem ke Admin Gudang (melalui sisi bawah)
    # ==========================================================
    d.edge(
        proses,
        admin,
        "Hak Akses Sesi Aktif",
        S_EDGE(),
        exit_xy=(0.18, 1.0),
        entry_xy=(0.22, 1.0),
        points=[(568, 600), (104, 600)],
    )
    d.edge(
        proses,
        admin,
        "Ringkasan Dashboard",
        S_EDGE(),
        exit_xy=(0.48, 1.0),
        entry_xy=(0.50, 1.0),
        points=[(682, 640), (160, 640)],
    )
    d.edge(
        proses,
        admin,
        "Rekapitulasi Gudang",
        S_EDGE(),
        exit_xy=(0.78, 1.0),
        entry_xy=(0.78, 1.0),
        points=[(796, 680), (216, 680)],
    )

    # ==========================================================
    # Aliran data Registrasi Akun (Pengguna Baru)
    # ==========================================================
    d.edge(
        pengguna_baru,
        proses,
        "Data Registrasi Akun",
        S_EDGE(),
        exit_xy=(0.2, 1.0),
        entry_xy=(0.92, 0.0),
        points=[(1042, 205), (850, 205)],
    )
    d.edge(
        proses,
        pengguna_baru,
        "Konfirmasi Registrasi Berhasil",
        S_EDGE(),
        exit_xy=(0.74, 0.0),
        entry_xy=(0.62, 1.0),
        points=[(781, 225), (1130, 225)],
    )

    # ==========================================================
    # Aliran data Petani
    # ==========================================================
    d.edge(
        petani, proses, "Data Identitas Petani", S_EDGE(), exit_xy=(0.25, 1.0), entry_xy=(0.20, 0.0)
    )
    d.edge(
        proses,
        petani,
        "Data Setoran Panen Tercatat",
        S_EDGE(),
        exit_xy=(0.40, 0.0),
        entry_xy=(0.62, 1.0),
        points=[(652, 225), (730, 225)],
    )

    # ==========================================================
    # Aliran data Distributor
    # ==========================================================
    d.edge(
        distributor,
        proses,
        "Permintaan Pasokan Komoditas",
        S_EDGE(),
        exit_xy=(0.0, 0.30),
        entry_xy=(1.0, 0.30),
    )
    d.edge(
        proses,
        distributor,
        "Data Pengiriman &amp; Status Pengiriman",
        S_EDGE(),
        exit_xy=(1.0, 0.60),
        entry_xy=(0.0, 0.70),
    )

    d.text(
        "Keterangan: Admin Gudang (ACT-01) merupakan aktor internal yang "
        "mengoperasikan aplikasi. Pengguna Baru (ACT-04) adalah aktor eksternal "
        "yang melakukan pendaftaran akun pada tahap UAS. Petani (ACT-02) dan "
        "Distributor (ACT-03) tetap bersifat non-user; seluruh data terkait "
        "dicatat oleh Admin Gudang melalui antarmuka AgriUno.",
        60,
        730,
        1340,
        60,
        S_CATATAN,
    )

    return d


# ============================================================
# 2. DFD LEVEL 1
# ============================================================
def diagram_dfd_level1():
    """DFD Level 1 AgriUno."""
    d = Diagram("DFD Level 1 AgriUno", 1760, 900, "DFD Level 1 AgriUno")
    _judul(
        d,
        "DFD Level 1 AgriUno",
        "Pecahan proses 0.0 menjadi lima proses fungsional dan empat data store",
        1760,
    )

    # ------------------------------------------------------------
    # Aktor dan entitas eksternal (kolom kiri)
    # ------------------------------------------------------------
    petani = d.node("Petani<br>(ACT-02)", S_ENTITAS, 40, 110, 190, 76)
    admin = d.node("Admin Gudang<br>(ACT-01)", S_ENTITAS, 40, 280, 190, 290)
    distributor = d.node("Distributor<br>(ACT-03)", S_ENTITAS, 40, 640, 190, 76)
    pengguna_baru = d.node("Pengguna Baru<br>(ACT-04)", S_AKTOR, 1470, 640, 200, 80)

    # ------------------------------------------------------------
    # Kolom proses (tengah) - tinggi setiap proses 72 piksel
    # ------------------------------------------------------------
    px, pw = 600, 290
    p1 = _proses(d, px, 160, pw, 72, "1.0", "Autentikasi &amp; Registrasi")
    p2 = _proses(d, px, 280, pw, 72, "2.0", "Kelola Data Petani")
    p3 = _proses(d, px, 400, pw, 72, "3.0", "Kelola Setoran Panen")
    p4 = _proses(d, px, 520, pw, 72, "4.0", "Kelola Alokasi Distribusi")
    p5 = _proses(d, px, 640, pw, 72, "5.0", "Tampilan Dashboard Ringkasan")

    # ------------------------------------------------------------
    # Kolom data store (kanan) - sejajar dengan proses induknya
    # ------------------------------------------------------------
    sx, sw = 1140, 280
    s1 = _store(d, sx, 268, sw, 96, "D1", "petani")
    s2 = _store(d, sx, 388, sw, 96, "D2", "inventori_panen")
    s3 = _store(d, sx, 508, sw, 96, "D3", "distribusi")
    s4 = _store(d, sx, 148, sw, 96, "D4", "users")

    # ==========================================================
    # Aliran data Admin Gudang -> proses 1.0 s.d. 4.0
    # Titik keluar dan masuk dijajarkan agar membentuk garis lurus.
    # ==========================================================
    d.edge(admin, p1, "Data Login Pengguna", S_EDGE(), exit_xy=(1.0, 0.10), entry_xy=(0.0, 0.5))
    d.edge(
        admin,
        p2,
        "Data Master Petani",
        S_EDGE(),
        exit_xy=(1.0, 0.30),
        entry_xy=(0.0, 0.5),
        label_offset=(115, -48),
    )
    d.edge(admin, p3, "Data Setoran Panen", S_EDGE(), exit_xy=(1.0, 0.50), entry_xy=(0.0, 0.5))
    d.edge(
        admin, p4, "Data Alokasi Pengiriman", S_EDGE(), exit_xy=(1.0, 0.72), entry_xy=(0.0, 0.28)
    )
    d.edge(
        admin, p4, "Update Status Pengiriman", S_EDGE(), exit_xy=(1.0, 0.90), entry_xy=(0.0, 0.76)
    )

    # ==========================================================
    # Aliran data proses -> Admin Gudang
    # ==========================================================
    d.edge(
        p1,
        admin,
        "Hak Akses Sesi Aktif",
        S_EDGE(),
        exit_xy=(0.0, 1.0),
        entry_xy=(1.0, 0.02),
        points=[(520, 250), (300, 250)],
    )
    d.edge(
        p5,
        admin,
        "Ringkasan Dashboard",
        S_EDGE(),
        exit_xy=(0.0, 0.28),
        entry_xy=(1.0, 0.96),
        points=[(520, 660), (300, 660)],
    )
    d.edge(
        p5,
        admin,
        "Rekapitulasi Gudang",
        S_EDGE(),
        exit_xy=(0.0, 0.76),
        entry_xy=(1.0, 0.99),
        points=[(480, 700), (280, 700)],
    )

    # ==========================================================
    # Aliran data Registrasi Akun (Pengguna Baru)
    # ==========================================================
    d.edge(
        pengguna_baru,
        p1,
        "Data Registrasi Akun",
        S_EDGE(),
        exit_xy=(0.0, 0.35),
        entry_xy=(0.92, 1.0),
        points=[(1020, 668), (1020, 246)],
        label_offset=(-20, 96),
    )
    d.edge(
        p1,
        pengguna_baru,
        "Konfirmasi Registrasi Berhasil",
        S_EDGE(),
        exit_xy=(0.85, 0.0),
        entry_xy=(0.35, 0.0),
        points=[(846, 120), (1540, 120)],
    )

    # ==========================================================
    # Aliran data Petani
    # ==========================================================
    d.edge(
        petani,
        p2,
        "Data Identitas Petani",
        S_EDGE(),
        exit_xy=(1.0, 0.80),
        entry_xy=(0.0, 0.86),
        points=[(300, 171), (300, 342)],
        label_offset=(60, 0),
    )
    d.edge(
        p2,
        petani,
        "Data Setoran Panen Tercatat",
        S_EDGE(),
        exit_xy=(0.0, 0.14),
        entry_xy=(1.0, 0.50),
        points=[(470, 290), (330, 290), (330, 148)],
    )

    # ==========================================================
    # Aliran data Distributor
    # ==========================================================
    d.edge(
        distributor,
        p4,
        "Permintaan Pasokan Komoditas",
        S_EDGE(),
        exit_xy=(1.0, 0.35),
        entry_xy=(0.0, 0.28),
        points=[(330, 667), (330, 540)],
    )
    d.edge(
        p4,
        distributor,
        "Data Pengiriman &amp; Status Pengiriman",
        S_EDGE(),
        exit_xy=(0.0, 0.76),
        entry_xy=(1.0, 0.75),
        points=[(500, 575), (380, 575)],
    )

    # ==========================================================
    # Aliran data antar proses dan data store
    # ==========================================================
    d.edge(p1, s4, "Data Akun Pengguna", S_EDGE(), exit_xy=(1.0, 0.5), entry_xy=(0.0, 0.5))
    d.edge(
        s4,
        p1,
        "Data Kredensial Terverifikasi",
        S_EDGE(),
        exit_xy=(0.0, 0.85),
        entry_xy=(1.0, 0.85),
        points=[(1040, 230), (1040, 221)],
    )

    d.edge(p2, s1, "Data Master Petani", S_EDGE(), exit_xy=(1.0, 0.30), entry_xy=(0.0, 0.30))
    d.edge(
        s1,
        p2,
        "Data Petani Terdaftar",
        S_EDGE(),
        exit_xy=(0.0, 0.70),
        entry_xy=(1.0, 0.72),
        points=[(1060, 335), (1060, 332)],
    )

    d.edge(
        s1,
        p3,
        "Data Petani Penyetor",
        S_EDGE(),
        exit_xy=(0.0, 0.0),
        entry_xy=(1.0, 0.28),
        points=[(1020, 268), (1020, 420)],
        label_offset=(70, 0),
    )
    d.edge(p3, s2, "Data Setoran Panen", S_EDGE(), exit_xy=(1.0, 0.30), entry_xy=(0.0, 0.30))
    d.edge(
        s2,
        p3,
        "Data Stok Lot Panen",
        S_EDGE(),
        exit_xy=(0.0, 0.70),
        entry_xy=(1.0, 0.72),
        points=[(1060, 455), (1060, 452)],
    )

    d.edge(
        s2,
        p4,
        "Data Stok &amp; Riwayat Alokasi Lot",
        S_EDGE(),
        exit_xy=(0.0, 0.0),
        entry_xy=(1.0, 0.14),
        points=[(1050, 388), (1050, 530)],
        label_offset=(70, 0),
    )
    d.edge(p4, s3, "Data Alokasi Pengiriman", S_EDGE(), exit_xy=(1.0, 0.30), entry_xy=(0.0, 0.30))
    d.edge(
        s3,
        p4,
        "Data Status Pengiriman",
        S_EDGE(),
        exit_xy=(0.0, 0.70),
        entry_xy=(1.0, 0.72),
        points=[(1060, 575), (1060, 572)],
    )

    d.edge(
        s1,
        p5,
        "Data Rekapitulasi Petani",
        S_EDGE(),
        exit_xy=(0.0, 0.0),
        entry_xy=(1.0, 0.14),
        points=[(1100, 268), (1100, 650)],
        label_offset=(-30, 46),
    )
    d.edge(
        s2,
        p5,
        "Data Rekapitulasi Setoran Panen",
        S_EDGE(),
        exit_xy=(0.0, 0.0),
        entry_xy=(1.0, 0.40),
        points=[(1160, 388), (1160, 669)],
        label_offset=(100, -14),
    )
    d.edge(
        s3,
        p5,
        "Data Rekapitulasi Distribusi",
        S_EDGE(),
        exit_xy=(0.0, 0.0),
        entry_xy=(1.0, 0.70),
        points=[(1220, 508), (1220, 690)],
        label_offset=(100, 16),
    )

    d.text(
        "Keseimbangan terhadap Diagram Konteks: setiap aliran data pada "
        "Diagram Konteks memiliki pasangan pada Level 1. Aliran \u201cRekapitulasi "
        "Gudang\u201d terbagi menjadi tiga aliran turunan (Rekapitulasi Petani, "
        "Rekapitulasi Setoran Panen, dan Rekapitulasi Distribusi). Aliran "
        "\u201cData Registrasi Akun\u201d dan \u201cKonfirmasi Registrasi Berhasil\u201d "
        "merupakan tambahan tahap UAS yang berasal dari proses 1.0 dan "
        "berinteraksi dengan data store D4 users.",
        40,
        790,
        1660,
        80,
        S_CATATAN,
    )

    return d


# ============================================================
# 3. DFD LEVEL 2
# ============================================================
def diagram_dfd_l2_autentikasi():
    """DFD Level 2 untuk proses 1.0 Autentikasi & Registrasi."""
    d = Diagram(
        "DFD Level 2 Proses 1.0",
        1520,
        860,
        "DFD Level 2 - Proses 1.0 Autentikasi dan Registrasi Pengguna",
    )
    _judul(
        d,
        "DFD Level 2  \u2014  Proses 1.0 Autentikasi dan Registrasi Pengguna",
        "(pecahan dari DFD Level 1: Proses 1.0)",
        1520,
    )

    baru = d.node("Pengguna Baru<br>(ACT-04)", S_AKTOR, 40, 130, 210, 76)
    admin = d.node("Admin Gudang<br>(ACT-01)", S_ENTITAS, 40, 280, 210, 280)

    px, pw = 600, 300
    p1 = _proses(d, px, 280, pw, 76, "1.1", "Verifikasi Login")
    p2 = _proses(d, px, 400, pw, 76, "1.2", "Validasi &amp; Simpan Registrasi")
    p3 = _proses(d, px, 520, pw, 76, "1.3", "Penetapan Hak Akses Sesi")

    store = _store(d, 1180, 265, 280, 106, "D4", "users")

    # --- Aliran dari Pengguna Baru ---
    d.edge(
        baru,
        p1,
        "Data Registrasi Akun",
        S_EDGE(),
        exit_xy=(0.7, 1.0),
        entry_xy=(0.4, 0.0),
        points=[(187, 255), (720, 255)],
    )
    d.edge(
        p3,
        baru,
        "Konfirmasi Registrasi Berhasil",
        S_EDGE(),
        exit_xy=(1.0, 0.3),
        entry_xy=(1.0, 0.5),
        points=[(960, 543), (960, 220), (250, 220)],
    )

    # --- Aliran dari Admin Gudang ---
    d.edge(admin, p1, "Data Login Pengguna", S_EDGE(), exit_xy=(1.0, 0.136), entry_xy=(0.0, 0.5))
    d.edge(admin, p3, "Data Profil Pengguna", S_EDGE(), exit_xy=(1.0, 0.95), entry_xy=(0.0, 0.35))

    # --- Aliran antar proses ---
    d.edge(
        p1,
        p2,
        "Identitas Pengguna Terverifikasi",
        S_EDGE(),
        exit_xy=(0.25, 1.0),
        entry_xy=(0.25, 0.0),
    )
    d.edge(p2, p3, "Akun Berhasil Dibuat", S_EDGE(), exit_xy=(0.6, 1.0), entry_xy=(0.6, 0.0))
    d.edge(
        p3,
        admin,
        "Hak Akses Sesi Aktif",
        S_EDGE(),
        exit_xy=(0.0, 1.0),
        entry_xy=(0.5, 1.0),
        points=[(600, 650), (145, 650)],
    )

    # --- Aliran dengan data store D4 ---
    d.edge(
        p1,
        store,
        "Data Kredensial (username, password, salt)",
        S_EDGE(),
        exit_xy=(1.0, 0.35),
        entry_xy=(0.0, 0.25),
    )
    d.edge(
        store,
        p1,
        "Hash SHA-256 &amp; Data Peran Pengguna",
        S_EDGE(),
        exit_xy=(0.0, 0.65),
        entry_xy=(1.0, 0.7),
    )
    d.edge(
        p2,
        store,
        "Data Akun Pengguna Baru",
        S_EDGE(),
        exit_xy=(1.0, 0.15),
        entry_xy=(0.0, 0.45),
        points=[(1120, 411), (1120, 313)],
    )
    d.edge(
        store,
        p2,
        "Konfirmasi Penyimpanan",
        S_EDGE(),
        exit_xy=(0.0, 0.85),
        entry_xy=(1.0, 0.85),
        points=[(1000, 355), (1000, 465)],
    )

    d.text(
        "Catatan kesesuaian dengan kode: proses 1.1 membaca data kredensial "
        "pada tabel users melalui UserModel.authenticate(), proses 1.2 "
        "memvalidasi formulir registrasi serta membangkitkan salt acak "
        "sebelum menyimpan hash SHA-256, dan proses 1.3 menetapkan peran "
        "pengguna pada objek Session. Peran 'admin' tidak dapat dipilih "
        "pada formulir registrasi (BR-07).",
        40,
        730,
        1420,
        80,
        S_CATATAN,
    )

    return d


def diagram_dfd_l2_petani():
    """DFD Level 2 untuk proses 2.0 Kelola Data Petani."""
    d = Diagram("DFD Level 2 Proses 2.0", 1520, 860, "DFD Level 2 - Proses 2.0 Kelola Data Petani")
    _judul(
        d,
        "DFD Level 2  \u2014  Proses 2.0 Kelola Data Petani",
        "(pecahan dari DFD Level 1: Proses 2.0)",
        1520,
    )

    petani = d.node("Petani<br>(ACT-02)", S_ENTITAS, 40, 100, 210, 76)
    admin = d.node("Admin Gudang<br>(ACT-01)", S_ENTITAS, 40, 250, 210, 280)

    px, pw = 600, 300
    p1 = _proses(d, px, 250, pw, 76, "2.1", "Validasi &amp; Simpan Data Petani")
    p2 = _proses(d, px, 380, pw, 76, "2.2", "Tampilkan &amp; Perbarui Data Petani")
    p3 = _proses(d, px, 510, pw, 76, "2.3", "Hapus Data Petani")

    store = _store(d, 1180, 218, 280, 140, "D1", "petani")

    # --- Aliran dari Admin Gudang ---
    d.edge(admin, p1, "Data Master Petani", S_EDGE(), exit_xy=(1.0, 0.136), entry_xy=(0.0, 0.5))
    d.edge(
        admin,
        p2,
        "Data Master Petani (perubahan)",
        S_EDGE(),
        exit_xy=(1.0, 0.60),
        entry_xy=(0.0, 0.5),
        label_offset=(0, 26),
    )
    d.edge(
        admin, p3, "Data Master Petani (hapus)", S_EDGE(), exit_xy=(1.0, 1.0), entry_xy=(0.0, 0.28)
    )

    # --- Aliran dengan data store D1 ---
    d.edge(p1, store, "Data Identitas Petani", S_EDGE(), exit_xy=(1.0, 0.30), entry_xy=(0.0, 0.15))
    d.edge(
        store,
        p1,
        "Konfirmasi Penyimpanan",
        S_EDGE(),
        exit_xy=(0.0, 0.30),
        entry_xy=(1.0, 0.78),
        points=[(1010, 260), (1010, 309)],
        label_offset=(30, 18),
    )
    d.edge(
        p2,
        store,
        "Data Master Petani",
        S_EDGE(),
        exit_xy=(1.0, 0.15),
        entry_xy=(0.0, 0.45),
        points=[(1100, 391), (1100, 281)],
    )
    d.edge(
        store,
        p2,
        "Data Petani Terdaftar",
        S_EDGE(),
        exit_xy=(0.0, 0.55),
        entry_xy=(1.0, 0.90),
        points=[(1040, 295), (1040, 448)],
    )
    d.edge(
        p3,
        store,
        "Permintaan Penghapusan",
        S_EDGE(),
        exit_xy=(1.0, 0.15),
        entry_xy=(0.0, 0.70),
        points=[(1150, 521), (1150, 316)],
    )
    d.edge(
        store,
        p3,
        "Status Penghapusan",
        S_EDGE(),
        exit_xy=(0.0, 0.88),
        entry_xy=(1.0, 0.85),
        points=[(1080, 341), (1080, 575)],
    )

    # --- Aliran dengan Petani ---
    d.edge(
        petani,
        p2,
        "Data Identitas Petani",
        S_EDGE(),
        exit_xy=(1.0, 0.85),
        entry_xy=(0.0, 0.20),
        points=[(300, 165), (300, 395)],
        label_offset=(-40, -20),
    )
    d.edge(
        p2,
        petani,
        "Data Setoran Panen Tercatat",
        S_EDGE(),
        exit_xy=(0.0, 0.05),
        entry_xy=(1.0, 0.15),
        points=[(520, 384), (400, 384), (400, 111)],
    )

    d.text(
        "Catatan kesesuaian dengan kode: proses 2.1 memvalidasi kelengkapan "
        "dan panjang kolom melalui AgriUnoController.tambah_petani(), proses "
        "2.2 menangani pembaruan serta pemuatan ulang tabel antarmuka, dan "
        "proses 2.3 menolak penghapusan apabila petani masih memiliki "
        "riwayat setoran panen (BR-01, galat errno 1451).",
        40,
        730,
        1420,
        80,
        S_CATATAN,
    )

    return d


def diagram_dfd_l2_panen():
    """DFD Level 2 untuk proses 3.0 Kelola Setoran Panen."""
    d = Diagram(
        "DFD Level 2 Proses 3.0", 1520, 880, "DFD Level 2 - Proses 3.0 Kelola Setoran Panen"
    )
    _judul(
        d,
        "DFD Level 2  \u2014  Proses 3.0 Kelola Setoran Panen",
        "(pecahan dari DFD Level 1: Proses 3.0)",
        1520,
    )

    admin = d.node("Admin Gudang<br>(ACT-01)", S_ENTITAS, 40, 280, 210, 280)

    px, pw = 600, 300
    p1 = _proses(d, px, 250, pw, 76, "3.1", "Validasi Setoran Panen")
    p2 = _proses(d, px, 390, pw, 76, "3.2", "Simpan Lot Setoran Panen")
    p3 = _proses(d, px, 530, pw, 76, "3.3", "Hitung &amp; Tampilkan Sisa Stok")

    s_petani = _store(d, 1180, 120, 280, 110, "D1", "petani")
    s_panen = _store(d, 1180, 350, 280, 110, "D2", "inventori_panen")
    s_dist = _store(d, 1180, 560, 280, 110, "D3", "distribusi")

    # --- Aliran dari Admin Gudang ---
    d.edge(admin, p1, "Data Setoran Panen", S_EDGE(), exit_xy=(1.0, 0.136), entry_xy=(0.0, 0.5))
    d.edge(
        admin,
        p2,
        "Data Setoran Panen (perubahan)",
        S_EDGE(),
        exit_xy=(1.0, 0.60),
        entry_xy=(0.0, 0.5),
    )

    # --- Aliran antar proses ---
    d.edge(p1, p2, "Data Setoran Panen Valid", S_EDGE(), exit_xy=(0.25, 1.0), entry_xy=(0.25, 0.0))
    d.edge(p2, p3, "Data Lot Setoran Panen", S_EDGE(), exit_xy=(0.7, 1.0), entry_xy=(0.7, 0.0))

    # --- Aliran dengan data store ---
    d.edge(
        s_petani,
        p1,
        "Data Petani Penyetor",
        S_EDGE(),
        exit_xy=(0.0, 0.6),
        entry_xy=(1.0, 0.25),
        points=[(1030, 186), (1030, 269)],
    )
    d.edge(
        p1,
        p2,
        "Validasi Keberadaan Penyetor",
        S_EDGE(),
        exit_xy=(0.85, 0.5),
        entry_xy=(0.0, 0.5),
        label_offset=(0, -22),
    )
    d.edge(
        p2, s_panen, "Data Lot Setoran Panen", S_EDGE(), exit_xy=(1.0, 0.28), entry_xy=(0.0, 0.28)
    )
    d.edge(
        s_panen,
        p2,
        "Konfirmasi Penyimpanan",
        S_EDGE(),
        exit_xy=(0.0, 0.70),
        entry_xy=(1.0, 0.78),
        points=[(1090, 427), (1090, 449)],
        label_offset=(20, 20),
    )
    d.edge(
        s_panen,
        p3,
        "Data Berat Awal Lot",
        S_EDGE(),
        exit_xy=(0.0, 0.55),
        entry_xy=(1.0, 0.25),
        points=[(1040, 411), (1040, 549)],
    )
    d.edge(
        s_dist,
        p3,
        "Data Total Alokasi Terkirim",
        S_EDGE(),
        exit_xy=(0.0, 0.55),
        entry_xy=(1.0, 0.75),
        points=[(1070, 621), (1070, 587)],
    )
    d.edge(
        p3,
        admin,
        "Data Sisa Stok &amp; Rekapitulasi Setoran",
        S_EDGE(),
        exit_xy=(0.0, 1.0),
        entry_xy=(0.5, 1.0),
        points=[(600, 660), (145, 660)],
    )

    d.text(
        "Catatan kesesuaian dengan kode: proses 3.1 memvalidasi kelengkapan "
        "kolom, konversi berat menjadi angka positif, format tanggal "
        "YYYY-MM-DD, serta keberadaan penyetor pada tabel petani (BR-01). "
        "Proses 3.2 menyimpan berat awal lot pada tabel inventori_panen. "
        "Proses 3.3 menghitung sisa stok dengan rumus jumlah_berat dikurangi "
        "SUM(jumlah_dikirim) pada tabel distribusi (BR-02), sehingga tidak "
        "terdapat risiko stok minus.",
        40,
        740,
        1420,
        80,
        S_CATATAN,
    )

    return d


def diagram_dfd_l2_distribusi():
    """DFD Level 2 untuk proses 4.0 Kelola Alokasi Distribusi."""
    d = Diagram(
        "DFD Level 2 Proses 4.0", 1520, 880, "DFD Level 2 - Proses 4.0 Kelola Alokasi Distribusi"
    )
    _judul(
        d,
        "DFD Level 2  \u2014  Proses 4.0 Kelola Alokasi Distribusi",
        "(pecahan dari DFD Level 1: Proses 4.0)",
        1520,
    )

    admin = d.node("Admin Gudang<br>(ACT-01)", S_ENTITAS, 40, 280, 210, 280)
    distributor = d.node("Distributor<br>(ACT-03)", S_ENTITAS, 40, 100, 210, 76)

    px, pw = 600, 300
    p1 = _proses(d, px, 250, pw, 76, "4.1", "Hitung Sisa Stok &amp; Validasi")
    p2 = _proses(d, px, 390, pw, 76, "4.2", "Simpan Alokasi Pengiriman")
    p3 = _proses(d, px, 530, pw, 76, "4.3", "Perbarui Status Pengiriman")

    s_panen = _store(d, 1180, 220, 280, 110, "D2", "inventori_panen")
    s_dist = _store(d, 1180, 450, 280, 110, "D3", "distribusi")

    # --- Aliran dari Admin Gudang ---
    d.edge(
        admin,
        p2,
        "Data Alokasi Pengiriman",
        S_EDGE(),
        exit_xy=(1.0, 0.30),
        entry_xy=(0.0, 0.5),
        label_offset=(-30, -34),
    )
    d.edge(
        admin, p3, "Update Status Pengiriman", S_EDGE(), exit_xy=(1.0, 0.75), entry_xy=(0.0, 0.5)
    )

    # --- Aliran antar proses ---
    d.edge(p1, p2, "Sisa Stok Valid", S_EDGE(), exit_xy=(0.25, 1.0), entry_xy=(0.25, 0.0))
    d.edge(p2, p3, "Data Alokasi Terdaftar", S_EDGE(), exit_xy=(0.7, 1.0), entry_xy=(0.7, 0.0))

    # --- Aliran dengan data store ---
    d.edge(
        s_panen,
        p1,
        "Data Berat Lot &amp; Riwayat Alokasi",
        S_EDGE(),
        exit_xy=(0.0, 0.6),
        entry_xy=(1.0, 0.30),
        points=[(1040, 286), (1040, 273)],
    )
    d.edge(
        p2,
        s_dist,
        "Data Alokasi Pengiriman",
        S_EDGE(),
        exit_xy=(1.0, 0.28),
        entry_xy=(0.0, 0.28),
        label_offset=(-30, -18),
    )
    d.edge(
        s_dist,
        p2,
        "Konfirmasi Penyimpanan",
        S_EDGE(),
        exit_xy=(0.0, 0.70),
        entry_xy=(1.0, 0.78),
        points=[(1090, 527), (1090, 449)],
    )
    d.edge(
        s_dist,
        p3,
        "Data Status Pengiriman",
        S_EDGE(),
        exit_xy=(0.0, 0.55),
        entry_xy=(1.0, 0.25),
        points=[(1060, 511), (1060, 549)],
    )
    d.edge(
        p3,
        admin,
        "Rekapitulasi Distribusi",
        S_EDGE(),
        exit_xy=(0.0, 1.0),
        entry_xy=(0.5, 1.0),
        points=[(600, 660), (145, 660)],
    )

    # --- Aliran dengan Distributor ---
    d.edge(
        distributor,
        p2,
        "Permintaan Pasokan Komoditas",
        S_EDGE(),
        exit_xy=(1.0, 0.85),
        entry_xy=(0.0, 0.22),
        points=[(300, 165), (300, 407)],
        label_offset=(-70, 14),
    )
    d.edge(
        p2,
        distributor,
        "Data Pengiriman &amp; Status Pengiriman",
        S_EDGE(),
        exit_xy=(0.0, 0.05),
        entry_xy=(1.0, 0.15),
        points=[(520, 394), (400, 394), (400, 111)],
    )

    d.text(
        "Catatan kesesuaian dengan kode: proses 4.1 menghitung sisa stok "
        "dengan penguncian baris (SELECT ... FOR UPDATE) di dalam satu "
        "transaksi sehingga tidak dapat terjadi stok minus akibat dua "
        "permintaan bersamaan (BR-02). Proses 4.2 menyimpan alokasi dengan "
        "status awal 'Diproses' (BR-04). Proses 4.3 hanya menerima tiga "
        "nilai status baku (BR-05) dan menolak perubahan maupun penghapusan "
        "alokasi berstatus 'Terkirim' (BR-09).",
        40,
        740,
        1420,
        80,
        S_CATATAN,
    )

    return d
