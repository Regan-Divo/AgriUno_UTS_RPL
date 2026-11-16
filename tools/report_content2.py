"""
===========================================================
KONTEN TAMBAHAN LAPORAN UAS - AGRIUNO (RPL 2026)
===========================================================
Spesifikasi use case, katalog kelas, dan tabel wireframe yang
diselaraskan dengan implementasi UAS.
"""

# ============================================================
# SPESIFIKASI USE CASE
# ============================================================
SPESIFIKASI_UC = {
    "UC-01": [
        ("ID dan nama", "UC-01 Login ke Sistem AgriUno"),
        ("Aktor utama", "Admin Gudang (ACT-01), Pengguna Baru (ACT-04), Petani Terdaftar (ACT-05)"),
        (
            "Tujuan",
            "Memastikan hanya pengguna dengan"
            "akun valid dan berstatus"
            "aktif yang berhak membuka"
            "jendela utama AgriUno.",
        ),
        (
            "Prakondisi",
            "Aplikasi AgriUno dijalankan melalui"
            "berkas main.py; jendela"
            "splash telah selesai dan"
            "jendela login tampil.",
        ),
        (
            "Pemicu",
            "Pengguna menyelesaikan animasi"
            "splash dan memasukkan"
            "username serta password pada jendela login.",
        ),
        (
            "Alur utama",
            "1. Aplikasi menampilkan"
            "jendela splash selama 3"
            "detik yang memuat logo AgriUno"
            "dengan animasi, "
            "progress bar, dan pesan status.\n"
            "2. Setelah animasi selesai, jendela splash ditutup dan jendela LoginView tampil.\n"
            "3. Pengguna memasukkan username dan password lalu menekan tombol “Masuk Sistem”.\n"
            "4. Sistem memanggil fungsi proses_login() pada kelas LoginView.\n"
            "5. View meneruskan masukan ke AuthController.login(username, password).\n"
            "6. Controller memanggil UserModel.authenticate() yang menjalankan kueri berparameter "
            "SELECT ... FROM users WHERE username = %s.\n"
            "7. Model menghitung ulang hash = SHA-256(salt + password) dan membandingkannya dengan "
            "hmac.compare_digest() terhadap hash tersimpan.\n"
            "8. Bila cocok dan akun berstatus aktif, sesi pengguna diisi pada objek Session beserta "
            "perannya.\n"
            "9. Sistem menampilkan pesan"
            "berhasil, menutup jendela"
            "login, lalu membangun objek AgriUnoApp.\n"
            "10. Sidebar navigasi disusun sesuai hak akses peran pengguna.\n"
            "11. Sistem menampilkan halaman Dashboard melalui show_page('dashboard') dan memuat data "
            "rekapitulasi.",
        ),
        (
            "Alur alternatif",
            "6a. Bila username tidak ditemukan, sistem tetap melakukan proses hashing dengan salt "
            "palsu agar waktu respons seragam,"
            "lalu mengembalikan"
            "pesan “Username atau Password salah!”.\n"
            "7a. Bila password salah, sistem mengembalikan pesan yang sama.\n"
            "7b. Bila akun berstatus nonaktif (is_active = 0), sistem menolak login dengan pesan "
            "“Username atau Password salah!”.\n"
            "2a. Bila koneksi ke basis data gagal, sistem menampilkan pesan “Koneksi database gagal, "
            "login dibatalkan!” dan jendela login tetap terbuka.",
        ),
        (
            "Pascakondisi",
            "Sesi pengguna aktif dan jendela"
            "utama AgriUno terbuka pada"
            "halaman Dashboard dengan menu"
            "sidebar sesuai perannya.",
        ),
        ("Kebutuhan terkait", "FR-01, FR-07, FR-10, NFR-02, BR-06"),
    ],
    "UC-02": [
        ("ID dan nama", "UC-02 Melihat Dashboard Ringkasan"),
        ("Aktor utama", "Admin Gudang (ACT-01), Petani Terdaftar (ACT-05)"),
        (
            "Tujuan",
            "Memantau jumlah petani, lot"
            "panen, alokasi distribusi,"
            "ringkasan berat, dan indikator"
            "kinerja rantai pasok.",
        ),
        ("Prakondisi", "Pengguna telah berhasil login; jendela utama terbuka."),
        (
            "Pemicu",
            "Pengguna berada pada halaman Dashboard,"
            "baik saat pertama kali aplikasi"
            "dibuka maupun setelah berpindah"
            "halaman melalui sidebar.",
        ),
        (
            "Alur utama",
            "1. Sistem menampilkan halaman Dashboard Ringkasan Sistem Operasional.\n"
            "2. Sistem membangun tiga kartu"
            "statistik, yaitu Total"
            "Petani, Total Lot Panen,"
            "dan Total Distribusi.\n"
            "3. Sistem membangun panel ringkasan"
            "berat yang memuat Total"
            "Setoran, Total Dialokasikan,"
            "dan Sisa di Gudang.\n"
            "4. Fungsi load_data() dipanggil untuk membaca jumlah data pada ketiga tabel.\n"
            "5. Controller menghitung statistik melalui"
            "AgriUnoController.get_statistik()"
            "yang memanggil "
            "COUNT(*) pada tabel serta SUM() pada kolom berat.\n"
            "6. Tiga indikator kinerja dihitung dari data nyata, yaitu Alokasi Terdistribusi, "
            "Pengiriman Selesai, dan Petani Aktif.\n"
            "7. Sistem mengubah nilai pada seluruh kartu, progress bar, dan label persentase.",
        ),
        (
            "Alur alternatif",
            "4a. Jika jumlah data pada"
            "salah satu tabel bernilai"
            "nol, sistem tetap menampilkan nilai “0” "
            "pada kartu statistik terkait tanpa menampilkan galat.\n"
            "5a. Jika basis data tidak"
            "dapat dihubungi, sistem"
            "menampilkan nilai nol dan"
            "tidak menyebabkan "
            "aplikasi berhenti.",
        ),
        (
            "Pascakondisi",
            "Seluruh kartu statistik, ringkasan"
            "berat, dan indikator"
            "menampilkan angka terbaru dari basis data.",
        ),
        ("Kebutuhan terkait", "FR-02, NFR-01, NFR-04"),
    ],
    "UC-03": [
        ("ID dan nama", "UC-03 Mengelola Data Petani"),
        ("Aktor utama", "Admin Gudang (ACT-01); Petani (ACT-02) sebagai sumber data"),
        ("Tujuan", "Mendaftarkan dan mengelola profil identitas petani penyetor hasil panen."),
        ("Prakondisi", "Admin berada pada halaman Kelola Petani dan basis data terhubung."),
        (
            "Pemicu",
            "Petani baru mendaftarkan diri sebagai"
            "penyetor, atau terjadi"
            "perubahan data domisili maupun"
            "komoditas utama petani.",
        ),
        (
            "Alur utama",
            "1. Admin memilih menu “Kelola Petani” pada sidebar.\n"
            "2. Sistem menampilkan form isian Nama Petani, Lokasi Lahan, dan Komoditas Utama.\n"
            "3. Admin memasukkan ketiga data tersebut.\n"
            "4. Admin menekan tombol “Simpan”.\n"
            "5. Sistem memvalidasi kelengkapan"
            "kolom serta panjang"
            "teks melalui AgriUnoCont"
            "roller.tambah_petani(), lalu menormalkan penulisan teks "
            "(spasi rapat dan kapitalisasi judul) sesuai BR-11.\n"
            "6. Sistem memeriksa keunikan data: kombinasi nama, lokasi lahan, dan komoditas "
            "utama tidak boleh sama dengan data yang sudah tercatat (BR-11).\n"
            "7. Sistem menyimpan data melalui"
            "PetaniModel.insert() di dalam"
            "blok WITH DatabaseConnect"
            "ion.cursor(commit=True).\n"
            "8. Basis data mengeksekusi INSERT INTO petani (...) dan transaksi di-commit.\n"
            "9. Sistem menampilkan kotak dialog “Data petani berhasil disimpan!”.\n"
            "10. Sistem membersihkan form dan memuat ulang tabel data petani.",
        ),
        (
            "Alur alternatif",
            "5a. Jika salah satu kolom kosong, sistem membatalkan penyimpanan dan menampilkan pesan "
            "“Nama, lokasi lahan, dan komoditas utama wajib diisi!”.\n"
            "5b. Jika panjang teks melebihi kolom, sistem menampilkan pesan batas panjang.\n"
            "6a. Jika data identik sudah terdaftar, sistem menolak penyimpanan dan menampilkan "
            "pesan bahwa data petani yang sama sudah ada sesuai BR-11.\n"
            "8b. Jika Admin menekan “Ubah” atau “Hapus” tanpa memilih baris tabel, sistem menampilkan "
            "peringatan untuk memilih data terlebih dahulu.\n"
            "8c. Jika petani yang dihapus"
            "masih memiliki riwayat"
            "setoran panen, sistem menolak penghapusan "
            "dan menampilkan pesan bahwa relasi masih aktif.",
        ),
        (
            "Pascakondisi",
            "Data profil petani tersimpan"
            "di tabel petani dengan"
            "id_petani yang valid untuk"
            "transaksi setoran panen.",
        ),
        ("Kebutuhan terkait", "FR-03, FR-07, BR-01, BR-11, NFR-03"),
    ],
    "UC-04": [
        ("ID dan nama", "UC-04 Mencatat Setoran Panen"),
        ("Aktor utama", "Admin Gudang (ACT-01); Petani (ACT-02) sebagai sumber data"),
        (
            "Tujuan",
            "Mencatat jenis komoditasdan jumlah berat hasilpanen yang disetorkan petani ke gudang.",
        ),
        ("Prakondisi", "Data petani penyetor telah terdaftar pada tabel petani."),
        ("Pemicu", "Petani menyerahkan hasil panen ke gudang penampungan."),
        (
            "Alur utama",
            "1. Admin memilih menu “Inventori Panen” pada sidebar.\n"
            "2. Sistem mengisi kotak daftar"
            "“Petani Penyetor”"
            "secara otomatis dengan data"
            "dari tabel petani.\n"
            "3. Admin memilih penyetor pada kotak daftar tersebut; sistem otomatis mengisi "
            "Jenis Komoditas sesuai komoditas utama petani terpilih (BR-11).\n"
            "4. Admin mengisi Jumlah Berat (Kg) dan Tanggal; kolom tanggal terisi "
            "otomatis dengan tanggal hari ini.\n"
            "5. Admin menekan tombol “Simpan”.\n"
            "6. Sistem memvalidasi kelengkapan kolom, menormalkan penulisan jenis "
            "komoditas (BR-11), memastikan jumlah berat lebih besar dari nol, "
            "memastikan tanggal berformat YYYY-MM-DD dan tidak berada di masa depan.\n"
            "7. Sistem memastikan id_petani menunjuk data petani yang tercatat (BR-01).\n"
            "8. Sistem menyimpan data melalui PanenModel.insert() dan melakukan commit.\n"
            "9. Sistem menampilkan kotak dialog “Setoran panen berhasil dicatat!”.\n"
            "10. Sistem memuat ulang tabel lot panen sehingga rekapitulasi stok bertambah dan kolom "
            "Sisa Stok terisi.",
        ),
        (
            "Alur alternatif",
            "6a. Jika salah satu kolom kosong,"
            "sistem menampilkan"
            "pesan “Seluruh kolom setoran"
            "panen wajib diisi!”.\n"
            "6b. Jika nilai berat tidak dapat dikonversi menjadi angka, sistem menampilkan pesan "
            "“Jumlah berat harus berupa angka numerik!”.\n"
            "6c. Jika nilai berat nol"
            "atau negatif, sistem"
            "menampilkan pesan “Jumlah"
            "berat panen harus "
            "berupa angka positif!”.\n"
            "6d. Jika tanggal tidak valid,"
            "sistem menampilkan pesan"
            "“Tanggal panen harus berformat"
            "YYYY-MM-DD!”.\n"
            "7a. Jika penyetor tidak terdaftar,"
            "sistem menampilkan"
            "pesan “ID Petani tidak terdaftar"
            "di sistem!”.\n"
            "12a. Jika berat baru lebih kecil daripada total yang sudah dialokasikan, sistem menolak "
            "pembaruan dengan pesan yang menjelaskan batas minimum berat lot (BR-10).",
        ),
        (
            "Pascakondisi",
            "Catatan lot panen baru tersimpan"
            "di tabel inventori_panen"
            "dan rekapitulasi stok komoditas"
            "bertambah satu baris.",
        ),
        ("Kebutuhan terkait", "FR-04, FR-07, BR-01, BR-02, BR-10, BR-11"),
    ],
    "UC-05": [
        ("ID dan nama", "UC-05 Mengalokasikan Pengiriman"),
        ("Aktor utama", "Admin Gudang (ACT-01); Distributor (ACT-03) sebagai penerima"),
        (
            "Tujuan",
            "Mengalokasikan sejumlahstok panen dari gudanguntuk dikirimkan kepada penerima.",
        ),
        (
            "Prakondisi",
            "Terdapat lot panen padatabel inventori_panenyang masih memiliki sisa stok.",
        ),
        ("Pemicu", "Adanya permintaan pasokan komoditas dari pihak distributor."),
        (
            "Alur utama",
            "1. Admin memilih menu “Distribusi” pada sidebar.\n"
            "2. Sistem mengisi kotak daftar"
            "“Lot Panen” secara"
            "otomatis dengan data lot"
            "beserta sisa stoknya.\n"
            "3. Admin memilih lot, mengisi"
            "Tujuan Pengiriman dan Jumlah"
            "Dikirim (Kg), lalu menekan"
            "tombol “Simpan”.\n"
            "4. Sistem memvalidasi kelengkapan kolom dan memastikan jumlah lebih besar dari nol.\n"
            "5. Sistem memanggil Distribusi"
            "Model.create_with_stock_check()"
            "yang membuka satu transaksi basis data.\n"
            "6. Basis data mengunci baris lot dengan SELECT ... FOR UPDATE dan membaca jumlah_berat "
            "sekaligus SUM(jumlah_dikirim) pada tabel distribusi.\n"
            "7. Sistem menghitung sisa_stok = jumlah_berat − total_kirim.\n"
            "8. Jika jumlah yang diminta tidak melebihi sisa stok, sistem menyimpan data melalui "
            "INSERT INTO distribusi dengan status awal “Diproses” (BR-04) lalu melakukan commit.\n"
            "9. Sistem menampilkan kotak"
            "dialog “Alokasi pengiriman"
            "berhasil dibuat (Status"
            "Awal: Diproses)!”.\n"
            "10. Sistem memuat ulang tabel distribusi dan kotak daftar lot panen.",
        ),
        (
            "Alur alternatif",
            "4a. Jika salah satu kolom kosong, sistem menampilkan pesan “ID Panen, Tujuan, dan Jumlah "
            "Dikirim wajib diisi!”.\n"
            "6a. Jika ID Panen tidak terdaftar, sistem menolak dan menampilkan pesan “ID Panen tidak "
            "terdaftar di sistem!”.\n"
            "7a. Jika jumlah yang diminta melebihi sisa stok, sistem membatalkan alokasi, melakukan "
            "rollback, dan menampilkan pesan “Jumlah kirim melebihi sisa stok inventori yang tersedia "
            "di gudang!” beserta nilai sisa stok yang tersisa.\n"
            "8a. Jika alokasi yang diubah atau dihapus berstatus “Terkirim”, sistem menolak dengan "
            "pesan bahwa alokasi bersifat final (BR-09).",
        ),
        (
            "Pascakondisi",
            "Data alokasi tersimpan di"
            "tabel distribusi dengan"
            "status awal “Diproses”."
            "Nilai jumlah_berat pada"
            "tabel inventori_panen tidak"
            "berubah karena stok"
            "yang tersisa dihitung ulang"
            "dari data alokasi.",
        ),
        ("Kebutuhan terkait", "FR-05, FR-07, BR-02, BR-03, BR-04, BR-05, BR-09"),
    ],
    "UC-06": [
        ("ID dan nama", "UC-06 Keluar dari Aplikasi"),
        ("Aktor utama", "Admin Gudang (ACT-01), Petani Terdaftar (ACT-05)"),
        ("Tujuan", "Mengakhiri sesi aplikasi dengan menutup seluruh jendela AgriUno."),
        ("Prakondisi", "Pengguna telah berhasil login; jendela utama terbuka."),
        ("Pemicu", "Pengguna menekan tombol “Keluar” pada footer sidebar."),
        (
            "Alur utama",
            "1. Pengguna berada pada halaman mana pun di jendela utama AgriUno.\n"
            "2. Pengguna menekan tombol “Keluar” pada bagian bawah sidebar.\n"
            "3. Sistem memanggil AuthController.logout() yang mengosongkan objek Session.\n"
            "4. Sistem memanggil fungsi destroy() pada objek AgriUnoApp.\n"
            "5. Sistem menutup seluruh jendela aplikasi dan mengakhiri sesi program.",
        ),
        (
            "Alur alternatif",
            "2a. Jika pengguna tidak menekan"
            "tombol “Keluar”,"
            "jendela utama tetap terbuka dan pengguna "
            "dapat melanjutkan pekerjaan pada halaman yang sedang aktif.",
        ),
        (
            "Pascakondisi",
            "Seluruh jendela AgriUno ditutup,"
            "sesi pengguna dikosongkan,"
            "dan jendela login ditampilkan kembali.",
        ),
        ("Kebutuhan terkait", "FR-08, FR-01"),
    ],
    "UC-07": [
        ("ID dan nama", "UC-07 Memperbarui Status Pengiriman"),
        ("Aktor utama", "Admin Gudang (ACT-01); Distributor (ACT-03) sebagai penerima"),
        ("Tujuan", "Mengubah tahapan status pengiriman komoditas dari gudang menuju penerima."),
        ("Prakondisi", "Transaksi alokasi pengiriman sudah tercatat di tabel distribusi."),
        (
            "Pemicu",
            "Terjadi perubahan progres perjalanan"
            "pengiriman, misalnya"
            "pengangkut berangkat atau"
            "barang tiba di tujuan.",
        ),
        (
            "Alur utama",
            "1. Admin berada pada halaman Distribusi.\n"
            "2. Admin mengklik salah satu"
            "baris pada tabel distribusi"
            "sehingga data terpilih dan"
            "dimuat ke dalam form.\n"
            "3. Admin memilih status baru pada kotak pilihan Status Pengiriman.\n"
            "4. Admin menekan tombol “Ubah Status”.\n"
            "5. Sistem memanggil AgriUnoController.ubah_status_distribusi(id, status).\n"
            "6. Controller memastikan"
            "nilai status merupakan"
            "salah satu dari tiga nilai"
            "baku (BR-05) dan "
            "alokasi lama tidak berstatus “Terkirim” (BR-09).\n"
            "7. Sistem menyimpan pembaruan melalui DistribusiModel.update() dan melakukan commit.\n"
            "8. Sistem menampilkan kotak"
            "dialog “Status pengiriman"
            "berhasil diperbarui menjadi ...!”.\n"
            "9. Sistem membersihkan form dan memuat ulang tabel distribusi.",
        ),
        (
            "Alur alternatif",
            "3a. Jika Admin tidak memilih baris"
            "tabel, sistem menampilkan"
            "peringatan “Pilih data distribusi"
            "yang ingin diubah!”.\n"
            "5a. Jika status di luar daftar"
            "baku, sistem menolak"
            "dengan pesan “Status pengiriman"
            "tidak dikenali!”.\n"
            "6a. Jika alokasi berstatus"
            "“Terkirim”, sistem"
            "menolak dengan pesan bahwa"
            "alokasi bersifat "
            "final dan tidak dapat diubah (BR-09).",
        ),
        (
            "Pascakondisi",
            "Status pengiriman terbaru"
            "tersimpan pada tabel"
            "distribusi dan terlihat"
            "pada tabel antarmuka.",
        ),
        ("Kebutuhan terkait", "FR-06, FR-07, BR-05, BR-09"),
    ],
    "UC-08": [
        ("ID dan nama", "UC-08 Registrasi Akun Baru"),
        ("Aktor utama", "Pengguna Baru (ACT-04)"),
        ("Tujuan", "Mendaftarkan akun operator atau petani agar dapat mengakses AgriUno."),
        ("Prakondisi", "Jendela login tampil dan pengguna belum memiliki akun."),
        (
            "Pemicu",
            "Pengguna mengklik tautan “Belum punya akun?Daftar di sini” pada jendela login.",
        ),
        (
            "Alur utama",
            "1. Sistem membuka jendela RegisterView.\n"
            "2. Sistem menampilkan formulir"
            "Nama Lengkap, Username,"
            "Password, Konfirmasi Password, dan "
            "kotak pilihan Peran Pengguna yang hanya berisi Operator Gudang dan Petani.\n"
            "3. Pengguna mengisi seluruh kolom formulir.\n"
            "4. Pengguna menekan tombol “Daftar Sekarang”.\n"
            "5. View memanggil UserController.daftar()"
            "yang"
            "meneruskan masukan ke"
            "UserModel.register().\n"
            "6. Model memvalidasi nama lengkap, panjang username minimal 4 karakter dan keunikannya, "
            "password minimal 6 karakter, kesesuaian"
            "konfirmasi password,"
            "serta keabsahan peran (BR-06 s.d. BR-08).\n"
            "7. Model membangkitkan salt acak sepanjang 16 byte dan menghitung hash SHA-256 dari "
            "(salt + password).\n"
            "8. Basis data mengeksekusi INSERT"
            "INTO users (username,"
            "password, salt, full_name,"
            "role, is_active) "
            "dan melakukan commit.\n"
            "9. Sistem menampilkan pesan “Registrasi berhasil! Akun ... siap digunakan.” lalu "
            "mengosongkan formulir.",
        ),
        (
            "Alur alternatif",
            "6a. Jika kolom wajib kosong,"
            "sistem menampilkan"
            "pesan yang menunjuk kolom"
            "yang bermasalah.\n"
            "6b. Jika username sudah digunakan,"
            "sistem menampilkan"
            "pesan “Username ... sudah digunakan. "
            "Silakan gunakan username lain.”\n"
            "6c. Jika konfirmasi password"
            "tidak sama, sistem"
            "menampilkan pesan “Konfirmasi"
            "password tidak "
            "sama dengan password!”.\n"
            "6d. Jika peran yang dipilih"
            "adalah 'admin', sistem"
            "menolak dengan pesan bahwa"
            "akun Administrator "
            "hanya dapat dibuat oleh pengelola basis data (BR-07).\n"
            "9a. Pengguna dapat menekan"
            "tautan “Sudah punya"
            "akun? Kembali ke Login”"
            "untuk menutup jendela "
            "registrasi dan kembali ke halaman login.",
        ),
        (
            "Pascakondisi",
            "Akun baru tersimpan pada tabel"
            "users dengan hash SHA-256"
            "bersalt dan dapat langsung"
            "digunakan untuk login.",
        ),
        ("Kebutuhan terkait", "FR-09, FR-07, BR-06, BR-07, BR-08, NFR-02"),
    ],
    "UC-09": [
        ("ID dan nama", "UC-09 Mengubah Kata Sandi Pengguna"),
        ("Aktor utama", "Admin Gudang (ACT-01), Petani Terdaftar (ACT-05)"),
        ("Tujuan", "Mengubah kata sandi sendiri dengan verifikasi kata sandi lama."),
        ("Prakondisi", "Pengguna telah berhasil login dengan kredensial kata sandi lamanya."),
        ("Pemicu", "Pengguna memilih menu untuk mengubah kata sandi pada panel profil pengguna."),
        (
            "Alur utama",
            "1. Pengguna memasukkan kata"
            "sandi lama, kata sandi"
            "baru, dan konfirmasi kata sandi baru.\n"
            "2. Sistem memanggil AuthC"
            "ontroller.ubah_password()"
            "yang"
            "meneruskan masukan ke User"
            "Model.change_password().\n"
            "3. Model memvalidasi panjang"
            "kata sandi baru minimal"
            "6 karakter dan kesesuaian konfirmasi.\n"
            "4. Model membaca salt dan hash lama dari tabel users lalu memverifikasi kata sandi lama "
            "menggunakan hmac.compare_digest().\n"
            "5. Jika kata sandi lama sesuai, model menghitung hash baru dengan salt yang sama dan "
            "menyimpankannya melalui UPDATE users SET password = %s.\n"
            "6. Sistem menampilkan pesan “Password berhasil diubah!”.\n"
            "7. Pengguna disarankan menggunakan kata sandi baru pada login berikutnya.",
        ),
        (
            "Alur alternatif",
            "3a. Jika kata sandi baru terlalu"
            "pendek, sistem menampilkan"
            "pesan “Password baru minimal"
            "6 karakter!”.\n"
            "3b. Jika konfirmasi tidak"
            "sama, sistem menampilkan"
            "pesan “Konfirmasi password"
            "baru tidak sama!”.\n"
            "4a. Jika kata sandi lama tidak"
            "sesuai, sistem menampilkan"
            "pesan “Password lama tidak sesuai!” "
            "dan tidak melakukan perubahan.",
        ),
        (
            "Pascakondisi",
            "Kata sandi pengguna tersimpan sebagai hashSHA-256 yang baru dengan salt yang sama.",
        ),
        ("Kebutuhan terkait", "FR-11, FR-07, BR-08, NFR-02"),
    ],
}

