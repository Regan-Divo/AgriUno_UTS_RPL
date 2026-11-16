"""
==========================================================
KONTEN LAPORAN UAS - AGRIUNO (RPL 2026)
==========================================================
Seluruh teks dan isi tabel yang diselaraskan dengan kode sumber
AgriUno versi UAS. Data di berkas ini menjadi sumber kebenaran
saat laporan dokumen (.docx) dibangun ulang oleh
``tools/build_report.py``.

Perubahan utama terhadap versi UTS:
  * Tabel ``users`` (autentikasi dan registrasi) ditambahkan.
  * Aturan bisnis BR-06 s.d. BR-09 (RBAC dan status final) ditambahkan.
  * Kebutuhan fungsional FR-09 s.d. FR-11 (registrasi, splash, logout)
    ditambahkan.
  * Aktor ACT-04 (Pengguna Baru) dan ACT-05 (Petani Terdaftar) ditambahkan.
  * Nine use case (UC-08 dan UC-09) ditambahkan.
  * Seluruh narasi dan pesan galat diselaraskan dengan implementasi
    kode terbaru (dropdown penyetor, kolom sisa stok, transaksi
    database dengan penguncian baris, dan hashing SHA-256 bersalt).
"""

# ============================================================
# LEMBAR KENDALI DOKUMEN
# ============================================================
KENDALI = {
    "Nama proyek": "AgriUno — Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal",
    "Kode proyek": "RPL-2026-K1-B-AGRIUNO",
    "Versi dokumen": "2.0",
    "Tanggal penyusunan": "13 November 2026",
    "Status": "Diajukan untuk Presentasi UAS",
    "Ketua kelompok": "Regan Musholli Divo Rasjid (F5212520064)",
    "Repositori": "https://github.com/Regan-Divo/AgriUno_UAS_RPL",
    "Folder artefak": "AgriUno/ (kode sumber, docs/diagrams, assets, database.sql)",
}

RIWAYAT_PERUBAHAN = [
    ("0.1", "08 Oktober 2026", "Kelompok 1", "Pembuatan awal dokumen UTS"),
    ("1.0", "12 Oktober 2026", "Kelompok 1", "Versi UTS: modul 1 s.d. modul 6 selesai"),
    (
        "2.0",
        "13 November 2026",
        "Kelompok 1",
        "Versi UAS: modul 7 (autentikasi, registrasi akun, RBAC) dan modul 8 "
        "(logo, animasi splash, CI/CD, dan pemaketan) ditambahkan; seluruh "
        "diagram dan tabel diselaraskan dengan kode sumber terbaru",
    ),
]

# ============================================================
# 1. INFORMASI UMUM PROYEK
# ============================================================
IDENTITAS = [
    ("Nama sistem", "AgriUno — Sistem Informasi Pengelolaan Hasil Panen Pertanian Lokal"),
    ("Studi kasus", "Pengelolaan hasil panen pada gudang penampungan komoditas lokal"),
    (
        "Klien/pengguna sasaran",
        "Admin Gudang (peran admin dan operator) sebagai operator utama. "
        "Petani Terdaftar (peran petani) memperoleh akses baca atas rekapitulasi. "
        "Pengguna Baru dapat mendaftar akun secara mandiri. Petani penyetor dan "
        "Distributor tetap tercermin sebagai data yang dikelola, bukan sebagai "
        "pengguna aplikasi.",
    ),
    ("Platform", "Desktop — aplikasi jendela Windows (bukan web/mobile)"),
    (
        "Bahasa/framework",
        "Python 3.10+; CustomTkinter (antarmuka); tkinter.ttk.Treeview (tabel "
        "data); tkinter.Canvas (animasi splash); mysql-connector-python (koneksi "
        "basis data); Arsitektur Model-View-Controller",
    ),
    (
        "Basis data",
        "MySQL 8.0 Community Server (Laragon), database bernama agriuno dengan "
        "empat tabel: users, petani, inventori_panen, dan distribusi",
    ),
    ("Metode SDLC", "Waterfall dengan iterasi per modul"),
    (
        "Periode pengerjaan",
        "9 Oktober 2026 – 13 November 2026 (UTS 9 s.d. 12 Oktober 2026; "
        "UAS 13 Oktober s.d. 13 November 2026)",
    ),
    ("Versi aplikasi", "2.0.0 (UAS RPL 2026)"),
    ("Lisensi dan sumber", "Bebas digunakan untuk keperluan pendidikan"),
]

TUJUAN = [
    (
        "OBJ-01",
        "Mengelola data petani penyetor.",
        "Data identitas, lokasi lahan, dan komoditas utama petani dapat ditambah, "
        "diubah, dan dihapus serta ditampilkan dalam tabel.",
    ),
    (
        "OBJ-02",
        "Mencatat lot setoran panen dan memantau stok inventori.",
        "Setiap setoran panen memiliki ID, jenis komoditas, berat (Kg), dan "
        "tanggal; rekapitulasi stok bertambah setiap kali setoran baru dicatat "
        "dan sisa stok setiap lot ditampilkan pada tabel.",
    ),
    (
        "OBJ-03",
        "Mengalokasikan dan mengelola status pengiriman.",
        "Alokasi dapat dicatat terhadap lot panen tertentu, jumlah kirim "
        "divalidasi terhadap sisa stok dalam satu transaksi basis data, dan "
        "status dapat diubah antar tiga tahapan.",
    ),
    (
        "OBJ-04",
        "Menyediakan rekapitulasi operasional.",
        "Jumlah petani, jumlah lot panen, jumlah alokasi, dan indikator kinerja "
        "rantai pasok ditampilkan pada kartu statistik Dashboard.",
    ),
    (
        "OBJ-05",
        "Melindungi data sistem melalui autentikasi dan otorisasi.",
        "Kredensial pengguna diverifikasi terhadap tabel users menggunakan hash "
        "SHA-256 bersalt; setiap sesi pengguna memiliki peran yang membatasi "
        "modul yang dapat diakses.",
    ),
    (
        "OBJ-06",
        "Memungkinkan pengguna baru membuat akun secara mandiri.",
        "Pengguna dapat mendaftar melalui menu Registrasi dengan mengisi nama "
        "lengkap, username, password, dan peran operator atau petani; akun "
        "langsung dapat digunakan untuk login.",
    ),
    (
        "OBJ-07",
        "Menyediakan identitas visual dan pengalaman pembukaan yang baik.",
        "Aplikasi memiliki logo AgriUno dan animasi splash berupa logo yang "
        "muncul bertahap, cincin orbit, serta progress bar sebelum jendela login "
        "tampil.",
    ),
    (
        "OBJ-08",
        "Menjamin kualitas rilis melalui pengujian otomatis dan pemaketan.",
        "Seluruh skrip pengujian berstatus lulus pada pipeline GitHub Actions, "
        "dan aplikasi dapat dipaketkan menjadi berkas eksekusi mandiri (.exe).",
    ),
]

RUANG_LINGKUP = [
    (
        "Autentikasi dan Registrasi\nForm login dengan verifikasi kredensial "
        "terhadap tabel users, serta halaman pendaftaran akun baru yang "
        "menyediakan peran operator dan petani.",
        "Manajemen hak akses / multi-user\nTidak ada peran selain Admin Gudang; "
        "seluruh operasi dilakukan oleh satu operator.",
    ),
    (
        "Pengelolaan Data Petani\nTambah, ubah, hapus, dan tampilkan data "
        "petani penyetor (tabel petani).",
        "Pencarian dan penyaringan data\nTidak ada kolom pencarian atau filter; "
        "seluruh baris ditampilkan apa adanya.",
    ),
    (
        "Pencatatan Setoran Panen\nTambah, ubah, hapus, dan tampilkan lot panen "
        "masuk (tabel inventori_panen), termasuk perhitungan sisa stok.",
        "Transaksi keuangan dan E-Commerce\nTidak ada kasir, nota harga, "
        "pembayaran, maupun keranjang belanja.",
    ),
    (
        "Alokasi dan Status Pengiriman\nTambah, ubah status, hapus, dan "
        "tampilkan alokasi (tabel distribusi) dengan validasi stok atomik.",
        "Pelacakan armada / GPS dan proses cultivation\nTidak ada data kendaraan, "
        "identitas pengemudi, jadwal tanam, maupun pemupukan.",
    ),
    (
        "Otorisasi Berbasis Peran\nTiga peran pengguna (admin, operator, "
        "petani) dengan pembatasan modul sesuai haknya pada antarmuka.",
        "Manajemen akun oleh pengguna biasa\nHanya Administrator yang dapat "
        "mengaktifkan, menonaktifkan, atau menghapus akun pengguna.",
    ),
    (
        "Antarmuka Pembuka\nLogo AgriUno, animasi splash selama 3 detik, dan "
        "halaman login sebagai pintu masuk aplikasi.",
        "Aplikasi berbasis web atau mobile\nAgriUno hanya berjalan pada "
        "lingkungan desktop Windows.",
    ),
]

