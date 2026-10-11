from config.database import get_connection
from datetime import datetime

class PanenModel:
    @staticmethod
    def tambah_panen(id_petani, jenis_komoditas, jumlah_berat):
        jenis_komoditas = jenis_komoditas.strip().title()
        tgl_panen = datetime.now().strftime('%Y-%m-%d')
        
        conn = get_connection()
        if not conn:
            return False, "Koneksi database gagal."
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id_petani FROM petani WHERE id_petani = %s", (id_petani,))
            if not cursor.fetchone():
                return False, f"ID Petani '{id_petani}' tidak ditemukan dalam sistem."

            query = "INSERT INTO inventori_panen (id_petani, jenis_komoditas, jumlah_berat, tgl_panen) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (id_petani, jenis_komoditas, jumlah_berat, tgl_panen))
            conn.commit()
            return True, "Data panen berhasil dicatat."
        except Exception as e:
            return False, f"Terjadi kesalahan: {e}"
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def delete_panen(id_panen):
        conn = get_connection()
        if not conn:
            return False, "Koneksi database gagal."
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM inventori_panen WHERE id_panen = %s", (id_panen,))
            conn.commit()
            return True, "Data lot panen berhasil dihapus."
        except Exception as e:
            return False, f"Gagal menghapus: Lot panen masih memiliki data distribusi terkait."
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_panen():
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT p.id_panen, pt.nama_petani, p.jenis_komoditas, p.jumlah_berat, p.tgl_panen 
                FROM inventori_panen p
                JOIN petani pt ON p.id_petani = pt.id_petani
                ORDER BY p.id_panen DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_panen_by_id(id_panen):
        conn = get_connection()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM inventori_panen WHERE id_panen = %s", (id_panen,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()