# ============================================================
# KATALOG KELAS
# ============================================================
KATALOG_KELAS = [
    (
        "AgriUnoApp\n(main.py)",
        "Membangun jendela utama, sidebar"
        "navigasi yang menyesuaikan"
        "hak akses peran, dan menumpuk"
        "seluruh halaman aplikasi.",
        "user : dict\npages : dict[str,"
        "CTkFrame]\nnav_buttons"
        ": dict[str, CTkButton]\ncontent : CTkFrame",
        "+ __init__(user)\n+ show_page(page_name)\n+"
        "_build_sidebar()\n+"
        "_build_content()\n+ _tandai_menu_aktif()\n+"
        "keluar()",
        "Komposisi (1..*) terhadap empat kelas View",
    ),
    (
        "SplashView\n(views/splash_view.py)",
        "Menampilkan logo AgriUno beserta animasi pembuka sebelum jendela login tampil.",
        "on_finish : Callable\nframes"
        ": list[PhotoImage]\nprogress"
        ": CTkProgressBar\nstatus_label : CTkLabel",
        "+ __init__(on_finish)\n+ _tick()\n+ _draw_orbit()\n+ _update_status()\n+ _finish()\n+ skip()",
        "Dibuat oleh main.py sebelum LoginView; memanggil callback on_finish",
    ),
    (
        "LoginView\n(views/login_view.py)",
        "Menyediakan form login dengan verifikasi kredensial terhadap tabel users.",
        "on_login_success : Callable\ne_user : CTkEntry\ne_pass : CTkEntry\nlbl_error : CTkLabel",
        "+ __init__(on_login_success)\n+ proses_login()\n+ _place_logo()",
        "Memakai AuthController; membuat RegisterView",
    ),
    (
        "RegisterView\n(views/register_view.py)",
        "Menyediakan formulir pendaftaran akun baru bagi pengguna yang belum memiliki akun.",
        "on_success : Callable\ne_nama"
        ": CTkEntry\ne_user"
        ": CTkEntry\ne_pass"
        ": CTkEntry\ne_pass2 : CTkEntry\nopt_peran"
        ": CTkOptionMenu",
        "+ __init__(on_success)\n+ proses_registrasi()\n+ _peran_terpilih()\n+ _peran_diganti()",
        "Memakai UserController",
    ),
    (
        "DashboardView\n(views/dashboard_view.py)",
        "Menyajikan ringkasan jumlah"
        "data, ringkasan berat, dan"
        "indikator kinerja yang dihitung"
        "dari data nyata.",
        "controller : AgriUnoController\nlbl_p"
        ": CTkLabel\nlbl_h"
        ": CTkLabel\nlbl_d : CTkLabel\nindicators"
        ": dict",
        "+ load_data()\n+ create_stat_card()\n+ create_progress_indicator()\n+ _weight_item()",
        "Memakai AgriUnoController",
    ),
    (
        "PetaniView\n(views/petani_view.py)",
        "Menyediakan form dan tabel untuk mengelola data petani penyetor.",
        "controller : AgriUnoController\nselected_id\ntree : ttk.Treeview\nbisa_ubah : bool",
        "+ load_table()\n+ simpan()\n+ ubah()\n+ hapus()\n+ on_select()\n+ _terapkan_otorisasi()",
        "Memakai AgriUnoController",
    ),
    (
        "PanenView\n(views/panen_view.py)",
        "Menyediakan form dan tabel untuk mencatat lot setoran panen beserta sisa stoknya.",
        "controller : AgriUnoController\nselected_id\nopt_petani : CTkOptionMenu\n_petani_map : dict",
        "+ load_table()\n+ load_petani()\n+ simpan()\n+ ubah()\n+ hapus()\n+ on_select()",
        "Memakai AgriUnoController",
    ),
    (
        "DistribusiView\n(views/distribusi_view.py)",
        "Menyediakan form dan tabel untuk mengelola alokasi serta status pengiriman.",
        "controller : AgriUnoControl"
        "ler\nselected_id\nopt_panen"
        ": CTkOptionMenu\nopt_status"
        ": CTkOptionMenu\n_panen_map : dict",
        "+ load_table()\n+ load_panen()\n+ simpan()\n+ ubah()\n+ hapus()\n+ on_select()",
        "Memakai AgriUnoController",
    ),
    (
        "AgriUnoController\n(controllers/controller.py)",
        "Menjembatani antarmuka dengan basis"
        "data; memvalidasi masukan"
        "dan menerapkan aturan bisnis"
        "BR-01 sampai BR-11.",
        "Kelas utilitas; seluruh metode statis",
        "+ get_petani() / tambah_petani() / update_petani() / hapus_petani()\n"
        "+ get_panen() / tambah_panen() / update_panen() / hapus_panen()\n"
        "+ get_distribusi() / tambah_distribusi()\n"
        "+ update_distribusi() / ubah_status_distribusi() / hapus_distribusi()\n"
        "+ get_statistik()",
        "Memakai ketiga kelas model dan DatabaseConnection",
    ),
    (
        "AuthController\n(controllers/auth_controller.py)",
        "Menangani proses login, logout, sesi pengguna, dan penetapan hak akses berbasis peran.",
        "+ session : Session",
        "+ login(username, password)\n+ logout()\n+ register(...)\n+ current_user()\n+ boleh(aksi)\n"
        "+ daftar_akun()\n+ set_akun_aktif()\n+ hapus_akun()\n+ ubah_password()",
        "Memakai UserModel; memiliki komposisi Session",
    ),
    (
        "UserController\n(controllers/user_controller.py)",
        "Menyediakan antarmuka logika untuk registrasi dan pemeliharaan akun pengguna.",
        "Kelas utilitas; seluruh metode statis",
        "+ daftar(...)\n+ daftar_akun()\n+ ubah_profil()\n+ ubah_password()\n+ aktifkan()\n"
        "+ nonaktifkan()\n+ hapus()\n+ boleh_kelola_pengguna()",
        "Memakai UserModel dan AuthController",
    ),
    (
        "Session\n(controllers/auth_controller.py)",
        "Menyimpan state sesi pengguna yang sedang login beserta perannya.",
        "user : dict\nrole : str\nusername : str\nfull_name : str\nid_user : int",
        "+ aktif()\n+ set_user(user)\n+"
        "capabilities()\n+"
        "boleh(aksi)\n+"
        "label_peran\n+ ringkasan()\n+ reset()",
        "Komposisi (1) terhadap AuthController",
    ),
    (
        "BaseModel\n(models/base_model.py)",
        "Menyediakan helper eksekusi kueri,"
        "penanganan galat errno,"
        "dan konversi tipe yang"
        "dipakai seluruh model.",
        "Kelas utilitas; seluruh metode statis",
        "+ _execute_write(sql, params)\n+ _fetch_all(sql, params)\n+ _fetch_one(sql, params)\n"
        "+ to_decimal(value)\n+ format_berat(value)\n+ _is_foreign_key_violation(err)",
        "Dipakai seluruh kelas model",
    ),
    (
        "UserModel\n(models/user_model.py)",
        "Menjalankan hashing SHA-256"
        "bersalt, autentikasi,"
        "registrasi, dan pemeliharaan akun pengguna.",
        "Kelas utilitas; seluruh metode statis",
        "+ hash_password(password, salt)\n+"
        "generate_salt()\n+"
        "verify_password(password,"
        "salt, stored_hash)\n"
        "+ authenticate(username, password)\n+ register(...)\n+ get_all() / get_by_username()\n"
        "+ username_exists()\n+ update_profile() / change_password() / set_active() / delete()",
        "Mewariskan BaseModel; memakai DatabaseConnection",
    ),
    (
        "PetaniModel\n(models/petani_model.py)",
        "Menjalankan operasi CRUD pada tabel petani serta menangani galat errno 1451.",
        "Kelas utilitas; seluruh metode statis",
        "+ get_all() / get_by_id() / exists()\n+ count() / count_petani_aktif()\n"
        "+ insert() / update() / delete()",
        "Mewariskan BaseModel; memakai DatabaseConnection",
    ),
    (
        "PanenModel\n(models/panen_model.py)",
        "Menjalankan operasi CRUD pada tabel inventori_panen serta menghitung sisa stok tiap lot.",
        "Kelas utilitas; seluruh metode statis",
        "+ get_all() / get_by_id()\n+ get_sisa_stok(id_panen)\n+ get_total_terkirim(id_panen)\n"
        "+ count() / total_berat()\n+ insert() / update() / delete()",
        "Mewariskan BaseModel; memakai DatabaseConnection",
    ),
    (
        "DistribusiModel\n(models/distribusi_model.py)",
        "Menjalankan operasi CRUD pada tabel distribusi dengan transaksi atomik dan penguncian baris.",
        "Kelas utilitas; seluruh metode statis",
        "+ get_all() / get_by_id()\n+ create_with_stock_check()\n+ update_with_stock_check()\n"
        "+ count() / count_by_status() / total_dikirim()\n+ insert() / update() / delete()\n"
        "+ valid_status() / is_locked()",
        "Mewariskan BaseModel; memakai DatabaseConnection",
    ),
    (
        "DatabaseConnection\n(config/database.py)",
        "Menyediakan pembuatan koneksi"
        "tunggal ke server MySQL"
        "lokal beserta context manager"
        "kursor dan transaksi.",
        "DB_HOST / DB_PORT / DB_USER\nDB_PASSWORD / DB_NAME",
        "+ connect(database) : Connection\n+ cursor(dictionary, commit)\n+ ping() : bool",
        "Dipakai seluruh kelas model",
    ),
]

