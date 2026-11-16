"""
==========================================================
DIAGRAM UML AGRIUNO (UAS RPL 2026)
==========================================================
Pembangkitan Use Case Diagram, Sequence Diagram, Activity Diagram,
dan Class Diagram berdasarkan implementasi kode AgriUno terbaru.
"""

from diagram_builder import (
    GARIS,
    HIJAU_MUDA,
    HIJAU_TUA,
    MERAH,
    ORANYE,
    S_ACTIVITAS,
    S_AKHIR,
    S_AKTOR,
    S_AWAL,
    S_BOX_HEADER,
    S_CATATAN,
    S_EDGE,
    S_ENTITAS,
    S_ERROR,
    S_JUDUL,
    S_KEPUTUSAN,
    S_LABEL,
    S_MSG,
    S_SISTEM,
    S_SUBJUDUL,
    S_SWIMLANE,
    S_SWIMLANE_HEADER,
    S_USECASE,
    Diagram,
    arrow,
    arrow_h,
    arrow_v,
    lifeline,
    message,
)

JUDUL_SISTEM = "Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal"


def _judul(diag, judul, subjudul, width):
    """Menambahkan judul dan subjudul diagram."""
    diag.text(judul, 0, 16, width, 34, S_JUDUL)
    if subjudul:
        diag.text(subjudul, 0, 48, width, 22, S_SUBJUDUL)


# ============================================================
# 1. USE CASE DIAGRAM
# ============================================================
def diagram_use_case():
    """Use Case Diagram AgriUno."""
    d = Diagram("Use Case Diagram AgriUno", 1700, 900, "Use Case Diagram AgriUno")
    _judul(
        d,
        "Use Case Diagram AgriUno",
        "Sembilan use case dan lima aktor sesuai implementasi UAS",
        1700,
    )

    # ------------------------------------------------------------
    # Batas sistem
    # ------------------------------------------------------------
    d.node("", S_SISTEM, 370, 120, 760, 660)
    d.node("", S_BOX_HEADER, 370, 120, 760, 38)
    d.text("AgriUno  \u2014  " + JUDUL_SISTEM, 380, 124, 740, 30, S_BOX_HEADER)

    # ------------------------------------------------------------
    # Use case (dua kolom di dalam sistem)
    # ------------------------------------------------------------
    uc = [
        ("UC-01", "Login ke Sistem AgriUno", 395, 180),
        ("UC-08", "Registrasi Akun Baru", 395, 300),
        ("UC-02", "Melihat Dashboard Ringkasan", 395, 420),
        ("UC-06", "Keluar dari Aplikasi", 395, 540),
        ("UC-03", "Mengelola Data Petani", 765, 180),
        ("UC-04", "Mencatat Setoran Panen", 765, 300),
        ("UC-05", "Mengalokasikan Pengiriman", 765, 420),
        ("UC-07", "Memperbarui Status Pengiriman", 765, 540),
        ("UC-09", "Mengubah Kata Sandi Pengguna", 580, 640),
    ]
    ids = {}
    for kode, nama, x, y in uc:
        ids[kode] = d.node("%s<br>%s" % (kode, nama), S_USECASE, x, y, 320, 66)

    # ------------------------------------------------------------
    # Aktor
    # ------------------------------------------------------------
    admin = d.node(
        "Admin Gudang<br>(ACT-01)<br><i>peran: admin &amp; operator</i>",
        S_ENTITAS,
        40,
        250,
        240,
        110,
    )
    baru = d.node("Pengguna Baru<br>(ACT-04)<br><i>non-user</i>", S_AKTOR, 1190, 170, 220, 100)
    petani = d.node("Petani<br>(ACT-02)<br><i>non-user</i>", S_ENTITAS, 1190, 370, 220, 100)
    distributor = d.node(
        "Distributor<br>(ACT-03)<br><i>non-user</i>", S_ENTITAS, 1190, 570, 220, 100
    )
    petani_terdaftar = d.node(
        "Petani Terdaftar<br>(ACT-05)<br><i>peran: petani</i>", S_AKTOR, 40, 640, 240, 100
    )

    # ------------------------------------------------------------
    # Relasi aktor - use case
    # ------------------------------------------------------------
    rel = [
        (admin, "UC-01", (1.0, 0.12), (0.0, 0.5)),
        (admin, "UC-02", (1.0, 0.38), (0.0, 0.5)),
        (admin, "UC-06", (1.0, 0.62), (0.0, 0.5)),
        (admin, "UC-09", (1.0, 0.86), (0.0, 0.5)),
        (admin, "UC-03", (1.0, 0.25), (0.0, 0.5)),
        (admin, "UC-04", (1.0, 0.50), (0.0, 0.5)),
        (admin, "UC-05", (1.0, 0.75), (0.0, 0.5)),
        (admin, "UC-07", (1.0, 0.95), (0.0, 0.5)),
        (baru, "UC-08", (0.0, 0.35), (1.0, 0.5)),
        (baru, "UC-01", (0.0, 0.85), (1.0, 0.85)),
        (petani, "UC-03", (0.0, 0.35), (1.0, 0.85)),
        (petani, "UC-04", (0.0, 0.85), (1.0, 0.85)),
        (distributor, "UC-05", (0.0, 0.35), (1.0, 0.85)),
        (distributor, "UC-07", (0.0, 0.85), (1.0, 0.85)),
        (petani_terdaftar, "UC-01", (1.0, 0.25), (0.0, 0.85)),
        (petani_terdaftar, "UC-02", (1.0, 0.60), (0.0, 0.85)),
        (petani_terdaftar, "UC-09", (1.0, 0.90), (0.0, 0.5)),
    ]
    for src, kode, keluar, masuk in rel:
        d.edge(src, ids[kode], "", S_EDGE(arrow="none", width=1.3), exit_xy=keluar, entry_xy=masuk)

    d.text(
        "Relasi seluruh use case merupakan Association. Peran 'petani' "
        "(ACT-05) hanya memperoleh hak akses baca atas Dashboard, sedangkan "
        "peran 'admin' dan 'operator' memperoleh akses penuh terhadap modul "
        "petani, panen, dan distribusi. Use case UC-08 Registrasi Akun Baru "
        "merupakan tambahan tahap UAS yang tidak tersedia pada versi UTS.",
        40,
        845,
        1620,
        50,
        S_CATATAN,
    )

    return d


