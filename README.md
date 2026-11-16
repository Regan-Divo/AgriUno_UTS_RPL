# AgriUno — Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal

Aplikasi **desktop** untuk mengelola data petani penyetor, inventori lot panen,
dan alokasi pengiriman hasil panen pada gudang penampungan komoditas lokal.

Proyek Praktikum **Rekayasa Perangkat Lunak (RPL) 2026** — Kelompok 1, Kelas B.

> **Versi:** 2.0.0 (UAS — kelanjutan dari versi UTS 1.0)

---

## Daftar Isi

- [Ringkasan Proyek](#ringkasan-proyek)
- [Struktur Folder](#struktur-folder)
- [Menjalankan Aplikasi](#menjalankan-aplikasi)
- [Akun Demo](#akun-demo)
- [Pengujian Otomatis](#pengujian-otomatis)
- [Diagram](#diagram)
- [Keterlacakan Modul](#keterlacakan-modul)

---

## Ringkasan Proyek

| Aspek | Keterangan |
|-------|------------|
| Platform | Desktop (Windows) |
| Bahasa | Python 3.10+ |
| Antarmuka | CustomTkinter + tkinter.ttk.Treeview |
| Arsitektur | MVC (Model - View - Controller) |
| Basis data | MySQL 8.x (database `agriuno`, tabel `users`, `petani`, `inventori_panen`, `distribusi`) |
| Pengujian | pytest (97 skrip) + GitHub Actions |

## Struktur Folder

```
AgriUno/
├── .github/workflows/     pipeline CI (pytest + pytest-cov + ruff)
├── AgriUno-Studio/        aplikasi utama UAS (satu jendela, mandiri)
│   ├── config/            konstanta, koneksi basis data, mesin data bawaan, kit UI
│   ├── controllers/       controller utama, autentikasi, pemeliharaan akun
│   ├── models/            model data (user, petani, panen, distribusi, dashboard)
│   ├── views/             splash, login, registrasi, dashboard, data, dialog
│   ├── tests/             skrip pengujian AgriUno Studio
│   └── dist/              hasil pemaketan (AgriUnoStudio.exe)
├── assets/                logo, ikon, dan 24 frame animasi splash
├── config/                konstanta, koneksi basis data, kit antarmuka
├── controllers/           controller aplikasi
├── docs/diagrams/         berkas .drawio + PNG seluruh diagram
├── models/                model data AgriUno
├── runtime/               mesin MySQL portable saat membangun ulang exe
├── tests/                 skrip pengujian otomatis
├── tools/                 perkakas pembangun diagram dan laporan
├── views/                 tampilan aplikasi AgriUno
├── database.sql           skema empat tabel dan data contoh
├── main.py                titik masuk aplikasi
└── pytest.ini             konfigurasi pengujian
```

## Menjalankan Aplikasi

**Cara paling mudah (tanpa memasang apa pun):**

1. Unduh `AgriUnoStudio-UAS-RPL-2026.zip` dari bagian *Releases*.
2. Ekstrak, lalu jalankan `AgriUnoStudio.exe`.
3. Pemakaian pertama membutuhkan sekitar 30–60 detik (aplikasi menyiapkan
   mesin basis datanya sendiri). Setelah itu, aplikasi langsung terbuka.

**Dari kode sumber:**

```bash
pip install -r requirements.txt
python main.py
```

**Membangun ulang exe:**

```bash
# kembalikan mesin MySQL portable ke runtime/ (lihat runtime/README.txt)
pyinstaller AgriUno-Studio.spec
```

## Akun Demo

| Username | Password | Peran | Hak Akses |
|----------|----------|-------|-----------|
| `admin` | `admin123` | Administrator | Kelola penuh, termasuk hapus dan pemeliharaan akun |
| `operator` | `operator123` | Operator Gudang | Kelola data tanpa hapus |
| `petani` | `petani123` | Petani | Akses baca rekapitulasi |

## Pengujian Otomatis

```bash
pytest -q                      # 77 skrip (inti AgriUno)
cd AgriUno-Studio && pytest -q  # 20 skrip (AgriUno Studio)
```

Pipeline GitHub Actions menjalankan pengujian dan pemeriksaan kualitas kode
(`ruff check` + `ruff format --check`) pada setiap push dan Pull Request.

## Diagram

Seluruh diagram tersedia dalam dua format pada `docs/diagrams/`:

| Berkas | Isi |
|--------|------|
| `03_Diagram_Konteks.drawio` | Diagram Konteks (DFD Level 0) |
| `03_DFD_Level_1.drawio` | DFD Level 1 |
| `03_DFD_L2_Proses_1_0.drawio` … `_4_0` | DFD Level 2 (proses 1.0 – 4.0) |
| `04_Use_Case_Diagram.drawio` | Use Case Diagram (10 use case, 4 aktor) |
| `04_Sequence_Diagram_UC-*.drawio` | Sequence Diagram UC-01 s.d. UC-10 |
| `04_Activity_Diagram*.drawio` | Activity Diagram alokasi pengiriman dan splash |
| `04_Class_Diagram.drawio` | Class Diagram |
| `05_Entity_Relationship_Diagram.drawio` | Entity Relationship Diagram |
| `06_Arsitektur_Sistem.drawio` | Arsitektur Sistem |
| `06_Diagram_Navigasi.drawio` | Diagram Navigasi / Sitemap |

Berkas `.drawio` dapat dibuka dan diedit melalui draw.io Desktop.

## Keterlacakan Modul

| Modul | Nama Anggota | Kontribusi |
|-------|--------------|------------|
| 1 — Konsep dasar, DFD, dan UML | Yuda Pramesta | Diagram Konteks, DFD Level 1 dan 2, serta diagram UML |
| 1 — Analisis kebutuhan | Widyo Prabowo | Spesifikasi kebutuhan fungsional, non-fungsional, dan aturan bisnis |
| 2 — Arsitektur dan basis data | Sinaan Az Zufar | Entity Relationship Diagram, Diagram Arsitektur, dan rancangan basis data |
| 3 — Lingkungan kerja, VCS, dan CI | Aura Qadriandhara | Pipeline GitHub Actions, konfigurasi pytest dan ruff |
| 4 — Model Python dan integrasi MySQL | Kissya Syahluna R | Model data dan skrip pengujian model |
| 5 & 1 — Antarmuka dan pemodelan | Regan Musholli Divo Rasjid | Aplikasi AgriUno Studio, class diagram, dan navigasi antarmuka |

---

© 2026 Kelompok 1 — Praktikum Rekayasa Perangkat Lunak, Universitas Tadulako.