# ============================================================
# TABEL WIREFRAME 7.2 (perbaruan)
# ============================================================
WIREFRAME_LOGIN = [
    ("Elemen", "Fungsi", "Kebutuhan Terkait"),
    (
        "Logo AgriUno",
        "Emblem AgriUno menampilkan monogram"
        "huruf A dari batang"
        "tanaman dan helai daun padi"
        "di bagian atas formulir.",
        "FR-01, FR-10",
    ),
    (
        "Judul dan Subjudul",
        "Menampilkan identitas produk “AgriUno”"
        "dan keterangan “Sistem"
        "Informasi Pengelolaan Hasil"
        "Panen Pertanian Lokal”.",
        "FR-01",
    ),
    (
        "Kolom Username dan Password",
        "Menyediakan tempat pengguna memasukkan"
        "kredensial; kolom"
        "password disembunyikan dengan"
        "karakter bintang.",
        "FR-01",
    ),
    (
        "Pesan Galat Inline",
        "Menampilkan “Username atau Password"
        "salah!” di bawah form"
        "apabila verifikasi gagal,"
        "tanpa menutup jendela.",
        "FR-01, FR-07, NFR-03",
    ),
    (
        "Tombol “Masuk Sistem”",
        "Mengeksekusi validasi kredensial"
        "terhadap tabel"
        "users sebelum membuka jendela"
        "utama dashboard.",
        "FR-01, FR-07",
    ),
    (
        "Tautan “Daftar di sini”",
        "Membuka jendela registrasi akun baru bagipengguna yang belum memiliki akun.",
        "FR-09",
    ),
]