# ============================================================
# 2. SEQUENCE DIAGRAM
# ============================================================
def _seq_header(d, title, subtitle, lifelines, width):
    """Menyusun kepala sequence diagram beserta lifeline."""
    _judul(d, title, subtitle, width)
    centers = []
    for name, sub in lifelines:
        x = 60 + len(centers) * 320
        lifeline(d, x, name, sub)
        centers.append(x + 105)
    return centers


def diagram_seq_login():
    """Sequence Diagram UC-01 Login ke Sistem AgriUno."""
    d = Diagram(
        "Sequence Diagram UC-01", 1700, 780, "Sequence Diagram UC-01 Login ke Sistem AgriUno"
    )
    c = _seq_header(
        d,
        "Sequence Diagram AgriUno  —  UC-01 Login ke Sistem AgriUno",
        "Verifikasi kredensial terhadap tabel users menggunakan hash SHA-256",
        [
            ("Admin Gudang", "pengguna"),
            (":SplashView", "views/splash_view.py"),
            (":LoginView", "views/login_view.py"),
            (":AuthController", "controllers/auth_controller.py"),
            (":UserModel", "models/user_model.py"),
            (":MySQL", "db: agriuno"),
        ],
        1700,
    )

    a, splash, login, auth, model, mysql = c

    message(d, a, 150, 520, "1. aplikasi dibuka  ->  jalankan_splash()")
    arrow(d, a, splash, 168)
    message(
        d,
        splash,
        186,
        900,
        "2. tampilkan logo + animasi pembuka (24 frame), progress bar, "
        "dan pesan status selama 3 detik",
    )
    arrow(d, splash, login, 204)
    message(d, a, 222, 520, "3. isi username dan password")
    arrow(d, a, login, 240)
    message(d, login, 258, 700, "4. klik 'Masuk Sistem'  ->  proses_login()")
    arrow(d, login, auth, 276)
    message(d, auth, 294, 640, "5. AuthController.login(username, password)")
    arrow(d, auth, model, 312)
    message(
        d, model, 330, 700, "6. SELECT ... FROM users WHERE username = %s  (prepared statement)"
    )
    arrow(d, model, mysql, 348)
    message(d, mysql, 366, 640, "7. id_user, username, password, salt, role")
    arrow(d, mysql, model, 384)
    message(d, model, 402, 760, "8. hash = SHA-256(salt + password)  ->  hmac.compare_digest()")
    arrow(d, model, auth, 420)
    message(d, auth, 438, 640, "9. (True, session)")
    arrow(d, auth, login, 456)

    # Percabangan.
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#f6fdfa;strokeColor=%s;"
        "strokeWidth=1.2;dashed=0;" % GARIS,
        60,
        490,
        1580,
        230,
    )
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.2;" % (HIJAU_TUA, HIJAU_TUA),
        60,
        490,
        1580,
        28,
    )
    d.text("alt [kredensial valid dan akun aktif]", 70, 492, 1560, 24, S_LABEL)

    message(d, login, 536, 700, "10. tampilkan status berhasil, tutup LoginView")
    arrow(d, login, splash, 554)
    message(
        d,
        splash,
        572,
        900,
        "11. bangun AgriUnoApp  ->  sidebar, halaman, dan Dashboard (show_page('dashboard'))",
    )
    arrow(d, splash, a, 590)

    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#fff7ed;strokeColor=%s;"
        "strokeWidth=1.2;" % ORANYE,
        60,
        720,
        1580,
        60,
    )
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.2;" % (ORANYE, ORANYE),
        60,
        720,
        1580,
        28,
    )
    d.text(
        "else [username tidak ditemukan / password salah / akun nonaktif]",
        70,
        722,
        1560,
        24,
        S_LABEL,
    )
    message(d, login, 748, 700, "12. tampilkan pesan inline 'Username atau Password salah!'")
    arrow(d, login, a, 766)

    return d


