# ==========================================
# MODEL INVENTORI PANEN - AGRIUNO (Tabel: inventori_panen)
# Sesuai Kamus Data Laporan UTS Hal. 34-35
# ==========================================
from config.database import get_connection

class PanenModel:
    @staticmethod
    def tambah_panen(id_petani, jenis_komoditas, jumlah_berat, tgl_panen):
        conn = get_connection()
        if not conn: return False
        cursor = conn.cursor()
        query = "INSERT INTO inventori_panen (id_petani, jenis_komoditas, jumlah_berat, tgl_panen) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (id_petani, jenis_komoditas, jumlah_berat, tgl_panen))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    @staticmethod
    def get_all_panen():
        conn = get_connection()
        if not conn: return []
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT p.id_panen, pt.nama_petani, p.jenis_komoditas, p.jumlah_berat, p.tgl_panen 
            FROM inventori_panen p
            JOIN petani pt ON p.id_petani = pt.id_petani
            ORDER BY p.id_panen DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result