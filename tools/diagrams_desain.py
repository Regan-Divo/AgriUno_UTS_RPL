"""
==========================================================
DIAGRAM KELAS, ERD, ARSITEKTUR, DAN NAVIGASI - AGRIUNO (UAS)
==========================================================
Pembangkitan Class Diagram, Entity Relationship Diagram, Diagram
Arsitektur Sistem, dan Diagram Navigasi AgriUno versi UAS.
"""

from diagram_builder import (
    HIJAU_TUA,
    LATAR,
    S_ACTIVITAS,
    S_AKTOR,
    S_AWAL,
    S_BOX,
    S_BOX_HEADER,
    S_CATATAN,
    S_EDGE,
    S_EDGE_PLAIN,
    S_ENTITAS,
    S_ERROR,
    S_JUDUL,
    S_KEPUTUSAN,
    S_LINE,
    S_MSG,
    S_SISTEM,
    S_SUBJUDUL,
    TEKS,
    Diagram,
    arrow_h,
    arrow_v,
)

JUDUL_SISTEM = "Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal"


def _judul(diag, judul, subjudul, width):
    """Menambahkan judul dan subjudul diagram."""
    diag.text(judul, 0, 16, width, 34, S_JUDUL)
    if subjudul:
        diag.text(subjudul, 0, 48, width, 22, S_SUBJUDUL)


def _class_box(diag, x, y, w, name, file_name, catatan, attributes, methods):
    """Menyusun kotak kelas pada class diagram.

    Mengembalikan id simpul utama agar relasi dapat digambar dengan
    perutean otomatis oleh draw.io.
    """
    attr_h = 19 * max(1, len(attributes))
    meth_h = 19 * max(1, len(methods))
    total = 60 + attr_h + meth_h + 8

    body = diag.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;"
        "strokeColor=%s;strokeWidth=1.6;fontSize=14;align=center;"
        "verticalAlign=middle;" % (LATAR, HIJAU_TUA),
        x,
        y,
        w,
        total,
    )
    diag.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.6;fontSize=15;fontStyle=1;fontColor=#ffffff;"
        "align=center;verticalAlign=middle;" % (HIJAU_TUA, HIJAU_TUA),
        x,
        y,
        w,
        38,
    )
    diag.text(
        name,
        x + 4,
        y + 3,
        w - 8,
        20,
        S_MSG.replace("align=left", "align=center")
        .replace("fontSize=13", "fontSize=15")
        .replace("fontColor=#1f2937", "fontColor=#ffffff")
        .replace("fontStyle=0", "fontStyle=1"),
    )
    diag.text(
        file_name,
        x + 4,
        y + 22,
        w - 8,
        14,
        S_MSG.replace("align=left", "align=center")
        .replace("fontSize=13", "fontSize=11")
        .replace("fontColor=#1f2937", "fontColor=#cbd5e1"),
    )
    diag.line(x, y + 38, x + w, y + 38, S_LINE)

    diag.text(catatan, x + 8, y + 41, w - 16, 17, S_MSG.replace("fontSize=13", "fontSize=11"))
    diag.line(x, y + 60, x + w, y + 60, S_LINE)
    diag.text(
        "<br>".join(attributes) if attributes else "",
        x + 8,
        y + 62,
        w - 16,
        attr_h,
        S_MSG.replace("fontSize=13", "fontSize=11"),
    )
    diag.line(x, y + 62 + attr_h, x + w, y + 62 + attr_h, S_LINE)
    diag.text(
        "<br>".join(methods) if methods else "",
        x + 8,
        y + 64 + attr_h,
        w - 16,
        meth_h,
        S_MSG.replace("fontSize=13", "fontSize=11"),
    )

    return body


def _relasi(diag, a, b, label, stereotype="uses", warna=TEKS, offset=(0, 0)):
    """Menyusun garis relasi berlabel antara dua kelas."""
    dashed = "1" if stereotype == "uses" else "0"
    style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor=%s;"
        "strokeWidth=1.3;endArrow=open;endFill=0;dashed=%s;"
        "labelBackgroundColor=#ffffff;fontSize=11;fontColor=%s;"
        "labelBorderColor=#FFFFFF;exitX=0.5;exitY=0.5;exitDx=0;exitDy=0;"
        "entryX=0.5;entryY=0.5;entryDx=0;entryDy=0;" % (warna, dashed, TEKS)
    )
    teks = label
    if stereotype == "extends":
        teks = "<<extends>>"
    elif stereotype == "komposisi" and not label:
        teks = "<<creates>>"
    return diag.edge(a, b, teks, style, label_offset=offset)