def diagram_seq_registrasi():
    """Sequence Diagram UC-08 Registrasi Akun Baru."""
    d = Diagram("Sequence Diagram UC-08", 1700, 800, "Sequence Diagram UC-08 Registrasi Akun Baru")
    c = _seq_header(
        d,
        "Sequence Diagram AgriUno  —  UC-08 Registrasi Akun Baru",
        "Pendaftaran akun khusus pengguna dengan salt acak dan hash SHA-256",
        [
            ("Pengguna Baru", "pengguna"),
            (":RegisterView", "views/register_view.py"),
            (":UserController", "controllers/user_controller.py"),
            (":UserModel", "models/user_model.py"),
            (":MySQL", "db: agriuno"),
        ],
        1700,
    )

    a, view, ctrl, model, mysql = c

    message(d, a, 150, 520, "1. klik 'Belum punya akun? Daftar di sini'")
    arrow(d, a, view, 168)
    message(d, view, 186, 640, "2. RegisterView tampil dengan peran Operator/Petani")
    arrow(d, view, a, 204)
    message(d, a, 222, 620, "3. isi nama lengkap, username, password, konfirmasi, dan peran")
    arrow(d, a, view, 240)
    message(d, view, 258, 700, "4. klik 'Daftar Sekarang'  ->  proses_registrasi()")
    arrow(d, view, ctrl, 276)
    message(d, ctrl, 294, 640, "5. UserController.daftar(...)")
    arrow(d, ctrl, model, 312)
    message(
        d,
        model,
        330,
        860,
        "6. validasi: username >= 4 karakter & unik, password >= 6 karakter, "
        "konfirmasi sama, peran harus 'operator' atau 'petani' (BR-06 s.d. BR-08)",
    )
    arrow(d, model, mysql, 348)
    message(d, mysql, 366, 700, "7. SELECT id_user FROM users WHERE username = %s")
    arrow(d, mysql, model, 384)
    message(d, model, 402, 860, "8. salt = generate_salt()  ->  hash = SHA-256(salt + password)")
    arrow(d, model, mysql, 420)
    message(
        d,
        mysql,
        438,
        780,
        "9. INSERT INTO users (username, password, salt, full_name, role, is_active) / commit()",
    )
    arrow(d, mysql, model, 456)
    message(d, model, 474, 640, "10. (True, 'Registrasi berhasil!')")
    arrow(d, model, ctrl, 492)
    message(d, ctrl, 510, 640, "11. (True, pesan)")
    arrow(d, ctrl, view, 528)
    message(d, view, 546, 700, "12. tampilkan konfirmasi dan kosongkan formulir")
    arrow(d, view, a, 564)

    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#fef2f2;strokeColor=%s;"
        "strokeWidth=1.2;dashed=0;" % MERAH,
        60,
        600,
        1580,
        140,
    )
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.2;" % (MERAH, MERAH),
        60,
        600,
        1580,
        28,
    )
    d.text("else [validasi gagal]", 70, 602, 1560, 24, S_LABEL)
    message(
        d,
        model,
        646,
        860,
        "13. (False, pesan galat)  -  username sudah digunakan / peran "
        "'admin' tidak dapat dipilih / konfirmasi password tidak sama",
    )
    arrow(d, model, view, 664)
    message(d, view, 682, 700, "14. tampilkan pesan galat pada formulir")
    arrow(d, view, a, 700)

    return d