STAKEHOLDER = [
    (
        "STK-01",
        "Admin Gudang (Pengguna Akhir & Operasional)",
        "Mengoperasikan AgriUno untuk mencatat setoran panen, memantau stok, "
        "mengatur pengiriman, serta mengelola akun pengguna.",
        "Antarmuka yang sederhana agar pencatatan cepat dan tidak salah; data "
        "stok terlihat akurat; hak akses penuh atas seluruh modul.",
    ),
    (
        "STK-02",
        "Petani Penyetor (Klien)",
        "Menyerahkan hasil panen dan memberikan data identitas kepada pengelola gudang.",
        "Data identitas dan berat setorannya tercatat dengan benar dan dapat dibuktikan kembali.",
    ),
    (
        "STK-03",
        "Distributor (Klien / Penerima)",
        "Menerima pasokan komoditas hasil panen dari gudang.",
        "Kepastian jumlah barang yang dikirim dan kejelasan status pengirimannya.",
    ),
    (
        "STK-04",
        "Operator Gudang (Pengguna Sistem)",
        "Menjalankan operasional harian gudang dengan hak akses mengelola data "
        "petani, panen, dan distribusi.",
        "Dapat mengisi dan memperbarui data tanpa terhalang oleh pembatasan "
        "peran; penghapusan data dan pengelolaan akun pengguna lain hanya "
        "dapat dilakukan Administrator.",
    ),
    (
        "STK-05",
        "Petani Terdaftar (Pengguna Sistem)",
        "Pengguna dengan peran petani yang memperoleh akses baca atas "
        "rekapitulasi operasional gudang.",
        "Hanya dapat melihat ringkasan data; tidak dapat mengubah atau menghapus data apa pun.",
    ),
    (
        "STK-06",
        "Pengguna Baru (Pengguna Sistem)",
        "Pengguna yang belum memiliki akun dan mendaftar secara mandiri melalui "
        "halaman Registrasi.",
        "Pendaftaran mudah tanpa perlu bantuan administrator; akun langsung "
        "dapat digunakan untuk login.",
    ),
    (
        "STK-07",
        "Tim Pengembang (Kelompok 1)",
        "Membangun aplikasi AgriUno, merancang diagram, dan menyusun dokumentasi UTS maupun UAS.",
        "Dokumen dan diagram harus konsisten dengan kode yang benar-benar diimplementasikan.",
    ),
    (
        "STK-08",
        "Asisten Praktikum RPL (Evaluator)",
        "Membimbing dan mengevaluasi hasil proyek pada tahap UTS maupun UAS.",
        "Hasil kerja sesuai dengan modul pembelajaran dan kriteria penilaian.",
    ),
]

# ============================================================
# 2. SRS
# ============================================================
AKTOR = [
    (
        "ACT-01",
        "Admin Gudang",
        "Petugas internal gudang yang mengoperasikan aplikasi dengan akses penuh ke seluruh modul.",
        "Akses penuh (full access): login, logout, melihat dashboard, menambah, "
        "mengubah, menghapus, dan menampilkan data petani, lot panen, serta "
        "alokasi pengiriman, serta mengelola akun pengguna.",
    ),
    (
        "ACT-02",
        "Petani",
        "Pihak eksternal penyetor komoditas hasil panen ke gudang.",
        "Tidak memiliki akses langsung ke sistem (non-user). Data identitas dan "
        "setoran panen dicatat oleh Admin Gudang melalui kolom isian yang "
        "tersedia.",
    ),
    (
        "ACT-03",
        "Distributor",
        "Pihak eksternal penerima pasokan komoditas hasil panen dari gudang.",
        "Tidak memiliki akses langsung ke sistem (non-user). Alokasi barang "
        "keluar dan pembaruan status pengiriman dikelola oleh Admin Gudang.",
    ),
    (
        "ACT-04",
        "Pengguna Baru",
        "Pengguna yang belum memiliki akun dan ingin mendaftar menjadi pengguna aplikasi.",
        "Registrasi akun baru (nama lengkap, username, password, dan peran "
        "operator atau petani), kemudian login ke aplikasi.",
    ),
    (
        "ACT-05",
        "Petani Terdaftar",
        "Pengguna dengan peran 'petani' yang telah melakukan registrasi.",
        "Akses baca: login, logout, melihat Dashboard Ringkasan, dan mengubah "
        "kata sandi miliknya sendiri.",
    ),
]

FUNGSIONAL = [
    (
        "FR-01",
        "Autentikasi Pengguna",
        "Sistem harus dapat memvalidasi kredensial pengguna terhadap tabel "
        "users sebelum membuka jendela utama aplikasi.",
        "ACT-01, ACT-04, ACT-05",
        "Must",
        "Given jendela login terbuka, When pengguna memasukkan username dan "
        "password yang sesuai, Then jendela utama AgriUno terbuka dan panel "
        "profil menampilkan nama serta peran pengguna. Otherwise pesan "
        "“Username atau Password salah!” ditampilkan secara inline.",
    ),
    (
        "FR-02",
        "Menampilkan Dashboard Ringkasan",
        "Sistem harus dapat menampilkan jumlah total petani, lot panen, alokasi "
        "distribusi, serta ringkasan berat serta indikator kinerja yang "
        "dihitung dari data nyata.",
        "ACT-01, ACT-05",
        "Must",
        "Given halaman Dashboard dibuka, When fungsi load_data() dipanggil, "
        "Then tiga kartu statistik, panel ringkasan berat, dan tiga progress "
        "bar indikator menampilkan angka hasil pembacaan basis data.",
    ),
    (
        "FR-03",
        "Mengelola Data Petani",
        "Sistem harus dapat menambah, mengubah, dan menghapus data identitas petani penyetor "
        "dengan penulisan teks baku dan pemeriksaan keunikan data (BR-11).",
        "ACT-01, ACT-04",
        "Must",
        "Given kolom Nama, Lokasi Lahan, dan Komoditas Utama terisi, When Admin "
        "menekan Simpan, Then sistem menormalkan penulisan, menolak data identik "
        "yang sudah tercatat (BR-11), menyimpan data di tabel petani, dan tabel "
        "antarmuka dimuat ulang.",
    ),
    (
        "FR-04",
        "Mencatat Setoran Panen",
        "Sistem harus dapat menambah, mengubah, dan menghapus lot setoran panen "
        "yang masuk ke gudang.",
        "ACT-01, ACT-04",
        "Must",
        "Given penyetor dipilih dari kotak daftar, When Admin memilih penyetor, "
        "Then jenis komoditas terisi otomatis sesuai master data petani (BR-11); "
        "setelah Admin mengisi berat dan tanggal lalu menekan Simpan, data tersimpan "
        "di tabel inventori_panen dan kolom Sisa Stok pada tabel terisi.",
    ),
    (
        "FR-05",
        "Mengalokasikan Pengiriman",
        "Sistem harus dapat membuat, mengubah, dan menghapus alokasi pengiriman "
        "komoditas dari gudang ke distributor dengan validasi sisa stok.",
        "ACT-01, ACT-04",
        "Must",
        "Given jumlah yang dikirim tidak melebihi sisa stok lot, When Admin "
        "menekan Simpan, Then data tersimpan di tabel distribusi dan stok lot "
        "tersebut otomatis terpakai.",
    ),
    (
        "FR-06",
        "Memperbarui Status Pengiriman",
        "Sistem harus dapat mengubah tahapan status perjalanan pengiriman yang "
        "sedang dialokasikan.",
        "ACT-01, ACT-03",
        "Must",
        "Given baris alokasi dipilih dari tabel, When Admin memilih status "
        "pada kotak pilihan lalu menekan Ubah Status, Then kolom "
        "status_pengiriman pada tabel distribusi diperbarui.",
    ),
    (
        "FR-07",
        "Validasi Input dan Penanganan Galat",
        "Sistem harus dapat menolak masukan yang tidak valid dan menampilkan "
        "pesan kesalahan yang informatif.",
        "ACT-01, ACT-04, ACT-05",
        "Must",
        "Given kolom wajib terisi kosong atau nilai numerik tidak valid, When "
        "Admin menekan Simpan, Then penyimpanan dibatalkan dan kotak dialog pesan "
        "galat ditampilkan tanpa merusak basis data.",
    ),
    (
        "FR-08",
        "Menghentikan Aplikasi",
        "Sistem harus dapat mengakhiri sesi aplikasi melalui tombol Keluar pada sidebar.",
        "ACT-01, ACT-05",
        "Could",
        "Given jendela utama terbuka, When Admin menekan tombol Keluar, Then sesi "
        "diakhiri dan jendela login ditampilkan kembali.",
    ),
    (
        "FR-09",
        "Registrasi Akun Pengguna",
        "Sistem harus dapat menyediakan pendaftaran akun baru bagi pengguna yang "
        "belum memiliki akun.",
        "ACT-04",
        "Must",
        "Given formulir registrasi terisi lengkap dan peran yang dipilih adalah "
        "operator atau petani, When pengguna menekan Daftar Sekarang, Then akun "
        "tersimpan pada tabel users dan dapat langsung digunakan untuk login.",
    ),
    (
        "FR-10",
        "Menampilkan Logo dan Animasi Splash",
        "Sistem harus dapat menampilkan logo AgriUno beserta animasi pembuka "
        "sebelum jendela login tampil.",
        "ACT-01, ACT-04, ACT-05",
        "Must",
        "Given aplikasi dijalankan, When jendela splash tampil, Then logo "
        "AgriUno muncul secara bertahap, cincin orbit berputar, progress bar "
        "terisi hingga 100%, dan jendela login tampil secara otomatis.",
    ),
    (
        "FR-11",
        "Mengubah Kata Sandi Pengguna",
        "Sistem harus dapat memungkinkan pengguna mengubah kata sandinya sendiri "
        "dengan verifikasi kata sandi lama.",
        "ACT-01, ACT-05",
        "Could",
        "Given kata sandi lama sesuai, When pengguna memasukkan kata sandi baru "
        "minimal 6 karakter beserta konfirmasi, Then kata sandi tersimpan "
        "sebagai hash SHA-256 bersalt yang baru.",
    ),
]

