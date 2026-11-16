# Spesifikasi Kebutuhan Sistem AgriUno

Dokumen ini menjadi lampiran Bagian 2 (Software Requirements Specification)
pada laporan teknis UAS.

## 2.1 Gambaran Produk
AgriUno adalah aplikasi desktop (Python + CustomTkinter) untuk mengelola data
petani penyetor, lot setoran panen, dan alokasi pengiriman komoditas pada gudang
penampungan hasil panen. Arsitektur MVC, basis data MySQL (tabel `agriuno`).

## 2.2 Daftar Aktor dan Hak Akses

| ID | Aktor | Hak Akses Utama |
|----|-------|-----------------|
| ACT-01 | Admin Gudang | Kelola seluruh modul, termasuk hapus data dan pemeliharaan akun pengguna |
| ACT-02 | Petani Terdaftar | Login, melihat dashboard ringkasan, mengubah kata sandi, keluar |
| ACT-03 | Operator Gudang | Kelola data petani, setoran panen, alokasi, dan status pengiriman (tanpa hapus) |
| ACT-04 | Pengguna Baru | Registrasi akun baru (peran operator atau petani) |

Matriks hak akses (`config/constants.py`):

| Peran | kelola | hapus |
|-------|--------|-------|
| admin | Ya | Ya |
| operator | Ya | Tidak |
| petani | Tidak | Tidak |

## 2.3 Kebutuhan Fungsional

| ID | Nama | Aktor | Prioritas |
|----|------|-------|-----------|
| FR-01 | Login ke Sistem | ACT-01, ACT-02, ACT-04 | Must |
| FR-02 | Melihat Dashboard Ringkasan | ACT-01, ACT-02 | Must |
| FR-03 | Mengelola Data Petani | ACT-01, ACT-03 | Must |
| FR-04 | Mencatat Setoran Panen | ACT-01, ACT-03 | Must |
| FR-05 | Mengalokasikan Pengiriman | ACT-01, ACT-03 | Must |
| FR-06 | Keluar dari Aplikasi | ACT-01, ACT-02 | Must |
| FR-07 | Memperbarui Status Pengiriman | ACT-01, ACT-03 | Must |
| FR-08 | Registrasi Akun Baru | ACT-04 | Must |
| FR-09 | Mengubah Kata Sandi Pengguna | ACT-01, ACT-02 | Should |
| FR-10 | Kelola Akun Pengguna | ACT-01 | Should |

## 2.4 Kebutuhan Non-Fungsional

| ID | Kategori | Spesifikasi |
|----|----------|-------------|
| NFR-01 | Kinerja | Tabel dan ringkasan tampil tanpa jeda mengganggu |
| NFR-02 | Keamanan | Parameterized query, hash SHA-256 bersalt, validasi masukan |
| NFR-03 | Keandalan | Galat koneksi ditangani dengan umpan balik yang dipahami pengguna |
| NFR-04 | Kemudahan | Tata letak form, tombol, sidebar, dan tabel konsisten |
| NFR-05 | Kompatibilitas | Berjalan pada Windows dengan dependensi proyek |
| NFR-06 | Pemeliharaan | Kode dipisah view, controller, model, dan komponen koneksi |
| NFR-07 | Kontrol akses | Fungsi menyesuaikan peran dan status aktif akun |

## 2.5 Aturan Bisnis

| ID | Aturan |
|----|--------|
| BR-01 | Setoran wajib memakai id_petani terdaftar; petani berriwayat panen aktif tidak dapat dihapus |
| BR-02 | Jumlah kirim tidak melebihi sisa stok; berat lot tidak boleh dikecilkan di bawah total alokasi |
| BR-03 | Sisa stok = jumlah_berat - total jumlah_dikirim |
| BR-04 | Alokasi baru selalu berstatus awal Diproses |
| BR-05 | Status hanya Diproses, Dalam Pengiriman, atau Terkirim |
| BR-06 | Username registrasi minimal 4 karakter dan unik |
| BR-07 | Kata sandi minimal 6 karakter, konfirmasi sama, hash SHA-256 bersalt acak |
| BR-08 | Registrasi hanya mengizinkan peran operator atau petani |
| BR-09 | Alokasi berstatus Terkirim bersifat final (tidak dapat diubah atau dihapus) |
| BR-10 | Berat lot baru minimal sebesar total alokasi yang sudah tercatat |
| BR-11 | Kombinasi nama, lokasi lahan, dan komoditas utama petani harus unik |