def diagram_seq_petani():
    """Sequence Diagram UC-03 Mengelola Data Petani."""
    d = Diagram("Sequence Diagram UC-03", 1700, 840, "Sequence Diagram UC-03 Mengelola Data Petani")
    c = _seq_header(
        d,
        "Sequence Diagram AgriUno  —  UC-03 Mengelola Data Petani",
        "Operasi CRUD pada tabel petani melalui model dan basis data MySQL",
        [
            ("Admin Gudang", "pengguna"),
            (":PetaniView", "views/petani_view.py"),
            (":AgriUnoController", "controllers/controller.py"),
            (":PetaniModel", "models/petani_model.py"),
            (":DatabaseConnection", "config/database.py"),
            (":MySQL", "db: agriuno"),
        ],
        1700,
    )

    a, view, ctrl, model, db, mysql = c

    message(d, a, 150, 520, "1. isi form (nama, lokasi_lahan, komoditas_utama)")
    arrow(d, a, view, 168)
    message(d, view, 186, 700, "2. klik 'Simpan'  ->  simpan()")
    arrow(d, view, ctrl, 204)
    message(
        d,
        ctrl,
        222,
        760,
        "3. tambah_petani(nama, lokasi, komoditas)  ->  validasi kelengkapan dan panjang kolom",
    )
    arrow(d, ctrl, model, 240)
    message(d, model, 258, 700, "4. insert(nama, lokasi, komoditas)")
    arrow(d, model, db, 276)
    message(d, db, 294, 700, "5. with DatabaseConnection.cursor(commit=True)")
    arrow(d, db, mysql, 312)
    message(d, mysql, 330, 780, "6. INSERT INTO petani (...) / commit()")
    arrow(d, mysql, db, 348)
    message(d, db, 366, 640, "7. OK")
    arrow(d, db, model, 384)
    message(d, model, 402, 640, "8. True")
    arrow(d, model, ctrl, 420)
    message(d, ctrl, 438, 700, "9. (True, 'Data petani berhasil disimpan!')")
    arrow(d, ctrl, view, 456)
    message(d, view, 474, 700, "10. load_table()  ->  get_petani()  ->  get_all()")
    arrow(d, view, ctrl, 492)
    arrow(d, ctrl, model, 510)
    message(d, mysql, 528, 700, "11. SELECT * FROM petani ORDER BY nama_petani")
    arrow(d, mysql, view, 546)
    message(d, view, 564, 640, "12. isi tabel dan tampilkan kotak dialog sukses")
    arrow(d, view, a, 582)

    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#fff7ed;strokeColor=%s;"
        "strokeWidth=1.2;dashed=0;" % ORANYE,
        60,
        610,
        1580,
        90,
    )
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.2;" % (ORANYE, ORANYE),
        60,
        610,
        1580,
        28,
    )
    d.text("else [kolom wajib kosong / data tidak valid]", 70, 612, 1560, 24, S_LABEL)
    message(
        d, ctrl, 652, 760, "13. (False, 'Nama, lokasi lahan, dan komoditas utama wajib diisi!')"
    )
    arrow(d, ctrl, view, 670)
    arrow(d, view, a, 688)

    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#fef2f2;strokeColor=%s;"
        "strokeWidth=1.2;dashed=0;" % MERAH,
        60,
        710,
        1580,
        90,
    )
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.2;" % (MERAH, MERAH),
        60,
        710,
        1580,
        28,
    )
    d.text(
        "else [penghapusan: petani masih memiliki riwayat panen (BR-01)]",
        70,
        712,
        1560,
        24,
        S_LABEL,
    )
    message(
        d,
        model,
        752,
        860,
        "14. errno 1451  ->  (False, 'Gagal menghapus! Petani masih memiliki "
        "riwayat setoran panen aktif di gudang (BR-01).')",
    )
    arrow(d, model, view, 770)
    arrow(d, view, a, 788)

    return d