NON_FUNGSIONAL = [
    (
        "NFR-01",
        "Kinerja",
        "Setiap operasi baca data pada antarmuka memerlukan waktu lebih kurang "
        "dari 2 detik untuk volume data hingga 10.000 baris per tabel.",
        "Uji respon waktu kueri SELECT pada tabel users, petani, inventori_panen, dan distribusi.",
    ),
    (
        "NFR-02",
        "Keamanan",
        "Seluruh kueri SQL pada berkas model menggunakan parameter binding (%s), "
        "dan kata sandi pengguna disimpan sebagai hash SHA-256 dari kombinasi "
        "salt acak per pengguna serta dibandingkan memakai "
        "hmac.compare_digest().",
        "Inspeksi sintaks kueri pada models/*.py, uji masukan berisi tanda kutip "
        "ganda, dan uji kesamaan hash pada tests/test_auth.py.",
    ),
    (
        "NFR-03",
        "Keandalan",
        "Penghapusan data yang masih terikat relasi ditolak dengan pesan yang "
        "jelas (penanganan galat errno 1451), transaksi alokasi dijalankan "
        "atomik dengan penguncian baris, dan kegagalan koneksi ditangani tanpa "
        "menghentikan aplikasi.",
        "Uji penghapusan petani yang memiliki riwayat panen, uji alokasi melebihi "
        "stok, dan simulasi penghentian layanan MySQL.",
    ),
    (
        "NFR-04",
        "Kemudahan penggunaan",
        "Seluruh fungsi penting dapat diakses melalui sidebar navigasi yang "
        "tidak berubah, pemilihan penyetor dan lot panen memakai kotak daftar "
        "terisi otomatis, dan setiap aksi selesai dengan kotak dialog sukses "
        "atau galat.",
        "Uji inspeksi navigasi, uji isi kotak daftar penyetor dan lot, dan uji "
        "klik pada setiap tombol aksi.",
    ),
    (
        "NFR-05",
        "Kompatibilitas",
        "Aplikasi berjalan pada Windows 10 dan Windows 11 dengan Python 3.10 atau "
        "lebih baru serta MySQL 8.0 melalui Laragon.",
        "Uji eksekusi aplikasi pada dua unit laptop/PC.",
    ),
    (
        "NFR-06",
        "Pemeliharaan",
        "Struktur berkas dipisah mengikuti pola MVC (models/, controllers/, "
        "views/, config/) dan setiap entitas data memiliki satu kelas model "
        "tersendiri; seluruh diagram dilaporkan dibangkitkan ulang oleh skrip "
        "tools/generate_diagrams.py.",
        "Inspeksi struktur folder, pemetaan kelas model terhadap tabel, dan "
        "hasil pembangkitan ulang diagram.",
    ),
    (
        "NFR-07",
        "Ketersediaan aplikasi",
        "Aplikasi dapat dijalankan pada kondisi basis data MySQL tidak aktif "
        "tanpa menyebabkan crash; pesan galat koneksi ditampilkan dan "
        "aplicasi tetap dapat ditutup dengan rapi.",
        "Simulasi penghentian layanan MySQL saat aplikasi berjalan.",
    ),
]

ATURAN_BISNIS = [
    (
        "BR-01",
        "Setiap lot setoran panen wajib memiliki id_petani yang terisi "
        "dan menunjuk pada data petani yang tercatat.",
        "Menjaga integritas relasi data (Foreign Key) agar asal-usul komoditas "
        "panen dapat ditelusuri.",
    ),
    (
        "BR-02",
        "Jumlah yang dialokasikan ke distributor tidak boleh melebihi "
        "sisa stok lot tersebut, dengan perhitungan sisa_stok = jumlah_berat "
        "pada inventori_panen dikurangi SUM(jumlah_dikirim) pada distribusi untuk "
        "id_panen yang sama. Pemeriksaan dan penyimpanan dijalankan dalam satu "
        "transaksi dengan penguncian baris (SELECT ... FOR UPDATE).",
        "Mencegah terjadinya stok minus (defisit) pada inventori gudang, termasuk "
        "pada saat dua permintaan pengiriman berjalan bersamaan.",
    ),
    (
        "BR-03",
        "id_panen yang dirujuk pada sebuah alokasi wajib terdaftar pada "
        "tabel inventori_panen sebelum data alokasi disimpan.",
        "Menjamin setiap alokasi benar-benar berasal dari lot panen yang tersedia di gudang.",
    ),
    (
        "BR-04",
        "Alokasi pengiriman yang baru dibuat otomatis memperoleh status awal “Diproses”.",
        "Menjaga agar alur tahapan distribusi berjalan berurutan mulai dari "
        "penyiapan barang di gudang.",
    ),
    (
        "BR-05",
        "Kolom status_pengiriman hanya menerima tiga nilai baku, yaitu "
        "“Diproses”, “Dalam Pengiriman”, dan “Terkirim”.",
        "Menjaga konsistensi nilai status sehingga rekapitulasi distribusi tetap "
        "dapat dibaca secara seragam.",
    ),
    (
        "BR-06",
        "Username pengguna wajib unik, memiliki panjang minimal 4 "
        "karakter, dan hanya boleh memuat huruf, angka, titik, atau garis "
        "bawah.",
        "Menjaga setiap akun dapat diidentifikasi secara unik danmudah diketik oleh pengguna.",
    ),
    (
        "BR-07",
        "Peran yang dapat dipilih sendiri pada formulir registrasi "
        "hanya “operator” dan “petani”. Akun dengan peran “admin” hanya dapat "
        "dibuat oleh pengelola basis data melalui skrip database.sql.",
        "Mencegah pengguna mendaftarkan dirinya sebagai Administrator sehingga "
        "tidak terjadi penyalahgunaan hak akses.",
    ),
    (
        "BR-08",
        "Password pengguna wajib memiliki panjang minimal 6 karakter dan "
        "harus sama dengan konfirmasi password. Password disimpan sebagai hash "
        "SHA-256 dari (salt + password) dengan salt acak per pengguna.",
        "Menjaga keamanan kredensial dan mencegah kesalahan.input password yang "
        "tidak disadari pengguna.",
    ),
    (
        "BR-09",
        "Alokasi berstatus “Terkirim” bersifat final sehingga tidak dapat diubah maupun dihapus.",
        "Menjaga konsistensi riwayat pengiriman yang sudah selesai merupakan "
        "bukti sacado barang telah diterima.",
    ),
    (
        "BR-10",
        "Berat baru pada lot panen tidak boleh lebih kecil daripada "
        "total berat yang sudah dialokasikan kepada distributor.",
        "Menjaga agar pembaruan data lot tidak menimbulkan stok minus yang "
        "melewati pemeriksaan pada modul distribusi.",
    ),
    (
        "BR-11",
        "Data petani wajib unik: kombinasi nama petani, lokasi lahan, dan "
        "komoditas utama tidak boleh sama dengan data yang sudah tercatat. "
        "Seluruh teks isian dinormalkan terlebih dahulu (spasi rapat dan "
        "kapitalisasi gaya judul) sehingga perbedaan gaya penulisan seperti "
        "“JERUK” dan “Jeruk” tidak dihitung sebagai data berbeda. Pada modul "
        "panen, jenis komoditas juga otomatis mengikuti komoditas utama "
        "petani yang dipilih.",
        "Mencegah duplikasi master data akibat ketidaksengajaan pengguna "
        "mengetik ulang data yang sama dengan gaya penulisan berbeda, serta "
        "menjaga konsistensi antara master data petani dan catatan panen.",
    ),
]

ASUMSI = [
    (
        "Asumsi",
        "Pengguna/admin gudang mengoperasikan aplikasi pada PC atau "
        "laptop Windows yang sudah terpasang Python 3.10+ dan server Laragon "
        "MySQL dalam kondisi aktif.",
        "Pengembang dapat berfokus pada logika aplikasi desktop lokal tanpa "
        "perlu menangani konfigurasi lingkungan multi-platform yang kompleks.",
    ),
    (
        "Asumsi",
        "Pengguna baru yang mendaftar memahami mekanisme password "
        "minimal 6 karakter dan mampu mengingatnya sendiri.",
        "Proses registrasi dapat berlangsung mandiri tanpa keterlibatan Administrator.",
    ),
    (
        "Kendala",
        "Waktu pengerjaan proyek terikat oleh jadwal pengumpulan "
        "dokumen UTS dan UAS serta dikerjakan secara berbagi tugas dalam "
        "kelompok.",
        "Cakupan fitur dibatasi pada operasi inti (data petani, lot panen, "
        "alokasi distribusi, autentikasi, dan registrasi) agar pengerjaan "
        "selesai tepat waktu.",
    ),
    (
        "Kendala",
        "Server MySQL pada Laragon bersifat lokal sehingga basis data "
        "tidak dapat diakses dari perangkat lain.",
        "Seluruh pengujian integrasi dilakukan pada satu komputer yang "
        "menjalankan Laragon secara bersamaan.",
    ),
    (
        "Dependensi",
        "Aplikasi membutuhkan pustaka CustomTkinter, "
        "mysql-connector-python, serta layanan MySQL pada Laragon lokal yang "
        "aktif.",
        "Apabila pustaka pendukung belum terinstal atau layanan MySQL tidak "
        "aktif, aplikasi tidak dapat menjalankan modul yang memerlukan basis "
        "data.",
    ),
    (
        "Catatan teknis",
        "Nilai sisa stok tidak disimpan sebagai kolom "
        "tersendiri, melainkan dihitung ulang setiap kali data ditampilkan "
        "dengan LEFT JOIN antara inventori_panen dan distribusi.",
        "Data inventori_panen tetap berisi berat awal lot; rekapitulasi stok "
        "merupakan hasil hitungan, bukan data yang disimpan.",
    ),
    (
        "Catatan teknis",
        "Aset visual (logo dan 24 frame animasi) telah "
        "diprarender pada folder assets sehingga aplikasi tidak memerlukan "
        "pustaka Pillow saat dijalankan.",
        "Ukuran berkas executable tetap kecil dan proses pembukaan aplikasi "
        "tidak bergantung pada pemrosesan gambar.",
    ),
]