def diagram_class():
    """Class Diagram AgriUno."""
    d = Diagram("Class Diagram AgriUno", 1780, 1500, "Class Diagram AgriUno")
    _judul(
        d,
        "Class Diagram AgriUno",
        "Seluruh kelas yang benar-benar terdapat pada kode sumber versi UAS",
        1780,
    )

    # --- Lapisan 1: view dan entry point ---
    splash = _class_box(
        d,
        40,
        100,
        320,
        "SplashView",
        "views/splash_view.py",
        "jendela pemuatan (bukan turunan CTkFrame)",
        [
            "- on_finish : Callable",
            "- frames : list[PhotoImage]",
            "- progress : CTkProgressBar",
            "- status_label : CTkLabel",
        ],
        [
            "+ __init__(on_finish)",
            "+ _tick()",
            "+ _draw_orbit()",
            "+ _update_status()",
            "+ _finish()",
        ],
    )

    login = _class_box(
        d,
        400,
        100,
        320,
        "LoginView",
        "views/login_view.py",
        "jendela login (turunan CTk)",
        [
            "- on_login_success : Callable",
            "- e_user : CTkEntry",
            "- e_pass : CTkEntry",
            "- lbl_error : CTkLabel",
        ],
        ["+ __init__(on_login_success)", "+ proses_login()", "+ _place_logo()"],
    )

    register = _class_box(
        d,
        760,
        100,
        320,
        "RegisterView",
        "views/register_view.py",
        "jendela registrasi akun baru",
        [
            "- on_success : Callable",
            "- e_nama : CTkEntry",
            "- e_user : CTkEntry",
            "- e_pass : CTkEntry",
            "- e_pass2 : CTkEntry",
            "- opt_peran : CTkOptionMenu",
        ],
        ["+ __init__(on_success)", "+ proses_registrasi()", "+ _peran_terpilih()"],
    )

    app = _class_box(
        d,
        1120,
        100,
        320,
        "AgriUnoApp",
        "main.py",
        "jendela utama (turunan CTk)",
        [
            "- user : dict",
            "- pages : dict[str, CTkFrame]",
            "- nav_buttons : dict[str, CTkButton]",
            "- content : CTkFrame",
        ],
        [
            "+ __init__(user)",
            "+ show_page(page_name)",
            "+ _build_sidebar()",
            "+ _build_content()",
            "+ keluar()",
        ],
    )

    # --- Lapisan 2: halaman utama ---
    dashboard = _class_box(
        d,
        40,
        400,
        300,
        "DashboardView",
        "views/dashboard_view.py",
        "halaman ringkasan operasional",
        [
            "- controller : AgriUnoController",
            "- lbl_p : CTkLabel",
            "- lbl_h : CTkLabel",
            "- lbl_d : CTkLabel",
            "- indicators : dict",
        ],
        ["+ load_data()", "+ create_stat_card()", "+ create_progress_indicator()"],
    )

    petani_view = _class_box(
        d,
        370,
        400,
        300,
        "PetaniView",
        "views/petani_view.py",
        "halaman pengelolaan data petani",
        ["- controller : AgriUnoController", "- selected_id", "- tree : ttk.Treeview"],
        ["+ load_table()", "+ simpan()", "+ ubah()", "+ hapus()", "+ on_select()"],
    )

    panen_view = _class_box(
        d,
        700,
        400,
        300,
        "PanenView",
        "views/panen_view.py",
        "halaman inventori panen",
        [
            "- controller : AgriUnoController",
            "- selected_id",
            "- opt_petani : CTkOptionMenu",
            "- _petani_map : dict",
        ],
        [
            "+ load_table()",
            "+ load_petani()",
            "+ simpan()",
            "+ ubah()",
            "+ hapus()",
            "+ on_select()",
        ],
    )

    distribusi_view = _class_box(
        d,
        1030,
        400,
        300,
        "DistribusiView",
        "views/distribusi_view.py",
        "halaman alokasi distribusi",
        [
            "- controller : AgriUnoController",
            "- selected_id",
            "- opt_panen : CTkOptionMenu",
            "- opt_status : CTkOptionMenu",
            "- _panen_map : dict",
        ],
        [
            "+ load_table()",
            "+ load_panen()",
            "+ simpan()",
            "+ ubah()",
            "+ hapus()",
            "+ on_select()",
        ],
    )

    agri_controller = _class_box(
        d,
        1370,
        400,
        350,
        "AgriUnoController",
        "controllers/controller.py",
        "kelas utilitas - seluruh metode statis",
        ["(tanpa state; menyimpan konstanta aturan bisnis)"],
        [
            "+ get_petani() / tambah_petani() / update_petani() / hapus_petani()",
            "+ get_panen() / tambah_panen() / update_panen() / hapus_panen()",
            "+ get_distribusi() / tambah_distribusi()",
            "+ update_distribusi() / ubah_status_distribusi() / hapus_distribusi()",
            "+ get_statistik()",
        ],
    )

    # --- Lapisan 3: controller ---
    auth_controller = _class_box(
        d,
        40,
        760,
        320,
        "AuthController",
        "controllers/auth_controller.py",
        "kelas utilitas - seluruh metode statis",
        ["+ session : Session"],
        [
            "+ login(username, password)",
            "+ logout()",
            "+ register(...)",
            "+ current_user()",
            "+ boleh(aksi)",
            "+ daftar_akun()",
            "+ set_akun_aktif()",
            "+ hapus_akun()",
            "+ ubah_password()",
        ],
    )

    user_controller = _class_box(
        d,
        400,
        760,
        320,
        "UserController",
        "controllers/user_controller.py",
        "kelas utilitas - seluruh metode statis",
        ["(tanpa state)"],
        [
            "+ daftar(...)",
            "+ daftar_akun()",
            "+ ubah_profil()",
            "+ ubah_password()",
            "+ aktifkan()",
            "+ nonaktifkan()",
            "+ hapus()",
            "+ boleh_kelola_pengguna()",
        ],
    )

    session = _class_box(
        d,
        760,
        760,
        320,
        "Session",
        "controllers/auth_controller.py",
        "penyimpan state sesi pengguna",
        [
            "- user : dict",
            "- role : str",
            "- username : str",
            "- full_name : str",
            "- id_user : int",
        ],
        [
            "+ aktif()",
            "+ set_user(user)",
            "+ capabilities()",
            "+ boleh(aksi)",
            "+ label_peran",
            "+ ringkasan()",
            "+ reset()",
        ],
    )

    base_model = _class_box(
        d,
        1120,
        760,
        320,
        "BaseModel",
        "models/base_model.py",
        "kelas utilitas - seluruh metode statis",
        ["(tanpa state)"],
        [
            "+ _execute_write(sql, params)",
            "+ _fetch_all(sql, params)",
            "+ _fetch_one(sql, params)",
            "+ to_decimal(value)",
            "+ format_berat(value)",
            "+ _is_foreign_key_violation(err)",
        ],
    )

    # --- Lapisan 4: model ---
    user_model = _class_box(
        d,
        40,
        1130,
        320,
        "UserModel",
        "models/user_model.py",
        "kelas utilitas - seluruh metode statis",
        ["(tanpa state)"],
        [
            "+ hash_password(password, salt)",
            "+ generate_salt()",
            "+ verify_password(password, salt, stored_hash)",
            "+ authenticate(username, password)",
            "+ register(...)",
            "+ get_all() / get_by_username() / username_exists()",
            "+ update_profile() / change_password() / set_active() / delete()",
        ],
    )

    petani_model = _class_box(
        d,
        400,
        1130,
        300,
        "PetaniModel",
        "models/petani_model.py",
        "kelas utilitas - seluruh metode statis",
        ["(tanpa state)"],
        [
            "+ get_all() / get_by_id() / exists()",
            "+ count() / count_petani_aktif()",
            "+ insert() / update() / delete()",
        ],
    )

    panen_model = _class_box(
        d,
        730,
        1130,
        300,
        "PanenModel",
        "models/panen_model.py",
        "kelas utilitas - seluruh metode statis",
        ["(tanpa state)"],
        [
            "+ get_all() / get_by_id()",
            "+ get_sisa_stok(id_panen)",
            "+ get_total_terkirim(id_panen)",
            "+ count() / total_berat()",
            "+ insert() / update() / delete()",
        ],
    )

    distribusi_model = _class_box(
        d,
        1060,
        1130,
        300,
        "DistribusiModel",
        "models/distribusi_model.py",
        "kelas utilitas - seluruh metode statis",
        ["(tanpa state)"],
        [
            "+ get_all() / get_by_id()",
            "+ create_with_stock_check()",
            "+ update_with_stock_check()",
            "+ count() / count_by_status()",
            "+ total_dikirim()",
            "+ insert() / update() / delete()",
            "+ valid_status() / is_locked()",
        ],
    )

    database = _class_box(
        d,
        1390,
        1130,
        330,
        "DatabaseConnection",
        "config/database.py",
        "pabrik koneksi MySQL",
        ["- DB_HOST / DB_PORT / DB_USER", "- DB_PASSWORD / DB_NAME"],
        ["+ connect(database) : Connection", "+ cursor(dictionary, commit)", "+ ping() : bool"],
    )

    # ------------------------------------------------------------
    # Relasi
    # ------------------------------------------------------------
    _relasi(d, splash, login, "<<creates>>", "komposisi", HIJAU_TUA)
    _relasi(d, login, register, "<<creates>>", "komposisi", HIJAU_TUA)
    _relasi(d, login, auth_controller, "<<uses>>")
    _relasi(d, register, user_controller, "<<uses>>")
    _relasi(d, auth_controller, session, "<<owns>>", "komposisi", HIJAU_TUA)
    _relasi(d, auth_controller, user_model, "<<uses>>")
    _relasi(d, user_controller, user_model, "<<uses>>")

    _relasi(d, app, dashboard, "1 .. *")
    _relasi(d, app, petani_view, "")
    _relasi(d, app, panen_view, "")
    _relasi(d, app, distribusi_view, "")

    _relasi(d, dashboard, agri_controller, "<<uses>>")
    _relasi(d, petani_view, agri_controller, "<<uses>>")
    _relasi(d, panen_view, agri_controller, "<<uses>>")
    _relasi(d, distribusi_view, agri_controller, "<<uses>>")

    _relasi(d, agri_controller, petani_model, "<<uses>>")
    _relasi(d, agri_controller, panen_model, "<<uses>>")
    _relasi(d, agri_controller, distribusi_model, "<<uses>>")

    _relasi(d, user_model, base_model, "", "extends")
    _relasi(d, petani_model, base_model, "", "extends")
    _relasi(d, panen_model, base_model, "", "extends")
    _relasi(d, distribusi_model, base_model, "", "extends")
    _relasi(d, base_model, database, "<<uses>>")

    d.text(
        "Catatan: seluruh kelas model dan controller bersifat utilitas "
        "(metode statis) tanpa menyimpan state. Objek Session pada "
        "controllers/auth_controller.py merupakan satu-satunya penyimpan "
        "state aplikasi, yaitu profil pengguna yang sedang login beserta "
        "perannya. Hubungan <<extends>> menandakan pewarisan BaseModel.",
        40,
        1400,
        1680,
        70,
        S_CATATAN,
    )

    return d