def diagram_seq_panen():
    """Sequence Diagram UC-04 Mencatat Setoran Panen."""
    d = Diagram(
        "Sequence Diagram UC-04", 1700, 800, "Sequence Diagram UC-04 Mencatat Setoran Panen"
    )
    c = _seq_header(
        d,
        "Sequence Diagram AgriUno  —  UC-04 Mencatat Setoran Panen",
        "Pencatatan lot panen dengan validasi penyetor dan perhitungan sisa stok",
        [
            ("Admin Gudang", "pengguna"),
            (":PanenView", "views/panen_view.py"),
            (":AgriUnoController", "controllers/controller.py"),
            (":PanenModel", "models/panen_model.py"),
            (":MySQL", "db: agriuno"),
        ],
        1700,
    )

    a, view, ctrl, model, mysql = c

    message(
        d,
        a,
        150,
        620,
        "1. pilih petani penyetor pada kotak daftar, isi jenis komoditas, berat, dan tanggal",
    )
    arrow(d, a, view, 168)
    message(d, view, 186, 700, "2. klik 'Simpan'  ->  simpan()")
    arrow(d, view, ctrl, 204)
    message(
        d,
        ctrl,
        222,
        820,
        "3. tambah_panen(id_petani, jenis, berat, tanggal)  ->  validasi kolom, "
        "float(berat) > 0, tanggal YYYY-MM-DD",
    )
    arrow(d, ctrl, model, 240)
    message(d, model, 258, 700, "4. exists(id_petani)  ->  BR-01")
    arrow(d, model, mysql, 276)
    message(d, mysql, 294, 700, "5. SELECT id_petani FROM petani WHERE id_petani = %s")
    arrow(d, mysql, model, 312)
    message(d, model, 330, 700, "6. insert(id_petani, jenis, berat, tanggal)")
    arrow(d, model, mysql, 348)
    message(d, mysql, 366, 780, "7. INSERT INTO inventori_panen (...) / commit()")
    arrow(d, mysql, model, 384)
    message(d, model, 402, 640, "8. True")
    arrow(d, model, ctrl, 420)
    message(d, ctrl, 438, 700, "9. (True, 'Setoran panen berhasil dicatat!')")
    arrow(d, ctrl, view, 456)
    message(
        d,
        view,
        474,
        900,
        "10. load_table()  ->  get_panen()  ->  get_all() dengan LEFT JOIN "
        "dan perhitungan sisa_stok = jumlah_berat - SUM(jumlah_dikirim)",
    )
    arrow(d, view, ctrl, 492)
    arrow(d, ctrl, model, 510)
    message(
        d,
        mysql,
        528,
        820,
        "11. SELECT ... COALESCE(SUM(d.jumlah_dikirim),0) AS total_dikirim, "
        "(p.jumlah_berat - ...) AS sisa_stok",
    )
    arrow(d, mysql, view, 546)
    message(d, view, 564, 700, "12. tampilkan kolom Sisa Stok dan kotak dialog sukses")
    arrow(d, view, a, 582)

    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#fef2f2;strokeColor=%s;"
        "strokeWidth=1.2;dashed=0;" % MERAH,
        60,
        610,
        1580,
        140,
    )
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.2;" % (MERAH, MERAH),
        60,
        610,
        1580,
        28,
    )
    d.text("else [validasi gagal]", 70, 612, 1560, 24, S_LABEL)
    message(
        d,
        ctrl,
        652,
        900,
        "13. (False, ...)  -  'Seluruh kolom setoran panen wajib diisi!' / "
        "'Jumlah berat harus berupa angka numerik!' / 'Jumlah berat panen "
        "harus berupa angka positif!' / 'Tanggal panen harus berformat "
        "YYYY-MM-DD!' / 'ID Petani tidak terdaftar di sistem!'",
    )
    arrow(d, ctrl, view, 670)
    arrow(d, view, a, 688)

    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#fef2f2;strokeColor=%s;"
        "strokeWidth=1.2;dashed=0;" % MERAH,
        60,
        760,
        1580,
        70,
    )
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.2;" % (MERAH, MERAH),
        60,
        760,
        1580,
        28,
    )
    d.text(
        "else [pembaruan: berat baru di bawah total yang sudah dialokasikan (BR-02)]",
        70,
        762,
        1560,
        24,
        S_LABEL,
    )
    message(
        d,
        ctrl,
        796,
        1000,
        "14. (False, 'Berat baru lebih kecil daripada total yang sudah "
        "dialokasikan. Ubah alokasi distribusi terlebih dahulu.')",
    )
    return d


