# ==========================================
# MODEL DISTRIBUSI - AGRIUNO (Tabel: distribusi)
# Sesuai Kamus Data Laporan UTS Hal. 35
# ==========================================
from config.database import get_connection

class DistribusiModel:
    @staticmethod
    def tambah_distribusi(id_panen, tujuan_pengiriman, jumlah_dikirim, status_pengiriman):
        conn = get_connection()
        if not conn: return False
        cursor = conn.cursor()
        query = "INSERT INTO distribusi (id_panen, tujuan_pengiriman, jumlah_dikirim, status_pengiriman) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (id_panen, tujuan_pengiriman, jumlah_dikirim, status_pengiriman))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    @staticmethod
    def get_all_distribusi():
        conn = get_connection()
        if not conn: return []
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT d.id_distribusi, p.jenis_komoditas, d.tujuan_pengiriman, d.jumlah_dikirim, d.status_pengiriman 
            FROM distribusi d
            JOIN inventori_panen p ON d.id_panen = p.id_panen
            ORDER BY d.id_distribusi DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result