# ============================================================
# 2. ENTITY RELATIONSHIP DIAGRAM
# ============================================================
def _entitas(diag, x, y, w, h, nama, baris, lebar_kolom=380):
    """Menyusun satu entitas pada ERD."""
    diag.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.6;" % (LATAR, HIJAU_TUA),
        x,
        y,
        w,
        h,
    )
    diag.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.6;fontSize=18;fontStyle=1;fontColor=#ffffff;"
        "align=center;verticalAlign=middle;" % (HIJAU_TUA, HIJAU_TUA),
        x,
        y,
        w,
        36,
    )
    diag.text(
        nama,
        x + 4,
        y + 6,
        w - 8,
        24,
        S_MSG.replace("align=left", "align=center")
        .replace("fontSize=13", "fontSize=18")
        .replace("fontColor=#1f2937", "fontColor=#ffffff")
        .replace("fontStyle=0", "fontStyle=1"),
    )
    for nomor, isi_baris in enumerate(baris):
        yy = y + 42 + nomor * 24
        diag.text(isi_baris, x + 12, yy, w - 24, 22, S_MSG.replace("fontSize=13", "fontSize=14"))


def diagram_erd():
    """Entity Relationship Diagram AgriUno."""
    d = Diagram(
        "Entity Relationship Diagram AgriUno", 1560, 900, "Entity Relationship Diagram AgriUno"
    )
    _judul(
        d,
        "Entity Relationship Diagram (ERD) AgriUno",
        "Empat tabel: users, petani, inventori_panen, dan distribusi",
        1560,
    )

    _entitas(
        d,
        60,
        150,
        430,
        218,
        "users",
        [
            "PK  id_user            INT (AI)",
            "     username          VARCHAR(50) UNIQUE",
            "     password          VARCHAR(255)  &lt;hash SHA-256&gt;",
            "     salt              VARCHAR(64)",
            "     full_name         VARCHAR(100)",
            "     role              ENUM('admin','operator','petani')",
            "     is_active         TINYINT(1) DEFAULT 1",
        ],
    )

    petani = _entitas(
        d,
        60,
        500,
        430,
        142,
        "petani",
        [
            "PK  id_petani          INT (AI)",
            "     nama_petani        VARCHAR(100)",
            "     lokasi_lahan       VARCHAR(150)",
            "     komoditas_utama    VARCHAR(100)",
        ],
    )

    panen = _entitas(
        d,
        570,
        480,
        460,
        190,
        "inventori_panen",
        [
            "PK  id_panen           INT (AI)",
            "FK  id_petani          INT  &gt;- petani",
            "     jenis_komoditas    VARCHAR(100)",
            "     jumlah_berat        DECIMAL(10,2)",
            "     tgl_panen          DATE",
        ],
    )

    distribusi = _entitas(
        d,
        1090,
        480,
        420,
        190,
        "distribusi",
        [
            "PK  id_distribusi      INT (AI)",
            "FK  id_panen           INT  &gt;- inventori_panen",
            "     tujuan_pengiriman  VARCHAR(150)",
            "     jumlah_dikirim     DECIMAL(10,2)",
            "     status_pengiriman  VARCHAR(50)",
        ],
    )

    # ------------------------------------------------------------
    # Relasi petani (1) -> inventori_panen (0..*)
    # ------------------------------------------------------------
    d.edge(
        petani,
        panen,
        "",
        S_EDGE_PLAIN.replace("strokeColor=#1f2937", "strokeColor=#1f2937").replace(
            "endArrow=none", "endArrow=none"
        ),
        exit_xy=(1.0, 0.28),
        entry_xy=(0.0, 0.28),
    )
    d.edge(
        petani,
        panen,
        "",
        S_EDGE_PLAIN.replace("strokeColor=#1f2937", "strokeColor=#1f2937"),
        exit_xy=(1.0, 0.72),
        entry_xy=(0.0, 0.80),
    )
    d.line(510, 540, 540, 540, S_LINE.replace("strokeColor=#d1d5db", "strokeColor=#1f2937"))
    d.line(540, 540, 540, 633, S_LINE.replace("strokeColor=#d1d5db", "strokeColor=#1f2937"))
    d.line(540, 633, 570, 633, S_LINE.replace("strokeColor=#d1d5db", "strokeColor=#1f2937"))
    d.text(
        "1",
        500,
        505,
        60,
        20,
        S_MSG.replace("fontSize=13", "fontSize=15").replace("align=left", "align=center"),
    )
    d.text(
        "0..*",
        500,
        630,
        70,
        20,
        S_MSG.replace("fontSize=13", "fontSize=15").replace("align=left", "align=center"),
    )

    # ------------------------------------------------------------
    # Relasi inventori_panen (1) -> distribusi (0..*)
    # ------------------------------------------------------------
    d.edge(panen, distribusi, "", S_EDGE_PLAIN, exit_xy=(1.0, 0.28), entry_xy=(0.0, 0.28))
    d.edge(panen, distribusi, "", S_EDGE_PLAIN, exit_xy=(1.0, 0.72), entry_xy=(0.0, 0.80))
    d.line(1040, 540, 1060, 540, S_LINE.replace("strokeColor=#d1d5db", "strokeColor=#1f2937"))
    d.line(1060, 540, 1060, 633, S_LINE.replace("strokeColor=#d1d5db", "strokeColor=#1f2937"))
    d.line(1060, 633, 1090, 633, S_LINE.replace("strokeColor=#d1d5db", "strokeColor=#1f2937"))
    d.text(
        "1",
        1030,
        505,
        60,
        20,
        S_MSG.replace("fontSize=13", "fontSize=15").replace("align=left", "align=center"),
    )
    d.text(
        "0..*",
        1022,
        630,
        70,
        20,
        S_MSG.replace("fontSize=13", "fontSize=15").replace("align=left", "align=center"),
    )

    # ------------------------------------------------------------
    # Tabel users berdiri sendiri (tanpa foreign key)
    # ------------------------------------------------------------
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#f7fbf8;strokeColor=%s;"
        "strokeWidth=1.4;dashed=1;fontSize=13;fontColor=%s;align=center;"
        "verticalAlign=middle;" % ("#6b8f7d", TEKS),
        60,
        400,
        430,
        60,
    )
    d.text(
        "Tabel berdiri sendiri &mdash; tidak memiliki foreign key<br>"
        "Menyimpan kredensial seluruh jenis aktor",
        70,
        408,
        410,
        46,
        S_MSG.replace("fontSize=13", "fontSize=13").replace("align=left", "align=center"),
    )

    d.text(
        "Relasi: satu baris data pada tabel petani dapat memiliki banyak lot "
        "panen pada tabel inventori_panen (1 : 0..*). Setiap lot panen dapat "
        "dialokasikan menjadi banyak baris alokasi pada tabel distribusi "
        "(1 : 0..*). Tabel users berdiri sendiri tanpa foreign key karena "
        "menyimpan kredensial seluruh aktor yang berbeda jenis. Kolom "
        "status_pengiriman hanya menerima tiga nilai baku: Diproses, Dalam "
        "Pengiriman, dan Terkirim. Kolom jumlah_berat menyimpan berat awal "
        "lot; sisa stok dihitung dari jumlah_dikirim pada tabel distribusi "
        "(BR-02).",
        60,
        700,
        1440,
        100,
        S_CATATAN,
    )

    return d