def diagram_seq_distribusi():
    """Sequence Diagram UC-05 Mengalokasikan Pengiriman."""
    d = Diagram(
        "Sequence Diagram UC-05", 1700, 860, "Sequence Diagram UC-05 Mengalokasikan Pengiriman"
    )
    c = _seq_header(
        d,
        "Sequence Diagram AgriUno  —  UC-05 Mengalokasikan Pengiriman",
        "Validasi stok dalam satu transaksi dengan penguncian baris (FOR UPDATE)",
        [
            ("Admin Gudang", "pengguna"),
            (":DistribusiView", "views/distribusi_view.py"),
            (":AgriUnoController", "controllers/controller.py"),
            (":DistribusiModel", "models/distribusi_model.py"),
            (":MySQL", "db: agriuno"),
        ],
        1700,
    )

    a, view, ctrl, model, mysql = c

    message(
        d,
        a,
        150,
        640,
        "1. pilih lot panen pada kotak daftar, isi tujuan pengiriman dan jumlah dikirim",
    )
    arrow(d, a, view, 168)
    message(d, view, 186, 700, "2. klik 'Simpan'  ->  simpan()")
    arrow(d, view, ctrl, 204)
    message(
        d,
        ctrl,
        222,
        820,
        "3. tambah_distribusi(id_panen, tujuan, jumlah)  ->  validasi kolom dan jumlah > 0",
    )
    arrow(d, ctrl, model, 240)
    message(
        d,
        model,
        258,
        900,
        "4. create_with_stock_check(id_panen, tujuan, jumlah, 'Diproses')  ->  BEGIN TRANSACTION",
    )
    arrow(d, model, mysql, 276)
    message(
        d,
        mysql,
        294,
        1000,
        "5. SELECT p.jumlah_berat, COALESCE(SUM(d.jumlah_dikirim),0) "
        "FROM inventori_panen p LEFT JOIN distribusi d ... FOR UPDATE",
    )
    arrow(d, mysql, model, 312)
    message(d, model, 330, 760, "6. sisa_stok = jumlah_berat - total_dikirim")
    arrow(d, model, mysql, 348)
    message(
        d,
        mysql,
        366,
        900,
        "7. INSERT INTO distribusi (id_panen, tujuan_pengiriman, "
        "jumlah_dikirim, status_pengiriman) VALUES (..., 'Diproses') / commit()",
    )
    arrow(d, mysql, model, 384)
    message(d, model, 402, 640, "8. (True, id_distribusi)")
    arrow(d, model, ctrl, 420)
    message(
        d,
        ctrl,
        438,
        700,
        "9. (True, 'Alokasi pengiriman berhasil dibuat (Status Awal: Diproses)!')",
    )
    arrow(d, ctrl, view, 456)
    message(
        d,
        view,
        474,
        760,
        "10. load_table() dan load_panen()  ->  muat ulang tabel alokasi "
        "serta daftar lot beserta sisa stok",
    )
    arrow(d, view, a, 492)

    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#fef2f2;strokeColor=%s;"
        "strokeWidth=1.2;dashed=0;" % MERAH,
        60,
        520,
        1580,
        140,
    )
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.2;" % (MERAH, MERAH),
        60,
        520,
        1580,
        28,
    )
    d.text("else [jumlah kirim melebihi sisa stok (BR-02)]", 70, 522, 1560, 24, S_LABEL)
    message(
        d,
        model,
        562,
        900,
        "11. (False, 'Jumlah kirim melebihi sisa stok inventori yang tersedia "
        "di gudang! (Sisa: 90.00 Kg)')  ->  ROLLBACK",
    )
    arrow(d, model, ctrl, 580)
    message(d, ctrl, 598, 760, "12. (False, pesan)  ->  kotak dialog 'Validasi Stok (BR-02)'")
    arrow(d, ctrl, view, 616)
    arrow(d, view, a, 634)

    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#fef2f2;strokeColor=%s;"
        "strokeWidth=1.2;dashed=0;" % MERAH,
        60,
        670,
        1580,
        140,
    )
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.2;" % (MERAH, MERAH),
        60,
        670,
        1580,
        28,
    )
    d.text(
        "else [alokasi berstatus 'Terkirim'  ->  bersifat final (BR-09)]",
        70,
        672,
        1560,
        24,
        S_LABEL,
    )
    message(
        d,
        model,
        712,
        900,
        "13. (False, 'Alokasi berstatus 'Terkirim' bersifat final dan tidak "
        "dapat diubah/dihapus (BR-09).')",
    )
    arrow(d, model, view, 730)
    arrow(d, view, a, 748)

    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#eef5f0;strokeColor=%s;"
        "strokeWidth=1.2;dashed=0;" % HIJAU_MUDA,
        60,
        790,
        1580,
        60,
    )
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.2;" % (HIJAU_TUA, HIJAU_TUA),
        60,
        790,
        1580,
        28,
    )
    d.text(
        "opt [Ubah Status Pengiriman - hanya tiga nilai baku (BR-05)]", 70, 792, 1560, 24, S_LABEL
    )
    message(
        d,
        view,
        826,
        900,
        "14. ubah_status_distribusi(id, status)  ->  UPDATE distribusi "
        "SET status_pengiriman = %s WHERE id_distribusi = %s / commit()",
    )
    return d