# ============================================================
# 3. PEMODELAN ALIRAN DATA
# ============================================================
KONTEKS_TABEL = [
    (
        "Admin Gudang (ACT-01)",
        "Data Login Pengguna; Data Master Petani; Data Setoran Panen; Data "
        "Alokasi Pengiriman; Update Status Pengiriman",
        "Hak Akses Sesi Aktif; Ringkasan Dashboard; Rekapitulasi Gudang",
    ),
    ("Pengguna Baru (ACT-04)", "Data Registrasi Akun", "Konfirmasi Registrasi Berhasil"),
    ("Petani (ACT-02)", "Data Identitas Petani", "Data Setoran Panen Tercatat"),
    (
        "Distributor (ACT-03)",
        "Permintaan Pasokan Komoditas",
        "Data Pengiriman dan Status Pengiriman",
    ),
]

DFD1_TABEL = [
    (
        "1.0",
        "Autentikasi dan Registrasi Pengguna",
        "Data Login Pengguna (Admin Gudang); Data Registrasi Akun (Pengguna Baru)",
        "Hak Akses Sesi Aktif (Admin Gudang); Konfirmasi Registrasi Berhasil (Pengguna Baru)",
        "D4 users (baca dan tulis)",
    ),
    (
        "2.0",
        "Kelola Data Petani",
        "Data Master Petani (Admin Gudang); Data Identitas Petani (Petani)",
        "Data Master Petani (D1); Data Setoran Panen Tercatat (Petani); "
        "Rekapitulasi Petani (Admin Gudang)",
        "D1 petani (baca dan tulis)",
    ),
    (
        "3.0",
        "Kelola Setoran Panen",
        "Data Setoran Panen (Admin Gudang); Data Petani Penyetor (D1)",
        "Data Setoran Panen (D2); Data Sisa Stok dan Rekapitulasi Setoran Panen (Admin Gudang)",
        "D1 petani (baca); D2 inventori_panen (baca dan tulis)",
    ),
    (
        "4.0",
        "Kelola Alokasi Distribusi",
        "Data Alokasi Pengiriman dan Update Status Pengiriman (Admin Gudang); "
        "Permintaan Pasokan Komoditas (Distributor); Data Stok dan Riwayat "
        "Alokasi Lot (D2)",
        "Data Alokasi Pengiriman (D3); Data Pengiriman dan Status Pengiriman "
        "(Distributor); Rekapitulasi Distribusi (Admin Gudang)",
        "D2 inventori_panen (baca); D3 distribusi (baca dan tulis)",
    ),
    (
        "5.0",
        "Tampilan Dashboard Ringkasan",
        "Data Rekapitulasi Petani, Setoran, dan Distribusi (D1, D2, D3)",
        "Ringkasan Dashboard dan Rekapitulasi Gudang (Admin Gudang)",
        "D1, D2, D3 (baca)",
    ),
]

KESEIMBANGAN = [
    (
        "Entitas konteks sama dengan Level 1",
        "Sesuai",
        "Keempat entitas eksternal pada Diagram Konteks (Admin Gudang, Pengguna "
        "Baru, Petani, dan Distributor) direpresentasikan lengkap pada DFD "
        "Level 1 dengan jenis aliran yang sama.",
    ),
    (
        "Aliran masuk/keluar seimbang",
        "Sesuai",
        "Seluruh aliran pada Diagram Konteks memiliki pasangan pada Level 1. "
        "Aliran “Rekapitulasi Gudang” terbagi menjadi tiga aliran turunan "
        "(Rekapitulasi Petani, Rekapitulasi Setoran Panen, dan Rekapitulasi "
        "Distribusi), dan aliran tersebut merupakan penguraian yang sah.",
    ),
    (
        "Tidak ada aliran entitas langsung ke data store",
        "Sesuai",
        "Seluruh aliran dari entitas luar wajib melewati proses. Penyimpanan ke "
        "D1, D2, D3, dan D4 hanya dilakukan melalui proses 1.0, 2.0, 3.0, dan "
        "4.0.",
    ),
    (
        "Setiap proses memiliki masukan dan keluaran",
        "Sesuai",
        "Proses 1.0–5.0 masing-masing memiliki minimal satu aliran masukan dan "
        "satu aliran keluaran yang jelas, termasuk keluaran berupa pembacaan dan "
        "penulisannya data store.",
    ),
    (
        "Nama dan penomoran konsisten",
        "Sesuai",
        "Penomoran proses induk (1.0–5.0) dan proses turunan pada Level 2 "
        "(1.1–1.3, 2.1–2.3, 3.1–3.3, 4.1–4.3) mengikuti aturan induk — anak. "
        "Penamaan data store D1–D4 selaras dengan nama tabel pada basis data.",
    ),
    (
        "Penambahan tahap UAS terdokumentasi",
        "Sesuai",
        "Aliran “Data Registrasi Akun” dan “Konfirmasi Registrasi Berhasil” "
        "berserta data store D4 users merupakan tambahan tahap UAS dan telah "
        "terentry pada DFD Level 1, DFD Level 2 proses 1.0, Use Case Diagram, "
        "Class Diagram, serta ERD.",
    ),
]

# ============================================================
# 4. PEMODELAN UML
# ============================================================
USE_CASE_DAFTAR = [
    (
        "UC-01",
        "Login ke Sistem AgriUno",
        "Admin Gudang (ACT-01), Pengguna Baru(ACT-04), Petani Terdaftar (ACT-05)",
        "Memastikan hanya pengguna terdaftar yang berhak membuka jendela utama aplikasi.",
        "Association",
    ),
    (
        "UC-02",
        "Melihat Dashboard Ringkasan",
        "Admin Gudang (ACT-01), Petani Terdaftar (ACT-05)",
        "Memantau jumlah petani, lot panen, alokasi distribusi, dan ringkasan berat.",
        "Association",
    ),
    (
        "UC-03",
        "Mengelola Data Petani",
        "Admin Gudang (ACT-01), Petani (ACT-02)",
        "Mendaftarkan dan mengelola profil identitas petani penyetor.",
        "Association",
    ),
    (
        "UC-04",
        "Mencatat Setoran Panen",
        "Admin Gudang (ACT-01), Petani (ACT-02)",
        "Mencatat jenis komoditas dan jumlah berat panen yang masuk ke gudang.",
        "Association",
    ),
    (
        "UC-05",
        "Mengalokasikan Pengiriman",
        "Admin Gudang (ACT-01), Distributor (ACT-03)",
        "Mengalokasikan stok panen untuk dikirimkan kepada penerima.",
        "Association",
    ),
    (
        "UC-06",
        "Keluar dari Aplikasi",
        "Admin Gudang (ACT-01), Petani Terdaftar (ACT-05)",
        "Mengakhiri sesi aplikasi dengan menutup seluruh jendela AgriUno.",
        "Association",
    ),
    (
        "UC-07",
        "Memperbarui Status Pengiriman",
        "Admin Gudang (ACT-01), Distributor (ACT-03)",
        "Mengubah tahapan status pengiriman dari gudang menuju penerima.",
        "Association",
    ),
    (
        "UC-08",
        "Registrasi Akun Baru",
        "Pengguna Baru (ACT-04)",
        "Mendaftarkan akun operator atau petani agar dapat mengakses AgriUno.",
        "Association",
    ),
    (
        "UC-09",
        "Mengubah Kata Sandi Pengguna",
        "Admin Gudang (ACT-01), Petani Terdaftar (ACT-05)",
        "Mengubah kata sandi sendiri dengan verifikasi kata sandi lama.",
        "Association",
    ),
]

# ============================================================
# 5. DATA DAN BASIS DATA
# ============================================================
DAFTAR_TABEL = [
    (
        "1",
        "users",
        "Menyimpan kredensial, identitas, dan peran setiap pengguna aplikasi "
        "beserta status aktifnya.",
        "id_user",
        "Berdiri sendiri tanpa foreign key; menyimpan kredensial seluruh jenis aktor",
    ),
    (
        "2",
        "petani",
        "Menyimpan data identitas, lokasi lahan, dan komoditas utama setiap petani penyetor.",
        "id_petani",
        "Berelasi satu ke banyak ke tabel inventori_panen",
    ),
    (
        "3",
        "inventori_panen",
        "Mencatat rincian lot hasil panen yang masuk ke gudang beserta berat "
        "awal dan tanggal panen.",
        "id_panen",
        "Berelasi banyak ke satu dari tabel petani dan satu ke banyak ke tabel distribusi",
    ),
    (
        "4",
        "distribusi",
        "Mengelola pencatatan alokasi pengiriman hasil panen beserta tujuan dan "
        "status logistiknya.",
        "id_distribusi",
        "Berelasi banyak ke satu dari tabel inventori_panen",
    ),
]