# ============================================================
# 3. ARSITEKTUR SISTEM
# ============================================================
def diagram_arsitektur():
    """Arsitektur Sistem AgriUno."""
    d = Diagram("Arsitektur Sistem AgriUno", 1560, 1160, "Arsitektur Sistem AgriUno")
    _judul(
        d,
        "Arsitektur Sistem AgriUno (Three-Tier MVC)",
        "Lapisan presentasi, logika, dan akses data untuk versi UAS",
        1560,
    )

    lx, lw = 120, 940

    # --- Presentation layer ---
    d.node("", S_SISTEM, lx, 90, lw, 350)
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.8;fontSize=15;fontStyle=1;fontColor=#ffffff;"
        "align=center;verticalAlign=middle;" % (HIJAU_TUA, HIJAU_TUA),
        lx,
        90,
        lw,
        34,
    )
    d.text(
        "Presentation Layer (View)",
        lx + 10,
        92,
        lw - 20,
        28,
        S_MSG.replace("align=left", "align=center")
        .replace("fontSize=13", "fontSize=15")
        .replace("fontColor=#1f2937", "fontColor=#ffffff")
        .replace("fontStyle=0", "fontStyle=1"),
    )

    view_items = [
        "views/splash_view.py  —  SplashView: logo + animasi pembuka (tambahan UAS)",
        "views/login_view.py  —  LoginView: form login dengan verifikasi basis data",
        "views/register_view.py  —  RegisterView: pendaftaran akun khusus (tambahan UAS)",
        "views/dashboard_view.py  —  DashboardView: kartu statistik & indikator nyata",
        "views/petani_view.py  —  PetaniView: form + tabel data petani",
        "views/panen_view.py  —  PanenView: form + tabel lot panen + sisa stok",
        "views/distribusi_view.py  —  DistribusiView: form + tabel alokasi",
        "main.py  —  AgriUnoApp: jendela utama, sidebar, dan show_page()",
    ]
    for i, item in enumerate(view_items):
        yy = 130 + i * 34
        d.node("", S_BOX, lx + 20, yy, lw - 40, 30)
        d.text(item, lx + 30, yy + 4, lw - 60, 24, S_MSG.replace("fontSize=13", "fontSize=12"))

    d.text(
        "klik tombol / isi form  —  aman untuk dipakai pengguna",
        lx + 20,
        406,
        lw - 40,
        26,
        S_MSG.replace("fontSize=13", "fontSize=13").replace("align=left", "align=center"),
    )

    # --- Logic layer ---
    d.node("", S_SISTEM, lx, 470, lw, 180)
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.8;fontSize=15;fontStyle=1;fontColor=#ffffff;"
        "align=center;verticalAlign=middle;" % (HIJAU_TUA, HIJAU_TUA),
        lx,
        470,
        lw,
        34,
    )
    d.text(
        "Logic Layer (Controller)",
        lx + 10,
        472,
        lw - 20,
        28,
        S_MSG.replace("align=left", "align=center")
        .replace("fontSize=13", "fontSize=15")
        .replace("fontColor=#1f2937", "fontColor=#ffffff")
        .replace("fontStyle=0", "fontStyle=1"),
    )

    ctrl_items = [
        "controllers/auth_controller.py  —  AuthController &amp; Session: login, logout, RBAC",
        "controllers/user_controller.py  —  UserController: registrasi & pemeliharaan akun",
        "controllers/controller.py  —"
        "AgriUnoController: validasi"
        "masukan dan aturan bisnis BR-01 s.d. BR-09",
    ]
    for i, item in enumerate(ctrl_items):
        yy = 508 + i * 34
        d.node("", S_BOX, lx + 20, yy, lw - 40, 30)
        d.text(item, lx + 30, yy + 4, lw - 60, 24, S_MSG.replace("fontSize=13", "fontSize=12"))

    d.text(
        "nilai tervalidasi  —  diteruskan ke model",
        lx + 20,
        614,
        lw - 40,
        26,
        S_MSG.replace("align=left", "align=center"),
    )

    # --- Data access layer ---
    d.node("", S_SISTEM, lx, 680, lw, 280)
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.8;fontSize=15;fontStyle=1;fontColor=#ffffff;"
        "align=center;verticalAlign=middle;" % (HIJAU_TUA, HIJAU_TUA),
        lx,
        680,
        lw,
        34,
    )
    d.text(
        "Data Access Layer (Model)",
        lx + 10,
        682,
        lw - 20,
        28,
        S_MSG.replace("align=left", "align=center")
        .replace("fontSize=13", "fontSize=15")
        .replace("fontColor=#1f2937", "fontColor=#ffffff")
        .replace("fontStyle=0", "fontStyle=1"),
    )

    model_items = [
        "models/base_model.py  —  BaseModel: helper kueri, transaksi, dan galat errno",
        "models/user_model.py  —  UserModel: hashing SHA-256, autentikasi, registrasi",
        "models/petani_model.py  —  PetaniModel: CRUD tabel petani",
        "models/panen_model.py  —  PanenModel: CRUD tabel inventori_panen + sisa stok",
        "models/distribusi_model.py  —  DistribusiModel: CRUD tabel distribusi + FOR UPDATE",
        "config/database.py  —  DatabaseConnection: context manager koneksi & transaksi",
        "config/constants.py  —  palet warna, peran pengguna, dan nilai baku status",
    ]
    for i, item in enumerate(model_items):
        yy = 720 + i * 30
        d.node("", S_BOX, lx + 20, yy, lw - 40, 26)
        d.text(item, lx + 30, yy + 2, lw - 60, 22, S_MSG.replace("fontSize=13", "fontSize=12"))

    d.text(
        "kueri DML berparameter  —  server basis data",
        lx + 20,
        930,
        lw - 40,
        26,
        S_MSG.replace("align=left", "align=center"),
    )

    # --- Data store ---
    d.node(
        "Data Store: MySQL 8.0 (Laragon)<br>"
        "Database: agriuno  —  Tabel: users, petani, inventori_panen, "
        "distribusi<br><i>koneksi lewat mysql-connector-python</i>",
        "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=#f2f9f5;"
        "strokeColor=%s;strokeWidth=1.8;fontSize=14;fontColor=%s;"
        "align=center;verticalAlign=middle;" % (HIJAU_TUA, TEKS),
        300,
        1000,
        580,
        92,
    )

    # --- Aktor ---
    d.node("Admin Gudang<br><i>peran admin &amp; operator</i>", S_ENTITAS, 1110, 140, 240, 100)
    d.node("Pengguna Baru<br><i>registrasi akun</i>", S_AKTOR, 1110, 280, 240, 100)
    d.node("Petani Terdaftar<br><i>peran petani — akses baca</i>", S_AKTOR, 1110, 430, 240, 100)
    d.node("Petani &amp; Distributor<br><i>entitas non-user</i>", S_ENTITAS, 1110, 590, 240, 100)

    d.text(
        "input data",
        1120,
        110,
        220,
        20,
        S_MSG.replace("fontSize=13", "fontSize=12").replace("align=left", "align=center"),
    )
    d.text(
        "informasi",
        1120,
        250,
        220,
        20,
        S_MSG.replace("fontSize=13", "fontSize=12").replace("align=left", "align=center"),
    )

    # --- Pipeline CI/CD ---
    d.node("", S_BOX_HEADER, 1110, 740, 420, 30)
    d.node("", S_BOX, 1110, 770, 420, 180)
    d.text("Continuous Integration (Modul 8)", 1120, 744, 400, 24, S_BOX_HEADER)
    d.text(
        "• .github/workflows/ci_pipeline.yml<br>"
        "• pytest + pytest-cov (56 pengujian)<br>"
        "• ruff check + ruff format --check<br>"
        "• requirements.txt sebagai daftar dependensi<br>"
        "• PyInstaller untuk pemaketan .exe",
        1125,
        782,
        390,
        160,
        S_MSG.replace("fontSize=13", "fontSize=12"),
    )

    return d


