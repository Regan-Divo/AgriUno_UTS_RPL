# Rancangan Arsitektur Sistem AgriUno

Lampiran Bagian 6.1 (Arsitektur Sistem) pada laporan teknis UAS.

## Lapisan Arsitektur

| Lapisan | Isi | Peran |
|---------|-----|-------|
| Presentasi (View) | `views/`, `config/ui_kit.py` | Tampilan, formulir, tabel, toast, dan dialog |
| Kontrol (Controller) | `controllers/controller.py`, `controllers/auth_controller.py`, `controllers/user_controller.py` | Perantalah tampilan dan model, validasi hak akses |
| Model | `models/` | Akses basis data dan aturan bisnis BR-01 s.d. BR-11 |
| Infrastruktur | `config/database.py`, `config/mesin_database.py` | Koneksi MySQL dan penyalaan mesin data bawaan |

## Alur Data Utama
1. Pengguna melakukan interaksi pada halaman (View).
2. View memanggil `AgriUnoController` (tanpa menyimpan state bisnis).
3. Controller memanggil model; model memakai `config/database.py` (context
   manager `kursor()` dengan commit/rollback eksplisit).
4. Hasil kembali ke View untuk ditampilkan sebagai tabel, panel detail, atau toast.

## Atribut Kualitas
- **Keamanan**: parameterized query, hash SHA-256 bersalt, RBAC per peran.
- **Keandalan**: transaksi atomik dengan `SELECT ... FOR UPDATE` pada pemeriksaan
  sisa stok (BR-02) dan penanganan galat errno 1451 (BR-01).
- **Pemeliharaan**: pemisahan view-controller-model, 97 skrip pengujian otomatis.