# ============================================================
# 3. ACTIVITY DIAGRAM
# ============================================================
def diagram_activity():
    """Activity Diagram alur alokasi pengiriman."""
    d = Diagram(
        "Activity Diagram AgriUno", 1520, 1200, "Activity Diagram AgriUno - Alur Alokasi Pengiriman"
    )
    _judul(
        d,
        "Activity Diagram AgriUno  \u2014  Alur Alokasi Pengiriman",
        "Dua keputusan: kelengkapan masukan dan ketersediaan sisa stok",
        1520,
    )

    # ------------------------------------------------------------
    # Swimlane
    # ------------------------------------------------------------
    d.node("", S_SWIMLANE, 0, 90, 520, 1080)
    d.node("", S_SWIMLANE, 520, 90, 1000, 1080)
    d.node("", S_SWIMLANE_HEADER, 0, 90, 520, 36)
    d.node("", S_SWIMLANE_HEADER, 520, 90, 1000, 36)
    d.text("Admin Gudang", 0, 94, 520, 28, S_SWIMLANE_HEADER)
    d.text("Sistem AgriUno", 520, 94, 1000, 28, S_SWIMLANE_HEADER)

    lbl = S_MSG.replace("fontSize=13", "fontSize=12").replace("align=left", "align=center")

    # ------------------------------------------------------------
    # Simpul
    # ------------------------------------------------------------
    d.node("", S_AWAL, 232, 140, 56, 30)
    d.text("Mulai", 232, 143, 56, 26, lbl.replace("fontColor=#1f2937", "fontColor=#ffffff"))

    d.node("Membuka menu \u201cDistribusi\u201d", S_ACTIVITAS, 60, 200, 400, 52)
    d.node("Memilih lot panen pada kotak daftar", S_ACTIVITAS, 60, 285, 400, 52)
    d.node("Mengisi Tujuan Pengiriman dan Jumlah Dikirim", S_ACTIVITAS, 60, 370, 400, 52)
    d.node("Mengklik tombol \u201cSimpan\u201d", S_ACTIVITAS, 60, 455, 400, 52)

    d.node("Validasi kolom terisi dan jumlah &gt; 0", S_ACTIVITAS, 640, 455, 340, 56)
    d.node("Tampilkan pesan galat validasi input", S_ERROR, 1120, 455, 340, 56)

    d.node("Lengkap dan valid?", S_KEPUTUSAN, 660, 555, 300, 70)
    d.node(
        "Kunci baris lot dan hitung sisa stok<br>(SELECT ... FOR UPDATE)",
        S_ACTIVITAS,
        640,
        675,
        340,
        62,
    )
    d.node("Jumlah kirim &le; sisa stok?", S_KEPUTUSAN, 660, 785, 300, 70)
    d.node(
        "Tampilkan pesan \u201cJumlah kirim melebihi<br>sisa stok inventori\u201d (BR-02)",
        S_ERROR,
        1120,
        785,
        340,
        62,
    )
    d.node(
        "Simpan alokasi ke D3 distribusi dengan status<br>awal \u201cDiproses\u201d (BR-04)",
        S_ACTIVITAS,
        640,
        905,
        340,
        62,
    )
    d.node("Muat ulang tabel alokasi dan daftar lot", S_ACTIVITAS, 640, 1005, 340, 56)
    d.node("Tampilkan kotak dialog sukses", S_ACTIVITAS, 60, 1005, 400, 52)

    d.node("", S_AKHIR, 232, 1105, 56, 30)
    d.text("Selesai", 232, 1108, 56, 26, lbl)

    # ------------------------------------------------------------
    # Aliran
    # ------------------------------------------------------------
    arrow_v(d, 260, 170, 200)
    arrow_v(d, 260, 252, 285)
    arrow_v(d, 260, 337, 370)
    arrow_v(d, 260, 422, 455)
    arrow_h(d, 483, 460, 640)
    arrow_v(d, 810, 511, 555)
    arrow_h(d, 590, 960, 1120)
    arrow_v(d, 810, 625, 675)
    arrow_v(d, 810, 737, 785)
    arrow_h(d, 816, 960, 1120)
    arrow_v(d, 810, 855, 905)
    arrow_v(d, 810, 967, 1005)
    arrow_h(d, 1033, 640, 460)
    arrow_v(d, 260, 1057, 1105)

    d.text("Tidak", 985, 558, 80, 20, lbl)
    d.text("Ya", 700, 640, 60, 20, lbl)
    d.text("Tidak", 985, 784, 80, 20, lbl)
    d.text("Ya", 700, 870, 60, 20, lbl)

    d.text(
        "Catatan: alur di atas mengikuti implementasi AgriUnoController."
        "tambah_distribusi() dan DistribusiModel.create_with_stock_check(), "
        "yaitu pemeriksaan stok dan penyimpanan alokasi dijalankan dalam satu "
        "transaksi basis data dengan penguncian baris (FOR UPDATE) sehingga "
        "dua permintaan bersamaan tidak dapat menimbulkan stok minus.",
        560,
        1085,
        940,
        60,
        S_CATATAN,
    )

    return d


