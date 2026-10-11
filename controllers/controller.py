from models.database import create_connection

class AgriController:
    # Mengambil data petani untuk ditampilkan di tabel/form
    @staticmethod
    def ambil_data_petani():
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_petani, nama_petani, lokasi_lahan, komoditas FROM petani")
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        return []

    # Menyimpan data petani baru
    @staticmethod
    def tambah_petani(nama, lokasi, komoditas):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = "INSERT INTO petani (nama_petani, lokasi_lahan, komoditas) VALUES (%s, %s, %s)"
                cursor.execute(query, (nama, lokasi, komoditas))
                conn.commit()
                cursor.close()
                conn.close()
                return True
            except Exception as e:
                print(f"Error database: {e}")
                conn.rollback()
                conn.close()
                return False
        return False