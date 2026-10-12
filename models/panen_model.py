from config.database import DatabaseConnection

class PanenModel:
    @staticmethod
    def get_all():
        conn = DatabaseConnection.connect()
        if not conn: return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM inventori_panen")
        result = cursor.fetchall()
        cursor.close(); conn.close()
        return result

    @staticmethod
    def insert(id_petani, jenis, berat, tanggal):
        conn = DatabaseConnection.connect()
        if not conn: return False
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventori_panen (id_petani, jenis_komoditas, jumlah_berat, tgl_panen) VALUES (%s, %s, %s, %s)", (id_petani, jenis, berat, tanggal))
        conn.commit()
        cursor.close(); conn.close()
        return True

    @staticmethod
    def update(id_panen, id_petani, jenis, berat, tanggal):
        conn = DatabaseConnection.connect()
        if not conn: return False
        cursor = conn.cursor()
        cursor.execute("UPDATE inventori_panen SET id_petani=%s, jenis_komoditas=%s, jumlah_berat=%s, tgl_panen=%s WHERE id_panen=%s", (id_petani, jenis, berat, tanggal, id_panen))
        conn.commit()
        cursor.close(); conn.close()
        return True

    @staticmethod
    def delete(id_panen):
        conn = DatabaseConnection.connect()
        if not conn: return False
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventori_panen WHERE id_panen=%s", (id_panen,))
        conn.commit()
        cursor.close(); conn.close()
        return True