WIREFRAME_DASHBOARD = [
    ("Elemen", "Fungsi", "Kebutuhan Terkait"),
    (
        "Sidebar Navigasi",
        "Panel menu permanen di sisi"
        "kiri untuk berpindah"
        "halaman secara dinamis antara Dashboard,"
        "Kelola Petani, Inventori"
        "Panen, dan Distribusi."
        "Isi menu menyesuaikan peran pengguna.",
        "FR-02, FR-08, NFR-04",
    ),
    (
        "Tiga Kartu Statistik",
        "Menampilkan jumlah total petani,"
        "lot panen, dan alokasi"
        "distribusi yang diambil langsung"
        "dari basis data.",
        "FR-02",
    ),
    (
        "Tiga Indikator Kinerja",
        "Menampilkan progress bar"
        "Alokasi Terdistribusi,"
        "Pengiriman Selesai, dan"
        "Petani Aktif yang dihitung dari data"
        "nyata beserta nilai persentasenya.",
        "FR-02, NFR-01",
    ),
    (
        "Panel Ringkasan Berat",
        "Menampilkan Total Setoran,Total Dialokasikan,dan Sisa di Gudang dalam satuan Kg.",
        "FR-02, BR-02",
    ),
    (
        "Panel “Tentang Sistem AgriUno”",
        "Menampilkan deskripsi singkat"
        "fungsi sistem, penyebutan"
        "hash SHA-256, dan penerapan"
        "Role-Based Access Control.",
        "FR-02",
    ),
    (
        "Panel Profil Pengguna",
        "Menampilkan nama lengkap pengguna aktifdan perannya pada bagian bawah sidebar.",
        "FR-01, FR-02",
    ),
    (
        "Tombol “Keluar”",
        "Mengakhiri sesi, menutup seluruhjendela aplikasi,dan menampilkan kembali jendela login.",
        "FR-08",
    ),
]

WIREFRAME_PETANI = [
    ("Elemen", "Fungsi", "Kebutuhan Terkait"),
    (
        "Kolom Isian Form",
        "Menyediakan tempat Admin Gudang"
        "memasukkan Nama Petani,"
        "Lokasi Lahan, dan Komoditas"
        "Utama secara terstruktur.",
        "FR-03, BR-01",
    ),
    (
        "Tombol Simpan",
        "Menjalankan AgriUnoController.tambah_petani() untuk menambahkan data baru.",
        "FR-03, FR-07",
    ),
    (
        "Tombol Ubah",
        "Menjalankan pembaruan data petani pada baris tabel yang sedang dipilih.",
        "FR-03, FR-07",
    ),
    (
        "Tombol Hapus",
        "Menghapus data terpilih dengandialog konfirmasidan penanganan galat integritas relasi.",
        "FR-03, FR-07, NFR-03",
    ),
    (
        "Tabel Data Petani",
        "Menampilkan kolom ID Petani,Nama Petani, LokasiLahan, dan Komoditas Utama secara dinamis.",
        "FR-03, NFR-01",
    ),
]
