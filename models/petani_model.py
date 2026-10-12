from config.database import DatabaseConnection
import mysql.connector

class PetaniModel:
    @staticmethod
    def get_all():
        conn = DatabaseConnection.connect()
        if not conn: return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM petani")
        result = cursor.fetchall()
        cursor.close(); conn.close()
        return result

    @staticmethod
    def insert(nama, lokasi, komoditas):
        conn = DatabaseConnection.connect()
        if not conn: return False
        cursor = conn.cursor()
        cursor.execute("INSERT INTO petani (nama_petani, lokasi_lahan, komoditas_utama) VALUES (%s, %s, %s)", (nama, lokasi, komoditas))
        conn.commit()
        cursor.close(); conn.close()
        return True

    @staticmethod
    def update(id_petani, nama, lokasi, komoditas):
        conn = DatabaseConnection.connect()
        if not conn: return False
        cursor = conn.cursor()
        cursor.execute("UPDATE petani SET nama_petani=%s, lokasi_lahan=%s, komoditas_utama=%s WHERE id_petani=%s", (nama, lokasi, komoditas, id_petani))
        conn.commit()
        cursor.close(); conn.close()
        return True

    @staticmethod
    def delete(id_petani):
        conn = DatabaseConnection.connect()
        if not conn: 
            return False, "Koneksi database gagal!"
        
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM petani WHERE id_petani = %s", (id_petani,))
            conn.commit()
            cursor.close(); conn.close()
            return True, "Data petani berhasil dihapus!"
            
        except mysql.connector.Error as err:
            if conn and conn.is_connected():
                conn.close()
            if err.errno == 1451:
                return False, "Gagal menghapus! Petani masih memiliki riwayat setoran panen aktif di gudang (BR-01)."
            else:
                return False, f"Terjadi kesalahan database: {err.msg}"
        except Exception as e:
            if conn and conn.is_connected():
                conn.close()
            return False, f"Terjadi kesalahan sistem: {str(e)}"