KAMUS_DATA = [
    (
        "users",
        "id_user",
        "INT",
        "Tidak",
        "PK",
        "Auto Increment",
        "Identifier unik untuk setiap akun pengguna.",
    ),
    (
        "users",
        "username",
        "VARCHAR(50)",
        "Tidak",
        "UNIQUE",
        "—",
        "Nama akun yang diketik pengguna saat login.",
    ),
    (
        "users",
        "password",
        "VARCHAR(255)",
        "Tidak",
        "—",
        "—",
        "Hash SHA-256 dari (salt + password). Teks asli tidak pernah disimpan.",
    ),
    (
        "users",
        "salt",
        "VARCHAR(64)",
        "Tidak",
        "—",
        "—",
        "Salt acak sepanjang 16 byte yang dibangkitkan untuk setiap pengguna.",
    ),
    (
        "users",
        "full_name",
        "VARCHAR(100)",
        "Tidak",
        "—",
        "—",
        "Nama lengkap pengguna yang ditampilkan pada panel profil sidebar.",
    ),
    (
        "users",
        "role",
        "ENUM('admin','operator','petani')",
        "Tidak",
        "—",
        "petani",
        "Peran pengguna yang menentukan hak akses modul (BR-07).",
    ),
    (
        "users",
        "is_active",
        "TINYINT(1)",
        "Tidak",
        "—",
        "1",
        "Status aktif akun; akun nonaktif tidak dapat melakukan login.",
    ),
    (
        "users",
        "created_at",
        "TIMESTAMP",
        "Tidak",
        "—",
        "CURRENT_TIMESTAMP",
        "Waktu pembuatan akun pengguna.",
    ),
    (
        "petani",
        "id_petani",
        "INT",
        "Tidak",
        "PK",
        "Auto Increment",
        "Identifier unik untuk setiap petani atau kelompok tani penyetor.",
    ),
    (
        "petani",
        "nama_petani",
        "VARCHAR(100)",
        "Tidak",
        "—",
        "—",
        "Nama lengkap petani atau kelompok tani penyetor komoditas.",
    ),
    (
        "petani",
        "lokasi_lahan",
        "VARCHAR(150)",
        "Tidak",
        "—",
        "—",
        "Domisili atau lokasi lahan tempat komoditas diproduksi.",
    ),
    (
        "petani",
        "komoditas_utama",
        "VARCHAR(100)",
        "Tidak",
        "—",
        "—",
        "Jenis komoditas utama yang dikembangkan oleh petani.",
    ),
    (
        "inventori_panen",
        "id_panen",
        "INT",
        "Tidak",
        "PK",
        "Auto Increment",
        "Identifier unik untuk setiap lot hasil panen yang masuk ke gudang.",
    ),
    (
        "inventori_panen",
        "id_petani",
        "INT",
        "Tidak",
        "FK",
        "—",
        "Kunci relasi ke tabel petani(id_petani) untuk mengidentifikasi penyetor.",
    ),
    (
        "inventori_panen",
        "jenis_komoditas",
        "VARCHAR(100)",
        "Tidak",
        "—",
        "—",
        "Nama komoditas hasil panen, misalnya Beras Organik atau Cabai Rawit.",
    ),
    (
        "inventori_panen",
        "jumlah_berat",
        "DECIMAL(10,2)",
        "Tidak",
        "—",
        "0.00",
        "Berat awal lot saat disetor. Sisa stok dihitung dari tabel distribusi "
        "(BR-02), bukan dari kolom ini.",
    ),
    (
        "inventori_panen",
        "tgl_panen",
        "DATE",
        "Tidak",
        "—",
        "—",
        "Tanggal saat komoditas disetorkan dan dicatat ke sistem.",
    ),
    (
        "distribusi",
        "id_distribusi",
        "INT",
        "Tidak",
        "PK",
        "Auto Increment",
        "Identifier unik untuk setiap transaksi alokasi pengiriman.",
    ),
    (
        "distribusi",
        "id_panen",
        "INT",
        "Tidak",
        "FK",
        "—",
        "Kunci relasi ke tabel inventori_panen(id_panen) yang menunjukkan lot asal.",
    ),
    (
        "distribusi",
        "tujuan_pengiriman",
        "VARCHAR(150)",
        "Tidak",
        "—",
        "—",
        "Nama toko, pembeli, pasar, atau distributor tujuan pengiriman.",
    ),
    (
        "distribusi",
        "jumlah_dikirim",
        "DECIMAL(10,2)",
        "Tidak",
        "—",
        "—",
        "Berat komoditas yang dialokasikan untuk dikirim keluar gudang.",
    ),
    (
        "distribusi",
        "status_pengiriman",
        "VARCHAR(50)",
        "Tidak",
        "—",
        "Diproses",
        "Status alur logistik; hanya menerima nilai Diproses, Dalam Pengiriman, atau Terkirim.",
    ),
]

VALIDASI = [
    ("username (Form Login)", "Wajib diisi.", "“Username dan password wajib diisi!”"),
    (
        "username, full_name, role (Form Registrasi)",
        "Username minimal 4 karakter dan hanya memuat huruf, angka, titik, "
        "atau garis bawah; nama lengkap wajib diisi; peran harus operator atau "
        "petani.",
        "“Username minimal 4 karakter!” / “Nama lengkap wajib diisi!” / "
        "“Peran 'admin' tidak dapat dipilih saat pendaftaran.”",
    ),
    (
        "password dan konfirmasi (Form Registrasi)",
        "Minimal 6 karakter dan harus sama dengan konfirmasi password.",
        "“Password minimal 6 karakter!” / “Konfirmasi password tidak sama dengan password!”",
    ),
    (
        "nama_petani, lokasi_lahan, komoditas_utama (Form Petani)",
        "Ketiga kolom wajib diisi; panjang teks dibatasi oleh panjang kolom pada "
        "basis data; penulisan dinormalkan (spasi rapat dan kapitalisasi judul); "
        "kombinasi ketiganya wajib unik terhadap data yang sudah tercatat (BR-11).",
        "“Nama, lokasi lahan, dan komoditas utama wajib diisi!” / “Gagal menyimpan! "
        "Petani dengan nama, lokasi lahan, dan komoditas yang sama sudah terdaftar "
        "(ID x - y) sesuai aturan BR-11.”",
    ),
    (
        "Tombol Ubah / Hapus pada Form Petani",
        "Baris pada tabel harus dipilih terlebih dahulu sebelum data dapat diubah atau dihapus.",
        "“Pilih data petani yang ingin diubah!” / “Pilih data petani yang ingin dihapus!”",
    ),
    (
        "Penghapusan data petani",
        "Ditolak apabila petani masih memiliki riwayat setoran panen (galat errno 1451).",
        "“Gagal menghapus! Petani masih memiliki riwayat setoran panen aktif di gudang (BR-01).”",
    ),
    (
        "id_petani, jenis_komoditas, jumlah_berat, tgl_panen (Form Inventori Panen)",
        "Penyetor dipilih dari kotak daftar dan wajib terdaftar; seluruh kolom "
        "wajib diisi; jumlah_berat harus dapat dikonversi menjadi angka dan "
        "lebih besar dari nol; tanggal berformat YYYY-MM-DD dan tidak berada di "
        "masa depan.",
        "“ID Petani tidak terdaftar di sistem!” / “Seluruh kolom setoran panen "
        "wajib diisi!” / “Jumlah berat harus berupa angka numerik!” / “Jumlah "
        "berat panen harus berupa angka positif!” / “Tanggal panen harus "
        "berformat YYYY-MM-DD!”",
    ),
    (
        "Pembaruan berat lot panen",
        "Berat baru minimal sebesar total berat yang sudah dialokasikan (BR-10).",
        "“Berat baru (… Kg) lebih kecil daripada total yang sudah dialokasikan "
        "(… Kg). Ubah alokasi distribusi terlebih dahulu.”",
    ),
    (
        "id_panen, tujuan_pengiriman, jumlah_dikirim (Form Distribusi)",
        "Seluruh kolom wajib diisi dan jumlah yang dikirim harus berupa angka positif.",
        "“ID Panen, Tujuan, dan Jumlah Dikirim wajib diisi!” / “Jumlah dikirim "
        "harus lebih dari 0!” / “Jumlah dikirim harus berupa angka!”",
    ),
    (
        "Validasi ketersediaan stok (Form Distribusi)",
        "Jumlah yang diminta tidak boleh melebihi sisa stok, dengan sisa stok = "
        "jumlah_berat pada lot dikurangi total jumlah_dikirim untuk lot yang sama "
        "(aturan bisnis BR-02).",
        "“Jumlah kirim melebihi sisa stok inventori yang tersedia di gudang! (Sisa: … Kg)”",
    ),
    (
        "status_pengiriman (Form Distribusi)",
        "Hanya menerima tiga nilai baku yang disediakan oleh kotak pilihan, "
        "yaitu Diproses, Dalam Pengiriman, dan Terkirim (aturan bisnis BR-05).",
        "“Status pengiriman tidak dikenali!”",
    ),
    (
        "Alokasi berstatus “Terkirim” (Form Distribusi)",
        "Alokasi yang sudah final tidak dapat diubah maupun dihapus (aturan bisnis BR-09).",
        "“Alokasi berstatus 'Terkirim' bersifat final dan tidak dapat diubah/dihapus (BR-09).”",
    ),
    (
        "Penghapusan lot panen",
        "Ditolak apabila lot masih terikat pada data alokasi distribusi (galat errno 1451).",
        "“Gagal menghapus! Lot panen masih terikat dengan data alokasi distribusi.”",
    ),
]

