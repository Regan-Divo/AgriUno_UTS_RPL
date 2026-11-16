-- ===========================================================================
--  BERKAS SKEMA BASIS DATA - AgriUno
--  Proyek  : AgriUno - Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal
--  Praktikum: Rekayasa Perangkat Lunak (UAS) - Modul 1 s.d. Modul 8
--  DBMS    : MySQL 8.0 (melalui Laragon)
--  Kelompok : 1 - Kelas B
--
--  CARA MENJALANKAN:
--    1. Buka Laragon lalu klik "Start All" agar service MySQL aktif.
--    2. Buka Terminal Laragon (atau Command Prompt), lalu jalankan:
--         mysql -u root -p < database.sql
--    3. Alternatif: buka phpMyAdmin (http://localhost/phpmyadmin),
--       pilih tab "Import", pilih berkas ini, lalu klik "Go".
--
--  CATATAN PENTING:
--    Skrip ini menggunakan DROP DATABASE. Jalankan HANYA pada database
--    'agriuno' milik proyek-praktikum.
--
--    Kata sandi pada tabel `users` TIDAK PERNAH disimpan sebagai teks biasa.
--    Nilai yang tersimpan adalah SHA-256 dari (salt + password).
--    Seed akun di bawah memakai satu salt yang sama untuk seluruh akun demo
--    agar mudah diingat saat presentasi. Akun yang dibuat melalui menu
--    Registrasi pada aplikasi memakai salt acak per pengguna.
-- ===========================================================================

DROP DATABASE IF EXISTS agriuno;
CREATE DATABASE agriuno
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE agriuno;

-- ===========================================================================
--  TABEL 1 : users
--  Menyimpan kredensial, identitas, dan peran pengguna aplikasi.
--  Kolom `password` berisi hash SHA-256 dari (salt + password).
-- ===========================================================================
CREATE TABLE users (
    id_user    INT           NOT NULL AUTO_INCREMENT,
    username   VARCHAR(50)  NOT NULL,
    password   VARCHAR(255) NOT NULL,
    salt       VARCHAR(64)  NOT NULL,
    full_name  VARCHAR(100) NOT NULL,
    role       ENUM('admin', 'operator', 'petani') NOT NULL DEFAULT 'petani',
    is_active  TINYINT(1)   NOT NULL DEFAULT 1,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_users PRIMARY KEY (id_user),
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT chk_users_role CHECK (role IN ('admin', 'operator', 'petani'))
) ENGINE = InnoDB;

-- ===========================================================================
--  TABEL 2 : petani
--  Menyimpan data identitas personal dan lokasi lahan penyetor panen.
--  Primary key  : id_petani
-- ===========================================================================
CREATE TABLE petani (
    id_petani       INT           NOT NULL AUTO_INCREMENT,
    nama_petani     VARCHAR(100)  NOT NULL,
    lokasi_lahan    VARCHAR(150)  NOT NULL,
    komoditas_utama  VARCHAR(100)  NOT NULL,
    CONSTRAINT pk_petani PRIMARY KEY (id_petani)
) ENGINE = InnoDB;

-- ===========================================================================
--  TABEL 3 : inventori_panen
--  Mencatat rincian stok dan hasil panen yang masuk ke gudang.
--
--  CATATAN PENTING SOAL KOLOM jumlah_berat:
--  Nilai kolom ini adalah BERAT AWAL LOT saat disetor ke gudang,
--  BUKAN sisa stok. Kolom ini tidak dimodifikasi ketika alokasi
--  distribusi dibuat. Sisa stok dihitung ulang dari sumber
--  kebenaran tunggal, yaitu tabel `distribusi`:
--
--      sisa_stok = jumlah_berat - SUM(distribusi.jumlah_dikirim)
--
--  Pendekatan ini menjaga agar histori setoran tetap dapat ditelusuri
--  dan mencegah ketidaksesuaian antara data stok dengan data alokasi.
--
--  Relasi: Many-to-One terhadap tabel petani (BR-01).
-- ===========================================================================
CREATE TABLE inventori_panen (
    id_panen         INT           NOT NULL AUTO_INCREMENT,
    id_petani        INT           NOT NULL,
    jenis_komoditas  VARCHAR(100)  NOT NULL,
    jumlah_berat     DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    tgl_panen        DATE          NOT NULL,

    CONSTRAINT pk_panen PRIMARY KEY (id_panen),

    CONSTRAINT fk_panen_petani
        FOREIGN KEY (id_petani) REFERENCES petani (id_petani)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    -- Menjaga agar nilai berat tidak pernah negatif (lapis pengaman
    -- kedua untuk Aturan Bisnis BR-02).
    CONSTRAINT chk_berat_positif CHECK (jumlah_berat >= 0)
) ENGINE = InnoDB;

-- ===========================================================================
--  TABEL 4 : distribusi
--  Mencatat alokasi pengiriman hasil panen menuju distributor.
--
--  Aturan bisnis yang dijaga oleh tabel ini:
--    BR-02 : jumlah_dikirim tidak boleh melebihi sisa stok lot asal.
--    BR-03 : id_panen wajib menunjuk lot yang terdaftar.
--    BR-04 : status_pengiriman default 'Diproses'.
--    BR-05 : status hanya menerima tiga nilai baku.
--    BR-09 : alokasi berstatus 'Terkirim' bersifat final (dijaga Model).
--
--  Relasi: Many-to-One terhadap inventori_panen. ON DELETE RESTRICT
--  mencegah lot yang sudah dialokasikan ikut terhapus.
-- ===========================================================================
CREATE TABLE distribusi (
    id_distribusi      INT            NOT NULL AUTO_INCREMENT,
    id_panen           INT            NOT NULL,
    tujuan_pengiriman  VARCHAR(150)   NOT NULL,
    jumlah_dikirim     DECIMAL(10, 2) NOT NULL,
    status_pengiriman  VARCHAR(50)    NOT NULL DEFAULT 'Diproses',

    CONSTRAINT pk_distribusi PRIMARY KEY (id_distribusi),

    CONSTRAINT fk_distribusi_panen
        FOREIGN KEY (id_panen) REFERENCES inventori_panen (id_panen)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    -- Membatasi nilai status hanya pada tiga nilai baku (BR-04 & BR-05).
    CONSTRAINT chk_status_pengiriman
        CHECK (status_pengiriman IN ('Diproses', 'Dalam Pengiriman', 'Terkirim')),

    CONSTRAINT chk_jumlah_dikirim CHECK (jumlah_dikirim > 0)
) ENGINE = InnoDB;

-- ===========================================================================
--  INDEX PENDUKUNG
--  Mempercepat pencarian data (FR-02) dan penyaringan laporan (FR-06).
-- ===========================================================================
CREATE INDEX idx_users_role       ON users (role);
CREATE INDEX idx_petani_nama      ON petani (nama_petani);
CREATE INDEX idx_panen_komoditas  ON inventori_panen (jenis_komoditas);
CREATE INDEX idx_panen_tanggal    ON inventori_panen (tgl_panen);
CREATE INDEX idx_panen_petani     ON inventori_panen (id_petani);
CREATE INDEX idx_distribusi_status ON distribusi (status_pengiriman);
CREATE INDEX idx_distribusi_panen  ON distribusi (id_panen);

-- ===========================================================================
--  DATA CONTOH - AKUN PENGGUNA
--  Password : admin123 / operator123 / petani123
--  Salt     : 2d6fcf9887b4661144986566c6d4789a  (sama untuk akun demo)
-- ===========================================================================
INSERT INTO users (username, password, salt, full_name, role, is_active) VALUES
    ('admin',    'fd3819827da95a2c759c0eab8af42dc05b36f2a1f55814aa0d1b9ef0ed5c97a3',
                 '2d6fcf9887b4661144986566c6d4789a', 'Administrator AgriUno', 'admin', 1),
    ('operator', '914e85f7cd3a247a3c840ac0c767dc85a1fff1f1afd8ca01f0a345436132316b',
                 '2d6fcf9887b4661144986566c6d4789a', 'Operator Gudang',      'operator', 1),
    ('petani',   'feb721ab32b20836395ee1a5926af6bd09d9a1a64b01e9058fbcfd98330153ca',
                 '2d6fcf9887b4661144986566c6d4789a', 'PetaniDemo',            'petani', 1);

-- ===========================================================================
--  DATA CONTOH - PETANI
-- ===========================================================================
INSERT INTO petani (nama_petani, lokasi_lahan, komoditas_utama) VALUES
    ('Siti Halimah',            'Desa Wonosari, Kec. Poncowati',  'Beras Organik'),
    ('Kelompok Tani Maju',      'Desa Sukamaju, Kec. Balawa',     'Jagung Manis'),
    ('Ahmad Fauzi',             'Desa Mekarjaya, Kec. Dolo',      'Cabai Rawit'),
    ('Yanti Lestari',           'Desa Harapan, Kec. Kulawi',      'Tomat Cherry'),
    ('Kelompok Tani Sejahtera', 'Desa Tunggal, Kec. Sigi',        'Kentang');

-- ===========================================================================
--  DATA CONTOH - INVENTORI PANEN
--  jumlah_berat = berat awal lot (sisa stok dihitung dari tabel distribusi)
-- ===========================================================================
INSERT INTO inventori_panen (id_petani, jenis_komoditas, jumlah_berat, tgl_panen) VALUES
    (1, 'Beras Organik', 320.00, '2026-10-02'),
    (2, 'Jagung Manis',  185.50, '2026-10-04'),
    (3, 'Cabai Rawit',    96.00, '2026-10-05'),
    (1, 'Beras Organik', 140.00, '2026-10-07'),
    (5, 'Kentang',       260.00, '2026-10-08'),
    (4, 'Tomat Cherry',   75.25, '2026-10-09');

-- ===========================================================================
--  DATA CONTOH - DISTRIBUSI
-- ===========================================================================
INSERT INTO distribusi (id_panen, tujuan_pengiriman, jumlah_dikirim, status_pengiriman) VALUES
    (1, 'Pasar Induk Mazzini',      180.00, 'Terkirim'),
    (2, 'CV Sumber Deliciosa',      100.00, 'Dalam Pengiriman'),
    (3, 'Warung Mie Gado',           24.00, 'Diproses'),
    (5, 'Hotel Grand Siberia',      120.00, 'Diproses'),
    (6, 'Supermarket Segar.Enum',    40.25, 'Dalam Pengiriman');