# ============================================================
# 4. DIAGRAM NAVIGASI
# ============================================================
def diagram_navigasi():
    """Diagram Navigasi / Sitemap AgriUno."""
    d = Diagram("Diagram Navigasi AgriUno", 1560, 1160, "Diagram Navigasi AgriUno")
    _judul(
        d,
        "Diagram Navigasi / Sitemap AgriUno",
        "Alur splash, autentikasi, registrasi, dan navigasi jendela utama",
        1560,
    )

    # ------------------------------------------------------------
    # Tingkat 1: splash, login, registrasi
    # ------------------------------------------------------------
    d.node("", S_AWAL, 700, 76, 56, 30)
    d.text(
        "Mulai",
        700,
        79,
        56,
        26,
        S_MSG.replace("fontSize=13", "fontSize=12")
        .replace("align=left", "align=center")
        .replace("fontColor=#1f2937", "fontColor=#ffffff"),
    )

    d.node(
        "SplashView  \u2014  Animasi Logo<br>24 frame, progress bar, dan pesan status (3 detik)",
        S_ACTIVITAS,
        560,
        140,
        340,
        60,
    )
    d.node("LoginView  \u2014  Login<br>Kolom Username / Password", S_ACTIVITAS, 560, 250, 340, 60)
    d.node("Tombol \u201cDaftar di sini\u201d pada halaman login", S_ACTIVITAS, 560, 340, 340, 44)
    d.node(
        "RegisterView  \u2014  Registrasi Akun<br>Nama lengkap, username, password, dan peran",
        S_ACTIVITAS,
        120,
        250,
        340,
        64,
    )

    cek = d.node("Kredensial sesuai?", S_KEPUTUSAN, 610, 440, 240, 70)
    d.node(
        "Pesan galat inline<br>\u201cUsername atau Password salah!\u201d",
        S_ERROR,
        940,
        444,
        300,
        60,
    )

    # ------------------------------------------------------------
    # Tingkat 2: jendela utama
    # ------------------------------------------------------------
    sistem = d.node("", S_SISTEM, 160, 560, 1240, 480)
    d.node(
        "",
        "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;"
        "strokeWidth=1.8;fontSize=15;fontStyle=1;fontColor=#ffffff;"
        "align=center;verticalAlign=middle;" % (HIJAU_TUA, HIJAU_TUA),
        160,
        560,
        1240,
        40,
    )
    d.text(
        "AgriUnoApp (main.py)  \u2014  jendela utama 1150 x 680, sidebar "
        "navigasi, dan panel profil pengguna",
        170,
        566,
        1220,
        30,
        S_MSG.replace("align=left", "align=center")
        .replace("fontSize=13", "fontSize=15")
        .replace("fontColor=#1f2937", "fontColor=#ffffff")
        .replace("fontStyle=0", "fontStyle=1"),
    )

    halaman = [
        (
            200,
            "DashboardView",
            "Dashboard<br>\u2022 3 kartu statistik<br>"
            "\u2022 3 indikator kinerja nyata<br>"
            "\u2022 ringkasan berat",
        ),
        (
            490,
            "PetaniView",
            "Kelola Petani<br>\u2022 Form: Nama, Lokasi, Komoditas<br>\u2022 Tabel + tombol CRUD",
        ),
        (
            780,
            "PanenView",
            "Inventori Panen<br>\u2022 Dropdown penyetor<br>"
            "\u2022 Kolom Sisa Stok<br>\u2022 Tabel + tombol CRUD",
        ),
        (
            1070,
            "DistribusiView",
            "Distribusi<br>\u2022 Dropdown lot + sisa stok<br>"
            "\u2022 Kotak pilihan status<br>\u2022 Tabel + tombol CRUD",
        ),
    ]
    for x, nama, isi in halaman:
        d.node("", S_BOX_HEADER, x, 630, 260, 30)
        d.node("", S_BOX, x, 660, 260, 150)
        d.text(nama, x + 8, 632, 244, 26, S_BOX_HEADER)
        d.text(isi, x + 10, 672, 240, 130, S_MSG.replace("fontSize=13", "fontSize=12"))

    d.node(
        "Tombol \u201cKeluar\u201d (footer sidebar)<br>destroy() + logout()",
        S_ERROR,
        200,
        840,
        280,
        56,
    )

    d.text(
        "Seluruh perpindahan halaman dilakukan oleh fungsi show_page() "
        "pada kelas AgriUnoApp, yang memanggil load_data() atau "
        "load_table() lalu menjalankan tkraise() pada halaman tujuan. "
        "Menu sidebar menyesuaikan isi terhadap peran pengguna yang "
        "sedang login: peran \u201cpetani\u201d hanya memperoleh akses ke "
        "Dashboard.",
        510,
        830,
        860,
        90,
        S_CATATAN,
    )

    # ------------------------------------------------------------
    # Aliran
    # ------------------------------------------------------------
    arrow_v(d, 728, 106, 140)
    arrow_v(d, 728, 200, 250)
    arrow_v(d, 728, 310, 340)
    arrow_v(d, 728, 384, 440)
    arrow_h(d, 474, 850, 940)
    d.text(
        "Tidak",
        1180,
        408,
        80,
        20,
        S_MSG.replace("fontSize=13", "fontSize=12").replace("align=left", "align=center"),
    )

    # Jalur "Ya" menuju jendela utama.
    d.edge(
        cek,
        sistem,
        "",
        S_EDGE(arrow="block", width=1.5),
        exit_xy=(0.0, 0.5),
        entry_xy=(0.18, 0.0),
        points=[(480, 475), (480, 530)],
    )
    d.text(
        "Ya",
        500,
        430,
        60,
        20,
        S_MSG.replace("fontSize=13", "fontSize=12").replace("align=left", "align=center"),
    )

    # Jalur registrasi.
    arrow_h(d, 362, 560, 460)
    arrow_h(d, 300, 460, 560)
    d.text(
        "Kembali",
        470,
        268,
        120,
        20,
        S_MSG.replace("fontSize=13", "fontSize=12").replace("align=left", "align=center"),
    )

    d.text(
        "Catatan: navigasi aplikasi bersifat dua tingkat. Tingkat pertama "
        "menangani siklus splash, login, dan registrasi. Tingkat kedua "
        "menangani perpindahan antar halaman melalui sidebar pada jendela "
        "utama.",
        160,
        1050,
        1240,
        60,
        S_CATATAN,
    )

    return d
