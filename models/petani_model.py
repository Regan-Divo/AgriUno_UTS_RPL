from config.database import get_connection

class PetaniModel:
    @staticmethod
    def tambah_petani(nama_petani, lokasi_lahan, komoditas_utama):
        nama_petani = nama_petani.strip().title()
        lokasi_lahan = lokasi_lahan.strip().title()
        komoditas_utama = komoditas_utama.strip().title()
        
        conn = get_connection()
        if not conn:
            return False, "Koneksi database gagal."
        cursor = conn.cursor(dictionary=True)
        try:
            check_query = """
                SELECT id_petani FROM petani 
                WHERE LOWER(nama_petani) = LOWER(%s) 
                  AND LOWER(lokasi_lahan) = LOWER(%s) 
                  AND LOWER(komoditas_utama) = LOWER(%s)
            """
            cursor.execute(check_query, (nama_petani, lokasi_lahan, komoditas_utama))
            if cursor.fetchone():
                return False, f"Data petani '{nama_petani}' dengan detail tersebut sudah terdaftar!"

            query = "INSERT INTO petani (nama_petani, lokasi_lahan, komoditas_utama) VALUES (%s, %s, %s)"
            cursor.execute(query, (nama_petani, lokasi_lahan, komoditas_utama))
            conn.commit()
            return True, "Data petani berhasil ditambahkan."
        except Exception as e:
            return False, f"Terjadi kesalahan: {e}"
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update_petani(id_petani, nama_petani, lokasi_lahan, komoditas_utama):
        nama_petani = nama_petani.strip().title()
        lokasi_lahan = lokasi_lahan.strip().title()
        komoditas_utama = komoditas_utama.strip().title()

        conn = get_connection()
        if not conn:
            return False, "Koneksi database gagal."
        cursor = conn.cursor()
        try:
            query = "UPDATE petani SET nama_petani = %s, lokasi_lahan = %s, komoditas_utama = %s WHERE id_petani = %s"
            cursor.execute(query, (nama_petani, lokasi_lahan, komoditas_utama, id_petani))
            conn.commit()
            return True, "Data petani berhasil diperbarui."
        except Exception as e:
            return False, f"Terjadi kesalahan: {e}"
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def delete_petani(id_petani):
        conn = get_connection()
        if not conn:
            return False, "Koneksi database gagal."
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM petani WHERE id_petani = %s", (id_petani,))
            conn.commit()
            return True, "Data petani berhasil dihapus."
        except Exception as e:
            return False, f"Gagal menghapus: Petani masih memiliki relasi data panen aktif."
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_petani():
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id_petani, nama_petani, lokasi_lahan, komoditas_utama FROM petani")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()