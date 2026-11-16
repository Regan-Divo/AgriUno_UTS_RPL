# Panduan Lingkungan Kerja dan Continuous Integration

Lampiran Bagian 6 (Lingkungan Kerja) dan pipeline CI pada laporan teknis UAS.

## Lingkungan Kerja
- **Python 3.10+** sebagai bahasa utama.
- **CustomTkinter** untuk antarmuka, **tkinter.ttk.Treeview** untuk tabel data,
  **mysql-connector-python** untuk basis data.
- **MySQL 8.x** (Laragon) sebagai basis data lokal `agriuno`.
- **pytest** untuk pengujian otomatis, **ruff** untuk pemeriksaan gaya kode.

## Menjalankan Pengujian
```
pytest -q                 # seluruh pengujian inti
pytest -v                 # tampilkan nama setiap skrip
pytest -m db              # hanya skrip yang memerlukan MySQL aktif
```

## Pipeline GitHub Actions
Berkas `.github/workflows/ci_pipeline.yml` menjalankan otomatis:
1. Instal dependensi (`requirements.txt`).
2. Menjalankan `pytest` beserta laporan cakupan (`pytest-cov`).
3. Menjalankan pemeriksaan gaya kode (`ruff`).

Setiap push ke branch `main` memicu pipeline; lencana status dapat ditaruh pada
README repositori sebagai bukti pengujian otomatis.

## Aturan Commit
`feat(modul-N): uraian singkat perubahan` — contoh:
`feat(modul-1): lengkapi DFD Level 2 untuk proses 1.0 sampai 4.0`.