# ============================================================
# 6. ARSITEKTUR DAN PERANCANGAN
# ============================================================
TEKNOLOGI = [
    (
        "Front-end (View)",
        "Python 3.10+, CustomTkinter 5.2, tkinter(ttk.Treeview, messagebox, Canvas)",
        "Menyediakan antarmuka grafis desktop berupa jendela splash, login, "
        "registrasi, sidebar navigasi, form isian, dan tabel data dinamis.",
        "Memperoleh tampilan modern dengan usaha kecil karena tidak memerlukan "
        "browser atau peladen tambahan, dan sesuai untuk aplikasi internal "
        "serta Completely Offline.",
    ),
    (
        "Back-end (Logika)",
        "Python 3.10+",
        "Menjalankan logika bisnis, validasi masukan form, penerapan aturan "
        "bisnis, dan orkestrasi pemanggilan model.",
        "Bahasa yang mudah dibaca, mendukung pemrograman berorientasi objek, "
        "dan memiliki ekosistem pustaka yang luas.",
    ),
    (
        "Basis data",
        "MySQL 8.0 Community Server (Laragon)",
        "Menyimpan seluruh data relasional sistem pada empat tabel: users, "
        "petani, inventori_panen, dan distribusi.",
        "Menyediakan integritas relasi melalui kunci asing, transaksi, penguncian "
        "baris, dan mudah dijalankan secara lokal pada perkuliahan.",
    ),
    (
        "Pustaka koneksi",
        "mysql-connector-python 9.0",
        "Menyediakan koneksi ke server MySQL, kueri berparameter, dan eksekusi transaksi.",
        "Driver resmi MySQL untuk Python yang mendukung kueri berparameter "
        "sehingga aman terhadap injeksi SQL.",
    ),
    (
        "Perangkat pembantu",
        "Visual Studio Code; Draw.io; Laragon; HeidiSQL; Pillow",
        "Penyuntingan kode, pemodelan diagram, menjalankan layanan MySQL, "
        "pengelolaan basis data, dan pembangkitan aset visual logo.",
        "Perangkat gratis dan lazim dipakai pada perkuliahan sehingga artefak "
        "proyek dapat diperiksa mentor dengan mudah.",
    ),
    (
        "Kontinuitas Integrasi",
        "Git; GitHub Actions; pytest; pytest-cov; ruff; PyInstaller",
        "Pengujian otomatis, pemeriksaan kualitas kode, otomatisasi pipeline, "
        "dan pemaketan aplikasi menjadi berkas eksekusi mandiri.",
        "Menjamin setiap perubahan kode diuji secara otomatis sebelum rilis dan "
        "memudahkan distribusi aplikasi kepada pengguna akhir.",
    ),
]

DOKUMENTASI_MVC = [
    (
        "Model",
        "models/base_model.py (BaseModel)\nmodels/user_model.py (UserModel)\n"
        "models/petani_model.py (PetaniModel)\nmodels/panen_model.py (PanenModel)\n"
        "models/distribusi_model.py (DistribusiModel)\nconfig/database.py "
        "(DatabaseConnection)\nconfig/constants.py (konstanta aplikasi)",
        "Mengeksekusi kueri DML pada masing-masing tabel, membangkitkan hash "
        "SHA-256, menghitung sisa stok, menjalankan transaksi dengan "
        "penguncian baris, serta menangkap galat integritas errno 1451.",
        "Parameter data tabel (nama, lokasi, komoditas, id_panen, berat, tanggal, "
        "tujuan, jumlah, status, username, password, peran).",
        "Result set basis data, nilai boolean, pasangan nilai dan pesan galat, "
        "atau objek profil pengguna.",
        "Terhubung",
    ),
    (
        "Controller",
        "controllers/controller.py (AgriUnoController)\n"
        "controllers/auth_controller.py (AuthController, Session)\n"
        "controllers/user_controller.py (UserController)",
        "Mengatur logika bisnis per entitas, memvalidasi masukan form, "
        "menerapkan aturan bisnis BR-01 sampai BR-11, memverifikasi kredensial, "
        "menetapkan hak akses peran, dan mengorkestrasi pemanggilan model.",
        "Nilai mentah dari form antarmuka GUI dan parameter peran sesi.",
        "Pasangan (status, pesan) yang digunakan View untuk menampilkan kotak "
        "dialog, objek sesi pengguna, dan objek profil pengguna.",
        "Terhubung",
    ),
    (
        "View",
        "main.py (AgriUnoApp)\nviews/splash_view.py (SplashView)\n"
        "views/login_view.py (LoginView)\nviews/register_view.py (RegisterView)\n"
        "views/dashboard_view.py (DashboardView)\nviews/petani_view.py "
        "(PetaniView)\nviews/panen_view.py (PanenView)\n"
        "views/distribusi_view.py (DistribusiView)",
        "Menyajikan antarmuka desktop, menangani kejadian klik dan pemuatan "
        "ulang tabel, mengatur animasi splash, serta menampilkan pesan sukses "
        "atau galat.",
        "Interaksi klik tombol, pengisian kolom isian, pemilihan baris tabel, "
        "dan pilihan peran pada formulir registrasi.",
        "Tampilan jendela, form isian, tabel data, animasi pembuka, serta kotak dialog pesan.",
        "Terhubung",
    ),
]

STRUKTUR_FOLDER = """AgriUno/
├── .github/
│   └── workflows/
│       └── ci_pipeline.yml      # Pipeline CI GitHub Actions (Modul 8)
├── assets/
│   ├── anim/                    # 24 frame animasi logo untuk splash
│   ├── logo_agriuno.png         # Emblem AgriUno 512x512
│   ├── logo_agriuno_wordmark.png
│   ├── logo_agriuno_wordmark_small.png
│   └── logo_agriuno.ico         # Ikon untuk berkas .exe
├── config/
│   ├── constants.py             # Palet warna, peran pengguna, status baku
│   └── database.py              # DatabaseConnection (context manager)
├── controllers/
│   ├── auth_controller.py       # AuthController & Session (Modul 7)
│   ├── controller.py            # AgriUnoController
│   └── user_controller.py       # UserController (Modul 7)
├── models/
│   ├── base_model.py            # BaseModel (helper kueri & transaksi)
│   ├── user_model.py            # UserModel (hashing & autentikasi)
│   ├── petani_model.py          # PetaniModel
│   ├── panen_model.py           # PanenModel
│   └── distribusi_model.py      # DistribusiModel
├── views/
│   ├── splash_view.py           # SplashView (logo + animasi, Modul 8)
│   ├── login_view.py            # LoginView
│   ├── register_view.py         # RegisterView (registrasi, Modul 7)
│   ├── dashboard_view.py        # DashboardView
│   ├── petani_view.py           # PetaniView
│   ├── panen_view.py            # PanenView
│   └── distribusi_view.py       # DistribusiView
├── tests/
│   ├── conftest.py              # Fixture otomatis-skip bila MySQL mati
│   ├── test_auth.py             # Pengujian hashing, RBAC, registrasi
│   └── test_business_logic.py   # Pengujian aturan bisnis BR-01 s.d. BR-11
├── tools/
│   ├── generate_diagrams.py     # Pembangkit diagram .drawio + PNG
│   ├── generate_logo.py         # Pembangkit logo dan frame animasi
│   └── diagram_*.py             # Definisi diagram AgriUno
├── docs/diagrams/               # Hasil bangkit diagram (sumber laporan)
├── venv/                        # Lingkungan virtual Python
├── database.sql                 # Skema DDL + data contoh
├── main.py                      # AgriUnoApp (titik masuk)
├── pytest.ini                   # Konfigurasi penanda pengujian
├── requirements.txt             # Daftar dependensi
└── .gitignore"""

PENJELASAN_FOLDER = [
    "config/ — menyimpan konfigurasi penghubung basis data dan konstanta "
    "aplikasi. Berkas database.py memuat kelas DatabaseConnection dengan "
    "context manager cursor() yang menjamin setiap kursor dan koneksi "
    "ditutup serta transaksi di-commit atau di-rollback secara otomatis. "
    "Berkas constants.py memuat palet warna merek, daftar peran pengguna, "
    "dan nilai baku status pengiriman.",
    "controllers/ — menyimpan logika penghubung antara model data dan "
    "antarmuka. Berkas controller.py memuat kelas AgriUnoController yang "
    "memvalidasi masukan serta menerapkan aturan bisnis BR-01 sampai BR-11. "
    "Berkas auth_controller.py memuat AuthController dan Session yang "
    "menangani login, logout, serta penetapan hak akses berbasis peran. "
    "Berkas user_controller.py menangani registrasi dan pemeliharaan akun.",
    "models/ — menyimpan kelas model untuk masing-masing entitas. "
    "base_model.py menyediakan helper eksekusi kueri, penanganan galat, dan "
    "konversi tipe. user_model.py membangkitkan salt acak serta hash SHA-256 "
    "kata sandi. petani_model.py, panen_model.py, dan distribusi_model.py "
    "masing-masing menyediakan operasi get_all(), insert(), update(), dan "
    "delete() beserta perhitungan sisa stok dan transaksi alokasi.",
    "views/ — menyimpan seluruh kelas antarmuka, yaitu jendela splash dengan "
    "animasi logo, jendela login, jendela registrasi, dashboard, dan ketiga "
    "halaman pengelolaan data.",
    "main.py — berkas utama yang menjalankan aplikasi. Berkas ini membangun "
    "jendela utama, sidebar navigasi yang menyesuaikan hak akses peran, "
    "serta menumpuk seluruh halaman dan mengarahkan login berhasil ke "
    "fungsi run_main_app().",
    "tests/ — berisi skrip pengujian otomatis menggunakan pytest yang "
    "memverifikasi algoritma hashing, hak akses berbasis peran, validasi "
    "registrasi, dan seluruh aturan bisnis. Pengujian yang memerlukan MySQL "
    "ditandai dengan penanda db dan otomatis dilewati apabila server tidak "
    "tersedia.",
    "tools/ — berisi perkakas pembantu: generate_logo.py untuk membangkitkan "
    "logo dan frame animasi, serta generate_diagrams.py yang membangkitkan "
    "seluruh diagram .drawio beserta ekspor PNG-nya sehingga diagram pada "
    "laporan selalu selaras dengan kode sumber.",
    "assets/ dan docs/ — menyimpan aset visual aplikasi (logo dan frame "
    "animasi) serta hasil bangkit diagram yang dipakai pada laporan.",
    "database.sql, requirements.txt, pytest.ini, dan .gitignore — skema "
    "basis data beserta data contoh, daftar dependensi terkunci, konfigurasi "
    "pengujian, serta daftar berkas yang tidak ikut dilacak Git.",
]