def diagram_activity_splash():
    """Activity Diagram alur splash dan animasi logo."""
    d = Diagram(
        "Activity Diagram Splash AgriUno",
        1260,
        1080,
        "Activity Diagram AgriUno - Alur Splash dan Animasi Logo",
    )
    _judul(
        d,
        "Activity Diagram AgriUno  \u2014  Alur Splash dan Animasi Logo",
        "Proses pembukaan aplikasi hingga jendela login tampil",
        1260,
    )

    d.node("", S_SWIMLANE, 0, 90, 560, 960)
    d.node("", S_SWIMLANE, 560, 90, 700, 960)
    d.node("", S_SWIMLANE_HEADER, 0, 90, 560, 36)
    d.node("", S_SWIMLANE_HEADER, 560, 90, 700, 36)
    d.text("Aplikasi AgriUno", 0, 94, 560, 28, S_SWIMLANE_HEADER)
    d.text("Sistem dan Pewaktu", 560, 94, 700, 28, S_SWIMLANE_HEADER)

    lbl = S_MSG.replace("fontSize=13", "fontSize=12").replace("align=left", "align=center")

    d.node("", S_AWAL, 252, 140, 56, 30)
    d.text("Mulai", 252, 143, 56, 26, lbl.replace("fontColor=#1f2937", "fontColor=#ffffff"))
    d.node("jalankan_splash()  \u2192  buat objek SplashView", S_ACTIVITAS, 60, 200, 440, 52)
    d.node("Muat 24 frame logo PNG dan wordmark", S_ACTIVITAS, 660, 200, 460, 52)
    d.node(
        "Tampilkan logo dengan animasi skala dan opasitas<br>(ease-out cubic)",
        S_ACTIVITAS,
        660,
        290,
        460,
        62,
    )
    d.node("Putar cincin orbit titik pada Canvas", S_ACTIVITAS, 660, 380, 460, 52)
    d.node("Isi progress bar 0% \u2014 100%", S_ACTIVITAS, 660, 460, 460, 52)
    d.node("Ganti pesan status secara bertahap", S_ACTIVITAS, 660, 540, 460, 52)
    d.node("SplashView._tick() dipanggil setiap 45 ms", S_ACTIVITAS, 60, 460, 440, 52)
    d.node("Animasi selesai?", S_KEPUTUSAN, 700, 640, 240, 76)
    d.node("destroy() splash  \u2192  panggil on_finish()", S_ACTIVITAS, 60, 790, 440, 52)
    d.node("Tampilkan jendela LoginView", S_ACTIVITAS, 660, 790, 460, 52)
    d.node("", S_AKHIR, 252, 900, 56, 30)
    d.text("Selesai", 252, 903, 56, 26, lbl)

    arrow_v(d, 280, 170, 200)
    arrow_h(d, 226, 500, 660)
    arrow_v(d, 890, 252, 290)
    arrow_v(d, 890, 352, 380)
    arrow_v(d, 890, 432, 460)
    arrow_v(d, 890, 512, 540)
    arrow_v(d, 890, 592, 640)
    arrow_h(d, 678, 700, 280)
    arrow_v(d, 280, 678, 790)
    arrow_v(d, 280, 842, 900)
    arrow_h(d, 816, 500, 660)
    arrow_v(d, 890, 842, 900)

    d.text("Belum selesai", 960, 646, 180, 20, lbl)
    d.text("Selesai", 700, 716, 90, 20, lbl)

    d.text(
        "Catatan: seluruh frame logo telah diprarender terlebih dahulu pada "
        "folder assets/anim sehingga aplikasi tidak memerlukan pustaka Pillow "
        "saat dijalankan. Durasi animasi dapat diatur melalui parameter "
        "duration_ms pada kelas SplashView.",
        60,
        970,
        1140,
        60,
        S_CATATAN,
    )

    return d
