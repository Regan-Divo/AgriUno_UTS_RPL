# AgriUno — Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal

Aplikasi **desktop** untuk mengelola data petani penyetor, inventori lot panen,
dan alokasi pengiriman hasil panen pada gudang penampungan komoditas lokal.

Proyek Praktikum **Rekayasa Perangkat Lunak (RPL) 2026** — Username **Kelompok 1, Kelas B**.

> **Versi:** 2.0.0 (UAS — kelanjutan dari versi UTS 1.0)

---

## Daftar Isi

1. [Ringkasan Fitur](#1-ringkasan-fitur)
2. [Teknologi yang Digunakan](#2-teknologi-yang-digunakan)
3. [Struktur Proyek](#3-struktur-proyek)
4. [Menyiapkan Lingkungan](#4-menyiapkan-lingkungan)
5. [Menyiapkan Basis Data](#5-menyiapkan-basis-data)
6. [Menjalankan Aplikasi](#6-menjalankan-aplikasi)
7. [Akun Demo](#7-akun-demo)
8. [Menjalankan Pengujian](#8-menjalankan-pengujian)
9. [Membangkitkan Ulang Diagram](#9-membangkitkan-ulang-diagram)
10. [Pemaketan Aplikasi (.exe)](#10-pemaketan-aplikasi-exe)
11. [Pipeline CI/CD](#11-pipeline-cicd)
12. [Menerbitkan ke GitHub](#12-menerbitkan-ke-github)
13. [Perbandingan UTS dan UAS](#13-perbandingan-uts-dan-uas)
14. [Aturan Bisnis](#14-aturan-bisnis)
15. [Troubleshooting](#15-troubleshooting)

---

## 1. Ringkasan Fitur

| Modul | Fitur | Sumber |
|---|---|---|
| 1 | Diagram Konteks, DFD Level 1, DFD Level 2, Use Case, Sequence, Activity, Class | Modul 1 |
| 2 | Arsitektur three-tier MVC, ERD empat tabel, skema DDL MySQL | Modul 2 |
| 3 | Lingkungan virtual, VS Code, Git, GitHub | Modul 3 |
| 4 | Model Python berbasis OOP dengan parameterized query | Modul 4 |
| 5 | Tujuh kelas antarmuka desktop (CustomTkinter) | Modul 5 |
| 6 | Tiga controller + 56 skrip pengujian pytest | Modul 6 |
| 7 | Autentikasi SHA-256 bersalt, RBAC tiga peran, **registrasi akun** | Modul 7 |
| 8 | **Logo + animasi splash**, pipeline CI/CD, pemaketan `.exe` | Modul 8 |

**Fitur baru pada tahap UAS (dibanding versi UTS):**

- **Logo AgriUno** (emblem, wordmark, dan ikon `.ico`) beserta jendela **splash
  beranimasi** — logo muncul bertahap melalui 24 frame, cincin orbit berputar,
  progress bar, dan pesan status bergantian selama 3 detik.
- **Registrasi akun khusus pengguna** pada halaman login. Pengguna memilih peran
  `Operator Gudang` atau `Petani`; peran `Administrator` hanya dapat dibuat oleh
  pengelola basis data (BR-07).
- **Otorisasi berbasis peran (RBAC)** dengan tiga peran: `admin`, `operator`,
  dan `petani`. Menu sidebar, tombol, dan kolom isian menyesuaikan hak akses.
- **Autentikasi berbasis basis data** menggunakan hash SHA-256 dari
  `(salt + password)` dengan salt acak per pengguna dan perbandingan
  `hmac.compare_digest`.
- **Perhitungan stok atomik** — pemeriksaan sisa stok dan penyimpanan alokasi
  dijalankan dalam satu transaksi dengan penguncian baris (`SELECT ... FOR UPDATE`).
- **Pemilihan data berbasis dropdown** — penyetor dan lot panen dipilih dari kotak
  daftar yang terisi otomatis beserta sisa stoknya.
- **Indikator dashboard nyata** — progress bar dihitung dari data, bukan angka tetap.

---

## 2. Teknologi yang Digunakan

| Lapisan | Teknologi |
|---|---|
| Antarmuka | Python 3.10+, CustomTkinter 5.2, `tkinter.ttk.Treeview`, `tkinter.Canvas` |
| Logika | Python 3.10+ (MVC: Model–View–Controller) |
| Basis data | MySQL 8.0 Community Server (Laragon), `mysql-connector-python` 9.0 |
| Visual | Pillow 10.4 (hanya untuk membangun aset, bukan saat aplikasi berjalan) |
| Pengujian | pytest 8.3, pytest-cov 5.0, ruff 0.17 |
| Pemaketan | PyInstaller 6.10 |
| VCS & CI | Git, GitHub Actions |

---

## 3. Struktur Proyek

```
AgriUno/
├── .github/workflows/ci_pipeline.yml   # Pipeline CI GitHub Actions (Modul 8)
├── assets/
│   ├── anim/                           # 24 frame animasi logo untuk splash
│   ├── logo_agriuno.png                # Emblem AgriUno 512×512
│   ├── logo_agriuno_wordmark.png
│   ├── logo_agriuno_wordmark_small.png
│   └── logo_agriuno.ico                # Ikon untuk berkas .exe
├── config/
│   ├── constants.py                    # Palet warna, peran pengguna, status baku
│   └── database.py                     # DatabaseConnection (context manager)
├── controllers/
│   ├── auth_controller.py              # AuthController & Session (Modul 7)
│   ├── controller.py                   # AgriUnoController
│   └── user_controller.py              # UserController (Modul 7)
├── models/
│   ├── base_model.py                   # BaseModel (helper kueri & transaksi)
│   ├── user_model.py                   # UserModel (hashing & autentikasi)
│   ├── petani_model.py                 # PetaniModel
│   ├── panen_model.py                  # PanenModel (+ sisa stok)
│   └── distribusi_model.py             # DistribusiModel (+ transaksi stok)
├── views/
│   ├── splash_view.py                  # SplashView (logo + animasi, Modul 8)
│   ├── login_view.py                   # LoginView
│   ├── register_view.py                # RegisterView (registrasi, Modul 7)
│   ├── dashboard_view.py               # DashboardView
│   ├── petani_view.py                  # PetaniView
│   ├── panen_view.py                   # PanenView
│   └── distribusi_view.py              # DistribusiView
├── tests/
│   ├── conftest.py                     # Auto-skip bila MySQL tidak aktif
│   ├── test_auth.py                    # Hashing, RBAC, registrasi
│   └── test_business_logic.py          # Aturan bisnis BR-01 s.d. BR-10
├── tools/
│   ├── diagram_builder.py              # Pembangun mxGraph
│   ├── diagram_dfd.py                  # Definisi diagram DFD
│   ├── diagram_uml.py                  # Definisi diagram UML
│   ├── diagrams_desain.py              # ERD, arsitektur, navigasi
│   ├── generate_diagrams.py            # Pembangkit diagram + ekspor PNG
│   ├── generate_logo.py                # Pembangkit logo & frame animasi
│   ├── report_content.py               # Konten tabel laporan
│   ├── report_content2.py              # Konten spesifikasi use case
│   ├── build_report.py                 # Penyusun laporan (.docx)
│   └── build_report_uas.py             # Penambahan bagian UAS pada laporan
├── docs/
│   ├── diagrams/                       # Hasil bangkit diagram (.drawio + .png)
│   └── screenshots/                    # Tangkapan layar antarmuka
├── database.sql                        # Skema DDL + data contoh
├── main.py                             # Titik masuk aplikasi
├── pytest.ini                          # Konfigurasi penanda pengujian
├── requirements.txt                    # Daftar dependensi terkunci
├── ruff.toml                           # Konfigurasi pemeriksaan kualitas
└── .gitignore
```

---

## 4. Menyiapkan Lingkungan

**Prasyarat:** Python 3.10+, [Laragon](https://laragon.org/) (MySQL 8.0),
Visual Studio Code, dan Git.

```bash
# 1) Membuat lingkungan virtual
python -m venv env

# 2) Mengaktifkan lingkungan virtual
#    Windows (PowerShell)
.\env\Scripts\Activate.ps1
#    Windows (CMD)
.\env\Scripts\activate.bat
#    Linux/macOS
source env/bin/activate

# 3) Memasang seluruh dependensi
pip install -r requirements.txt
```

> Bila `pip`_powerShell menampilkan kebijakan eksekusi dibatasi, jalankan
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` sekali saja.

**Konfigurasi koneksi basis data** (opsional). Nilai bawaan mengikuti Laragon
standar. Untuk lingkungan lain, set environment variable berikut:

| Variabel | Bawaan |
|---|---|
| `AGRIUNO_DB_HOST` | `localhost` |
| `AGRIUNO_DB_PORT` | `3306` |
| `AGRIUNO_DB_USER` | `root` |
| `AGRIUNO_DB_PASSWORD` | *(kosong)* |
| `AGRIUNO_DB_NAME` | `agriuno` |

---

## 5. Menyiapkan Basis Data

1. Buka Laragon lalu klik **Start All** sehingga layanan MySQL aktif.
2. Buka **Menu → Terminal** (atau Command Prompt), lalu jalankan:

   ```bash
   mysql -u root -p < database.sql
   ```

   Alternatif melalui phpMyAdmin: buka `http://localhost/phpmyadmin`, pilih tab
   **Import**, pilih berkas `database.sql`, lalu klik **Go**.

Skrip `database.sql` membuat database `agriuno` beserta empat tabel
(`users`, `petani`, `inventori_panen`, `distribusi`), mengisi data contoh,
dan menyisipkan tiga akun demo.

> **Peringatan:** skrip ini menjalankan `DROP DATABASE IF EXISTS agriuno`.
> Jangan dijalankan pada basis data yang berisi data lain.

---

## 6. Menjalankan Aplikasi

AgriUno adalah **aplikasi desktop**. Tidak ada Laravel, tidak ada XAMPP,
tidak perlu browser, dan tidak perlu mengetik alamat URL apa pun.

### Cara A — Klik dua kali (paling mudah)

Klik dua kali berkas **`MULAI-APLIKASI.bat`** pada folder proyek. Berkas ini
otomatis memeriksa layanan MySQL lalu membuka aplikasi.

### Cara B — Klik dua kali berkas .exe

Klik dua kali **`dist\AgriUno.exe`**. One-click, tanpa console, memakai logo
AgriUno sebagai ikon. **Python tidak perlu terpasang** pada komputer tujuan.

### Cara C — Jalankan dari sumber (untuk pengembangan)

```bash
python main.py
```

### Urutan jendela yang tampil

1. **Splash** — logo AgriUno dengan animasi selama 3 detik.
2. **Login** — masukkan kredensial, atau klik *Belum punya akun? Daftar di sini*.
3. **Jendela utama** — sidebar navigasi, Dashboard, dan halaman pengelolaan data.

### Prasyarat saat membuka aplikasi

Layanan **MySQL pada Laragon harus aktif**.
Jika belum, buka Laragon lalu klik **Start All**, kemudian jalankan kembali
aplikasinya.

---

## 7. Akun Demo

| Username | Password | Peran | Hak Akses |
|---|---|---|---|
| `admin` | `admin123` | Administrator | Seluruh modul + kelola akun |
| `operator` | `operator123` | Operator Gudang | Kelola petani, panen, distribusi |
| `petani` | `petani123` | Petani | Dashboard (akses baca) |

Pengguna baru dapat mendaftar sendiri melalui menu **Daftar di sini** dengan
peran `Operator Gudang` atau `Petani`.

---

## 8. Menjalankan Pengujian

```bash
# Seluruh pengujian (56 skrip)
pytest -v

# Pengujian yang memerlukan MySQL aktif
pytest -v -m db

# Pengujian tanpa basis data
pytest -v -m "not db"

# Dengan laporan cakupan kode
pytest -v --cov=config --cov=models --cov=controllers --cov=views --cov-report=term-missing
```

Pengujian bertanda `db` **otomatis dilewati** apabila server MySQL tidak dapat
dihubungi, sehingga pipeline CI tetap hijau pada runner tanpa basis data.

---

## 9. Membangkitkan Ulang Diagram

Seluruh diagram laporan dibangkitkan secara terprogram dari kode sumber,
sehingga isinya dijamin konsisten dengan implementasi.

```bash
# Bangkitkan berkas .drawio saja
python tools/generate_diagrams.py

# Bangkitkan .drawio sekaligus ekspor PNG
python tools/generate_diagrams.py --export-png --scale 2
```

Ekspor PNG memerlukan **draw.io desktop**
([unduh](https://www.drawio.com)). Lokasi eksekusinya dicari otomatis pada
Windows; bila berada di lokasi lain, sesuaikan konstanta `DRAWIO_CANDIDATES`
di `tools/generate_diagrams.py`.

Logo dan frame animasi dibangun ulang dengan:

```bash
pip install Pillow
python tools/generate_logo.py
```

---

## 10. Pemaketan Aplikasi (.exe)

Berkas `.exe` beserta konfigurasinya **sudah tersedia** pada folder proyek:

| Berkas | Keterangan |
|---|---|
| `dist/AgriUno.exe` | Aplikasi mandiri (34,5 MB), siap didouble-click |
| `AgriUno.spec` | Konfigurasi pemaketan PyInstaller |
| `MULAI-APLIKASI.bat` | Peluncur sekali-klik |

Untuk membangun ulang (setelah kode berubah):

```bash
pip install pyinstaller
pyinstaller --noconfirm --clean AgriUno.spec
```

Folder `build/` dan `dist/` sudah masuk `.gitignore` sehingga tidak ikut
terunggah ke repositori. Bila ingin menyertakan berkas `.exe` ke dalam
repositori, hapus kedua baris tersebut dari `.gitignore` (perhatian: berkas
sebesar 34 MB melampaui batas wajar GitHub).

> **Catatan:** aplikasi memerlukan MySQL yang berjalan. Untuk aplikasi yang
> sepenuhnya mandiri, basis data dapat dipindahkan ke lokal menggunakan
> MariaDB portable.

---

## 11. Pipeline CI/CD

Berkas `.github/workflows/ci_pipeline.yml` menjalankan pipeline secara
otomatis pada setiap push ke branch `main` dan setiap pull request:

1. Checkout repositori.
2. Menyiapkan Python 3.11 dengan cache dependensi.
3. Memasang dependensi dari `requirements.txt`.
4. Menjalankan `pytest` beserta laporan cakupan kode.
5. Menjalankan `ruff check` dan `ruff format --check`.
6. Mengunggah laporan cakupan kode sebagai artefak.

> Badge status pipeline dapat disisipkan pada `README.md` setelah repositori
> dipublikasikan.

---

## 12. Menerbitkan ke GitHub

```bash
# 1) Inisialisasi (hanya bila belum ada repositori)
git init
git branch -M main

# 2) Terapkan seluruh perubahan
git add .
git commit -m "feat: rilis UAS AgriUno - modul 7 (autentikasi, registrasi, RBAC) dan modul 8 (logo, animasi, CI/CD)"

# 3) Hubungkan ke repositori remote
git remote add origin https://github.com/<akun>/<repositori>.git

# 4) Unggah
git push -u origin main
```

### Checklist sebelum presentasi

- [ ] `pytest -v` → seluruh pengujian lulus
- [ ] `ruff check .` dan `ruff format --check .` → tanpa galat
- [ ] `python main.py` → splash, login, dan seluruh halaman berjalan
- [ ] Registrasi akun baru berhasil dan akun dapat langsung login
- [ ] Diagram pada laporan merupakan hasil build terbaru
- [ ] Pipeline GitHub Actions berstatus hijau

---

## 13. Perbandingan UTS dan UAS

| Aspek | UTS | UAS |
|---|---|---|
| Autentikasi | Kredensial *hardcode* (`admin`/`12345`) | Tabel `users`, hash SHA-256 bersalt, `hmac.compare_digest` |
| Registrasi akun | Tidak tersedia | Halaman registrasi lengkap dengan validasi dan peran |
| Otorisasi | Satu operator | Tiga peran (RBAC), pembatasan modul dan tombol |
| Logo & animasi | Tidak tersedia | Emblem + wordmark + ikon, splash 24 frame |
| Basis data | 3 tabel | 4 tabel (`users` + CHECK constraint + indeks) |
| Perhitungan stok | Dua kueri pada dua koneksi | `LEFT JOIN` di basis data + transaksi `FOR UPDATE` |
| Transaksi | `commit()` parsial, alokasi ter-rollback diam-diam | Context manager `cursor(commit=True)` |
| Pemilihan data | ID diketik manual | Dropdown terisi otomatis |
| Indikator dashboard | Angka tetap (0,75 / 0,50 / 0,85) | Dihitung dari data nyata |
| Status pengiriman | `Terkirim` masih dapat diubah | `Terkirim` bersifat final (BR-09) |
| Pengujian | Tidak ada | 56 skrip pytest + pipeline CI |
| Pemaketan | Tidak ada | PyInstaller → `AgriUno.exe` |

---

## 14. Aturan Bisnis

| ID | Aturan |
|---|---|
| BR-01 | Setiap lot panen wajib menunjuk data petani yang tercatat. |
| BR-02 | Jumlah alokasi tidak boleh melebihi sisa stok; pemeriksaan dan penyimpanan berjalan dalam satu transaksi dengan `FOR UPDATE`. |
| BR-03 | `id_panen` wajib terdaftar sebelum alokasi disimpan. |
| BR-04 | Alokasi baru memperoleh status awal `Diproses`. |
| BR-05 | `status_pengiriman` hanya menerima `Diproses`, `Dalam Pengiriman`, `Terkirim`. |
| BR-06 | Username unik, minimal 4 karakter. |
| BR-07 | Registrasi mandiri hanya mengizinkan peran `operator` dan `petani`. |
| BR-08 | Password minimal 6 karakter dan sama dengan konfirmasi; disimpan sebagai SHA-256 bersalt. |
| BR-09 | Alokasi berstatus `Terkirim` bersifat final. |
| BR-10 | Berat baru lot panen minimal sebesar total yang sudah dialokasikan. |

---

## 15. Troubleshooting

| Gejala | Penyebab & Solusi |
|---|---|
| `Can't connect to MySQL server on 'localhost:3306'` | Layanan MySQL Laragon belum aktif — klik **Start All**. |
| `Koneksi database gagal` saat login | Periksa `AGRIUNO_DB_*` dan pastikan `database.sql` sudah dijalankan. |
| `Username atau Password salah!` | Gunakan akun demo pada tabel **Akun Demo**, atau daftar akun baru. |
| Jendela splash tidak berganti ke login | Pastikan `assets/anim/` lengkap (24 berkas PNG). Bangkit ulang dengan `python tools/generate_logo.py`. |
| Logo tidak tampil | Jalankan `python tools/generate_logo.py` untuk membangkitkan ulang aset. |
| `ModuleNotFoundError: customtkinter` | Aktivasi lingkungan virtual lalu `pip install -r requirements.txt`. |
| Pengujian `db` dilewati | MySQL belum aktif. Jalankan Laragon **Start All** lalu `pytest -m db`. |
| Karakter `—` atau `“”` tampil salah | Berkas sumber tersimpan sebagai UTF-8 — gunakan VS Code dengan pengkodean UTF-8. |

---

## Lisensi

Digunakan untuk keperluan pendidikan dalam mata kuliah Rekayasa Perangkat
Lunak, Universitas Tadulako, tahun 2026.