PEDOMAN_ANTARMUKA = [
    (
        "Warna",
        "Tema hijau tua pertanian (#1b4332) untuk sidebar dan judul; latar "
        "belakang konten #f8f9fa; warna aksen biru (#1d4ed8) untuk kartu Total "
        "Petani, oranye (#d97706) untuk kartu Total Lot Panen, dan hijau "
        "(#2d6a4f) untuk kartu Total Distribusi serta progress bar. Tombol "
        "Simpan menggunakan hijau tua, tombol Ubah menggunakan oranye, dan "
        "tombol Hapus serta Keluar menggunakan merah (#dc2626).",
    ),
    (
        "Tipografi",
        "Menggunakan huruf Arial. Judul halaman 22 pt tebal, judul jendela login "
        "26 pt tebal, judul panel 14 pt tebal, label serta teks form 11–12 pt, "
        "dan angka pada kartu statistik 22 pt tebal.",
    ),
    (
        "Komponen",
        "Komponen kustom CustomTkinter berupa CTk, CTkFrame, CTkButton, "
        "CTkEntry, dan CTkOptionMenu untuk penyetor, lot panen, dan status "
        "pengiriman. Data ditampilkan pada tabel tkinter.ttk.Treeview dengan "
        'mode show="headings" dan seluruh baris menggunakan warna latar putih '
        "yang sama.",
    ),
    (
        "Responsivitas",
        "Tata letak menggunakan manajer grid dan pack yang adaptif. Jendela "
        "utama dikelurkan pada ukuran tetap 1150 × 680 piksel, jendela login "
        "berukuran 430 × 560 piksel, jendela registrasi 560 × 760 piksel, dan "
        "jendela splash 520 × 480 piksel tanpa bingkai.",
    ),
    (
        "Aksesibilitas",
        "Sidebar navigasi permanen di sisi kiri dengan label teks yang selalu "
        "terlihat, kontras warna teks yang tinggi terhadap latar, logo AgriUno "
        "pada bagian atas sidebar dan jendela login, serta kotak dialog "
        "messagebox untuk setiap umpan balik aksi.",
    ),
    (
        "Halaman pembuka",
        "Sebelum jendela login tampil, aplikasi menampilkan jendela splash "
        "tanpa bingkai yang memuat logo AgriUno muncul secara bertahap melalui "
        "24 frame, cincin orbit titik yang berputar, progress bar, dan pesan "
        "status yang bergantian. Animasi berhenti otomatis setelah 3 detik.",
    ),
]

# ============================================================
# 8-11. TAMBAHAN UAS
# ============================================================
MODUL_IMPLEMENTASI = [
    (
        "Modul 1",
        "Konsep Dasar RPL, DFD, dan UML",
        "Diagram Konteks, DFD Level 1, DFD Level 2 (proses 1.0 s.d. 4.0), Use "
        "Case Diagram, Sequence Diagram, Activity Diagram, dan Class Diagram.",
        "docs/diagrams/*.drawio dan *.png",
        "18 diagram dibangkitkan ulang oleh tools/generate_diagrams.py sehingga "
        "selalu selaras dengan kode sumber.",
    ),
    (
        "Modul 2",
        "Perancangan Arsitektur dan Implementasi",
        "Arsitektur three-tier MVC, ERD empat tabel, dan skema basis data "
        "lengkap dengan kunci asing serta pemeriksaan CHECK.",
        "docs/diagrams/06_Arsitektur_Sistem.png, docs/diagrams/05_Entity_"
        "Relationship_Diagram.png, database.sql",
        "Seluruh DDL dapat dijalankan pada MySQL 8.0 Laragon dengan satu "
        "perintah mysql -u root -p < database.sql.",
    ),
    (
        "Modul 3",
        "Setup Environment, Code Editor, dan VCS",
        "Lingkungan virtual Python, konfigurasi Git, berkas .gitignore, dan "
        "struktur proyek ter-modular.",
        ".gitignore, requirements.txt, pytest.ini",
        "Folder venv/, __pycache__/, build/, dan dist/ tidak ikut dilacak Git.",
    ),
    (
        "Modul 4",
        "Perancangan Model Python dan Integrasi MySQL",
        "BaseModel, PetaniModel, PanenModel, DistribusiModel, dan UserModel "
        "dengan parameterized query serta transaction management.",
        "models/*.py, config/database.py",
        "Context manager cursor() menjamin kursor dan koneksi selalu ditutup; "
        "commit dan rollback berjalan otomatis.",
    ),
    (
        "Modul 5",
        "Pengembangan Antarmuka Pengguna (View)",
        "Tujuh kelas view: splash, login, registrasi, dashboard, petani, panen, dan distribusi.",
        "views/*.py",
        "Semua elemen antarmuka dibangun dengan CustomTkinter dan tkinter.ttk.Treeview.",
    ),
    (
        "Modul 6",
        "Integrasi Controller dan Pengujian Kode",
        "AgriUnoController, UserController, serta 77 skrip pengujian pytest "
        "yang memverifikasi hashing, RBAC, registrasi, dan seluruh aturan "
        "bisnis.",
        "controllers/*.py, tests/*.py",
        "pytest -v → 56 passed; pengujian basis data otomatis dilewati bila MySQL tidak aktif.",
    ),
    (
        "Modul 7",
        "Autentikasi, Otorisasi, dan Registrasi Akun",
        "Tabel users, hashing SHA-256 bersalt, AuthController, Session, "
        "UserController, LoginView, dan RegisterView.",
        "models/user_model.py, controllers/auth_controller.py, "
        "controllers/user_controller.py, views/login_view.py, "
        "views/register_view.py",
        "Peran admin, operator, dan-petani; pendaftaran mandiri hanya "
        "memungkinkan peran operator dan petani (BR-07).",
    ),
    (
        "Modul 8",
        "Otomasi CI/CD, Logo, Animasi, dan Pemaketan",
        "Logo AgriUno, 24 frame animasi splash, pipeline GitHub Actions, "
        "requirements.txt, dan konfigurasi PyInstaller.",
        "assets/, .github/workflows/ci_pipeline.yml, tools/generate_logo.py",
        "Pipeline menjalankan pytest, pytest-cov, ruff check, dan "
        "ruff format --check pada setiap push ke branch main.",
    ),
]

PERBANDINGAN = [
    (
        "Autentikasi",
        "Kredensial admin dibandingkan langsung dengan nilai hardcode "
        "(admin/12345) di dalam views/login_view.py.",
        "Kredensial diverifikasi terhadap tabel users menggunakan hash SHA-256 "
        "dari (salt + password) dengan salt acak per pengguna dan "
        "hmac.compare_digest().",
        "Modul 7",
    ),
    (
        "Registrasi akun",
        "Tidak tersedia.",
        "Halaman Registrasi lengkap dengan validasi username minimal 4 karakter, "
        "password minimal 6 karakter, konfirmasi password, dan pemilihan peran "
        "operator atau petani.",
        "Modul 7 + ketentuan UAS butir 3",
    ),
    (
        "Otorisasi (RBAC)",
        "Tidak tersedia; satu operator untuk seluruh aktivitas.",
        "Tiga peran (admin, operator, petani) dengan pembatasan modul, "
        "penyembunyian tombol navigasi, dan penonaktifan kolom isian; "
        "penghapusan data dibatasi khusus untuk Administrator sehingga "
        "hak operator dan admin tidak lagi identik.",
        "Modul 7",
    ),
    (
        "Logo dan animasi",
        "Tidak tersedia.",
        "Logo AgriUno (emblem, wordmark, dan ikon .ico) serta jendela splash "
        "dengan 24 frame animasi, cincin orbit, progress bar, dan pesan status.",
        "Modul 8 + ketentuan UAS butir 8",
    ),
    (
        "Basis data",
        "Tiga tabel: petani, inventori_panen, distribusi.",
        "Empat tabel: users, petani, inventori_panen, distribusi, lengkap dengan "
        "salt, role, is_active, serta CHECK constraint.",
        "Modul 7 dan 8",
    ),
    (
        "Perhitungan stok",
        "Sisa stok dihitung pada controller dengan dua kueri terpisah pada dua koneksi berbeda.",
        "Sisa stok dihitung pada level basis data dengan LEFT JOIN, dan "
        "alokasi disimpan dalam satu transaksi dengan SELECT ... FOR UPDATE.",
        "Perbaikan cacat logika",
    ),
    (
        "Transaksi database",
        "commit() hanya dijalankan pada sebagian "
        "kueri; alokasi distribusi justru dibatalkan karena tidak pernah "
        "di-commit.",
        "Context manager cursor(commit=True) sebagai jalan masuk tunggal; "
        "rollback otomatis saat terjadi galat.",
        "Perbaikan cacat logika",
    ),
    (
        "Pemilihan data",
        "ID Petani dan ID Panen diketik manual oleh pengguna.",
        "Kotak daftar (CTkOptionMenu) yang diisi otomatis dari data "
        "sebelumnya, "
        "petani dan lot panen beserta sisa stoknya.",
        "Perbaikan cacat logika",
    ),
    (
        "Indikator dashboard",
        "Tiga progress bar dengan angka tetap (0,75 / 0,50 / 0,85).",
        "Tiga indikator yang dihitung dari data nyata, ditambah panel ringkasan "
        "berat (total setoran, total dialokasikan, sisa gudang).",
        "Perbaikan cacat logika",
    ),
    (
        "Status pengiriman",
        "Status 'Terkirim' masih dapat diubah atau dihapus.",
        "Alokasi berstatus 'Terkirim' bersifat final dan ditolak baik saat "
        "diubah maupun saat dihapus (BR-09).",
        "Perbaikan cacat logika",
    ),
    (
        "Pengujian",
        "Tidak ada pengujian otomatis.",
        "77 skrip pytest beserta pipeline GitHub Actions dengan laporan "
        "cakupan kode dan pemeriksaan kualitas dengan ruff.",
        "Modul 8",
    ),
    (
        "Pemaketan",
        "Tidak ada.",
        "Konfigurasi PyInstaller untuk menghasilkan berkas eksekusi mandiri "
        "AgriUno.exe beserta ikon logo.",
        "Modul 8",
    ),
    (
        "Validasi input",
        "Validasi hanya pada saat penambahan data.",
        "Validasi berlaku pada penambahan maupun pembaruan, termasuk format "
        "tanggal, keberadaan penyetor, dan batas berat minimum lot.",
        "Perbaikan cacat logika",
    ),
    (
        "Manajemen koneksi",
        "Koneksi dibuka dan ditutup manual pada setiap fungsi tanpa penjaminan pada kasus galat.",
        "Context manager dengan blok finally yang menjamin kursor dan koneksi selalu tertutup.",
        "Perbaikan cacat logika",
    ),
]

