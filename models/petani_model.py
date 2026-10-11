# ==========================================
# MODEL PETANI - AGRIUNO (Tabel: petani)
# ==========================================
from config.database import get_connection

class PetaniModel:
    @staticmethod
    def tambah_petani(nama_petani, lokasi_lahan, komoditas_utama):
        conn = get_connection()
        if not conn: return False
        cursor = conn.cursor()
        query = "INSERT INTO petani (nama_petani, lokasi_lahan, komoditas_utama) VALUES (%s, %s, %s)"
        cursor.execute(query, (nama_petani, lokasi_lahan, komoditas_utama))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    @staticmethod
    def get_all_petani():
        conn = get_connection()
        if not conn: return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM petani ORDER BY id_petani DESC")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result