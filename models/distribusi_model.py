from config.database import DatabaseConnection

class DistribusiModel:
    @staticmethod
    def get_all():
        conn = DatabaseConnection.connect()
        if not conn: return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM distribusi")
        result = cursor.fetchall()
        cursor.close(); conn.close()
        return result

    @staticmethod
    def insert(id_panen, tujuan, jumlah, status="Diproses"):
        conn = DatabaseConnection.connect()
        if not conn: return False
        cursor = conn.cursor()
        cursor.execute("INSERT INTO distribusi (id_panen, tujuan_pengiriman, jumlah_dikirim, status_pengiriman) VALUES (%s, %s, %s, %s)", (id_panen, tujuan, jumlah, status))
        conn.commit()
        cursor.close(); conn.close()
        return True

    @staticmethod
    def update(id_distribusi, id_panen, tujuan, jumlah, status):
        conn = DatabaseConnection.connect()
        if not conn: return False
        cursor = conn.cursor()
        cursor.execute("UPDATE distribusi SET id_panen=%s, tujuan_pengiriman=%s, jumlah_dikirim=%s, status_pengiriman=%s WHERE id_distribusi=%s", (id_panen, tujuan, jumlah, status, id_distribusi))
        conn.commit()
        cursor.close(); conn.close()
        return True

    @staticmethod
    def delete(id_distribusi):
        conn = DatabaseConnection.connect()
        if not conn: return False
        cursor = conn.cursor()
        cursor.execute("DELETE FROM distribusi WHERE id_distribusi=%s", (id_distribusi,))
        conn.commit()
        cursor.close(); conn.close()
        return True