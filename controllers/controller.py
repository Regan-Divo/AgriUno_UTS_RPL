from models.database import DatabaseManager

class AgriUnoController:
    """
    Lapisan Pengontrol (Controller) Utama Sistem AgriUno.
    Mengatur validasi masukan form dan menjembatani View dengan Model.
    """

    # ==================== KELOLA PETANI ====================
    @staticmethod
    def ambil_semua_petani():
        """Mengambil seluruh data petani terdaftar."""
        query = "SELECT id_petani, nama_petani, lokasi_lahan, komoditas_utama FROM petani ORDER BY id_petani DESC"
        return DatabaseManager.fetch_records(query)

    @staticmethod
    def simpan_petani(nama, lokasi, komoditas):
        """Menambahkan data petani baru dengan validasi integritas."""
        if not nama or not lokasi or not komoditas:
            return False, "Seluruh kolom pada form petani wajib diisi secara lengkap!"
        
        if len(nama.strip()) > 100 or len(lokasi.strip()) > 150:
            return False, "Panjang karakter melebihi batas maksimal yang diizinkan."

        query = "INSERT INTO petani (nama_petani, lokasi_lahan, komoditas_utama) VALUES (%s, %s, %s)"
        return DatabaseManager.execute_non_query(query, (nama.strip(), lokasi.strip(), komoditas.strip()))

    # ==================== KELOLA INVENTORI PANEN ====================
    @staticmethod
    def ambil_semua_inventori():
        """Mengambil rekapitulasi inventori panen dengan relasi JOIN ke tabel petani."""
        query = """
            SELECT p.id_panen, pt.nama_petani, p.jenis_komoditas, p.jumlah_berat, p.tgl_panen 
            FROM inventori_panen p
            JOIN petani pt ON p.id_petani = pt.id_petani
            ORDER BY p.id_panen DESC
        """
        return DatabaseManager.fetch_records(query)

    @staticmethod
    def catat_setoran_panen(id_petani, jenis, berat, tanggal):
        """Mencatat setoran panen masuk dengan validasi aturan bisnis BR-01 & BR-03."""
        if not id_petani or not jenis or not berat or not tanggal:
            return False, "Semua parameter setoran panen wajib diisi!"

        try:
            id_p = int(id_petani)
            berat_val = float(berat)
            if berat_val <= 0:
                return False, "Jumlah berat panen harus bernilai positif (> 0)!"
        except ValueError:
            return False, "ID Petani dan Jumlah Berat harus berupa angka yang valid!"

        query = "INSERT INTO inventori_panen (id_petani, jenis_komoditas, jumlah_berat, tgl_panen) VALUES (%s, %s, %s, %s)"
        return DatabaseManager.execute_non_query(query, (id_p, jenis.strip(), berat_val, tanggal.strip()))

    # ==================== KELOLA DISTRIBUSI LOGISTIK ====================
    @staticmethod
    def ambil_semua_distribusi():
        """Mengambil data riwayat pengiriman logistik keluar."""
        query = """
            SELECT d.id_distribusi, d.id_panen, d.tujuan_pengiriman, d.jumlah_dikirim, d.status_pengiriman
            FROM distribusi d
            ORDER BY d.id_distribusi DESC
        """
        return DatabaseManager.fetch_records(query)

    @staticmethod
    def alokasikan_pengiriman(id_panen, tujuan, jumlah, status):
        """Mengalokasikan pengiriman dengan pengecekan stok gudang (BR-02, BR-04)."""
        if not id_panen or not tujuan or not jumlah or not status:
            return False, "Form alokasi distribusi tidak boleh kosong!"

        try:
            id_p = int(id_panen)
            jml_val = float(jumlah)
            if jml_val <= 0:
                return False, "Jumlah alokasi kirim harus bernilai positif!"
        except ValueError:
            return False, "Format angka pada ID Panen atau Jumlah Kirim tidak valid!"

        # Validasi ketersediaan stok pada inventori
        cek_stok_query = "SELECT jumlah_berat FROM inventori_panen WHERE id_panen = %s"
        stok_result = DatabaseManager.fetch_records(cek_stok_query, (id_p,))
        
        if not stok_result:
            return False, "Lot ID Panen asal tidak ditemukan di dalam sistem gudang!"
        
        stok_tersedia = float(stok_result[0]['jumlah_berat'])
        if jml_val > stok_tersedia:
            return False, f"Stok gudang tidak mencukupi! Sisa stok tersedia: {stok_tersedia} Kg."

        # Eksekusi transaksi alokasi distribusi dan pemotongan stok secara atomik
        query_distribusi = "INSERT INTO distribusi (id_panen, tujuan_pengiriman, jumlah_dikirim, status_pengiriman) VALUES (%s, %s, %s, %s)"
        query_update_stok = "UPDATE inventori_panen SET jumlah_berat = jumlah_berat - %s WHERE id_panen = %s"

        conn = DatabaseManager.get_connection()
        if not conn:
            return False, "Koneksi basis data gagal."

        cursor = conn.cursor()
        try:
            conn.start_transaction()
            # 1. Catat distribusi
            cursor.execute(query_distribusi, (id_p, tujuan.strip(), jml_val, status.strip()))
            # 2. Kurangi stok inventori otomatis (BR-03)
            cursor.execute(query_update_stok, (jml_val, id_p))
            conn.commit()
            return True, "Alokasi pengiriman berhasil dan stok gudang otomatis terpotong."
        except Exception as e:
            conn.rollback()
            return False, f"Gagal memproses alokasi distribusi: {e}"
        finally:
            cursor.close()
            conn.close()