PENGUJIAN = [
    (
        "Pengujian hashing SHA-256",
        "Memastikan hash bersifat deterministik, berbeda untuk salt berbeda, "
        "tidak memuat teks password, dan hanya menerima password yang benar.",
        "tests/test_auth.py — TestHashing",
        "Lulus",
    ),
    (
        "Pengujian hak akses peran",
        "Memastikan admin, operator, dan petani memperoleh hak akses yang tepat, "
        "peran tidak dikenal jatuh ke hak akses paling kecil, dan penghapusan "
        "data ditolak bagi peran selain Administrator.",
        "tests/test_auth.py — TestOtorisasi; tests/test_business_logic.py",
        "Lulus",
    ),
    (
        "Pengujian registrasi",
        "Memastikan validasi username, password, konfirmasi, keunikan username, "
        "dan penolakan peran admin.",
        "tests/test_auth.py — TestValidasiRegistrasi",
        "Lulus",
    ),
    (
        "Pengujian aturan bisnis",
        "Memvalidasi BR-01 sampai BR-11: kolom wajib, format tanggal, "
        "keberadaan penyetor, batas berat lot, validasi stok, dan penguncian "
        "alokasi final.",
        "tests/test_business_logic.py",
        "Lulus",
    ),
    (
        "Pengujian integrasi basis data",
        "Memverifikasi login terhadap tabel users dengan kredensial yang benar dan salah.",
        "tests/test_auth.py — TestAutentikasiDatabase (penanda db)",
        "Lulus bila MySQL aktif, dilewati bila tidak",
    ),
    (
        "Pipeline Continuous Integration",
        "Menjalankan pytest beserta laporan cakupan kode, ruff check, dan "
        "ruff format --check pada setiap push ke branch main.",
        ".github/workflows/ci_pipeline.yml",
        "Berhasil (tanda centang hijau)",
    ),
]

DISTRIBUSI_LANGKAH = [
    (
        "1. Menyiapkan lingkungan",
        "Pasang Python 3.10 atau lebih baru, Laragon, dan Visual Studio Code. "
        "Jalankan Laragon lalu klik Start All agar layanan MySQL aktif.",
    ),
    (
        "2. Membuat lingkungan virtual",
        "Buka terminal VS Code pada folder proyek, lalu jalankan "
        "python -m venv env dan aktifkan dengan .\\env\\Scripts\\activate.",
    ),
    (
        "3. Memasang dependensi",
        "Jalankan pip install -r requirements.txt untuk memasang "
        "customtkinter, mysql-connector-python, Pillow, pytest, pytest-cov, "
        "ruff, dan pyinstaller.",
    ),
    (
        "4. Menyiapkan basis data",
        "Jalankan mysql -u root -p < database.sql untuk membentuk database "
        "agriuno beserta empat tabel, akun demo, dan data contoh.",
    ),
    (
        "5. Menjalankan aplikasi",
        "Jalankan python main.py. Jendela splash tampil selama 3 detik, "
        "kemudian jendela login. Gunakan akun admin/admin123, "
        "operator/operator123, atau petals/petani123.",
    ),
    (
        "6. Membuat akun baru",
        "Pada jendela login klik “Belum punya akun? Daftar di sini”, isi "
        "formulir, pilih peran Operator Gudang atau Petani, lalu tekan Daftar "
        "Sekarang.",
    ),
    (
        "7. Menjalankan pengujian",
        "Jalankan pytest -v untuk seluruh pengujian, atau pytest -v -m db "
        "untuk menguji integrasi basis data secara khusus.",
    ),
    (
        "8. Membangkitkan diagram",
        "Jalankan python tools/generate_diagrams.py --export-png untuk "
        "membangkitkan ulang seluruh diagram laporan dari kode sumber.",
    ),
    (
        "9. Memaketan aplikasi",
        "Jalankan pyinstaller --noconfirm --onefile --windowed --name "
        "AgriUno --icon assets/logo_agriuno.ico main.py, lalu jalankan "
        "berkas AgriUno.exe pada folder dist/.",
    ),
    (
        "10. Menerbitkan ke GitHub",
        'Jalankan git add ., git commit -m "feat: rilis UAS AgriUno", dan '
        "git push origin main. Pipeline GitHub Actions otomatis memverifikasi "
        "seluruh pengujian.",
    ),
]

KESIMPULAN = [
    (
        "Konsep Dasar RPL, DFD, dan UML",
        "Seluruh diagram AgriUno berhasil dibangkitkan ulang secara "
        "terprogram melalui tools/generate_diagrams.py sehingga isinya dijamin "
        "konsisten dengan kode sumber. Diagram Konteks, DFD Level 1, DFD Level 2, "
        "Use Case, Sequence, Activity, dan Class Diagram telah diperbarui untuk "
        "mencerminkan penambahan modul autentikasi, registrasi, dan animasi "
        "splash.",
    ),
    (
        "Perancangan Arsitektur dan Implementasi",
        "Arsitektur three-tier MVC tetap dipertahankan dan dilengkapi dengan "
        "lapisan autentikasi serta modul pengguna. Basis data kini terdiri atas "
        "empat tabel dengan kunci asing, pemeriksaan CHECK, dan indeks "
        "pendukung yang seluruhnya berjalan pada MySQL 8.0 melalui Laragon.",
    ),
    (
        "Setup Environment, Code Editor, dan VCS",
        "Penggunaan lingkungan virtual, VS Code, serta Git dan GitHub tetap "
        "berpijak pada praktik yang sama dan kini dilengkapi berkas "
        "requirements.txt, pytest.ini, serta pipeline GitHub Actions.",
    ),
    (
        "Perancangan Model Python dan Integrasi MySQL",
        "Lapisan model telah direfactor menjadi BaseModel bersama empat model "
        "entitas. Context manager koneksi memastikan tidak terjadi connection "
        "leak, transaksi berjalan secara atomik, dan seluruh kueri menggunakan "
        "parameter binding.",
    ),
    (
        "Pengembangan Antarmuka Pengguna (View)",
        "Tujuh kelas view telah dikembangkan, termasuk jendela splash dengan "
        "animasi logo 24 frame dan halaman registrasi akun baru. Seluruh "
        "pemilihan penyetor dan lot panen kini memakai kotak daftar yang terisi "
        "otomatis.",
    ),
    (
        "Integrasi Controller dan Pengujian Kode",
        "Controller telah dikembangkan pada tiga kelas dengan 77 skrip pengujian "
        "pytest yang memverifikasi hashing, otorisasi peran, validasi "
        "registrasi, dan seluruh aturan bisnis BR-01 sampai BR-11.",
    ),
    (
        "Autentikasi dan Otorisasi Pengguna",
        "Modul autentikasi telah diimplementasikan secara penuh menggunakan "
        "hash SHA-256 bersalt dengan perbandingan waktu-tetap. Fitur registrasi "
        "akun khusus pengguna ditambahkan beserta pembatasan peran berbasis "
        "Role-Based Access Control.",
    ),
    (
        "Otomasi CI/CD, Logo, Animasi, dan Pemaketan",
        "Logo AgriUno beserta animasi splash telah dirancang dan diprarender "
        "sehingga aplikasi tidak memerlukan pustaka gambar saat dijalankan. "
        "Pipeline GitHub Actions memverifikasi kualitas kode secara otomatis "
        "dan aplikasi dapat dipaketkan menjadi berkas eksekusi mandiri.",
    ),
]
