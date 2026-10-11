from config.database import get_connection
from models.panen_model import PanenModel

class DistribusiModel:
    @staticmethod
    def tambah_distribusi(id_panen, tujuan_pengiriman, jumlah_dikirim):
        tujuan_pengiriman = tujuan_pengiriman.strip().title()
        
        panen = PanenModel.get_panen_by_id(id_panen)
        if not panen:
            return False, f"ID Panen '{id_panen}' tidak ditemukan dalam database."
        
        stok_tersedia = float(panen['jumlah_berat'])
        
        conn = get_connection()
        if not conn:
            return False, "Koneksi database gagal."
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT SUM(jumlah_dikirim) as total_kirim FROM distribusi WHERE id_panen = %s", (id_panen,))
            res = cursor.fetchone()
            sudah_dikirim = float(res['total_kirim']) if res and res['total_kirim'] else 0.0
            
            sisa_stok = stok_tersedia - sudah_dikirim
            if jumlah_dikirim > sisa_stok:
                return False, f"Gagal: Jumlah kirim ({jumlah_dikirim} Kg) melebihi sisa stok panen ({sisa_stok} Kg dari total {stok_tersedia} Kg)!"
            
            insert_query = "INSERT INTO distribusi (id_panen, tujuan_pengiriman, jumlah_dikirim, status_pengiriman) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (id_panen, tujuan_pengiriman, jumlah_dikirim, "Diproses"))
            conn.commit()
            return True, "Distribusi berhasil dialokasikan."
        except Exception as e:
            return False, f"Terjadi kesalahan: {e}"
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def delete_distribusi(id_distribusi):
        conn = get_connection()
        if not conn:
            return False, "Koneksi database gagal."
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM distribusi WHERE id_distribusi = %s", (id_distribusi,))
            conn.commit()
            return True, "Data distribusi berhasil dihapus."
        except Exception as e:
            return False, f"Terjadi kesalahan: {e}"
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_distribusi():
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT d.id_distribusi, d.id_panen, pt.nama_petani, p.jenis_komoditas, d.tujuan_pengiriman, d.jumlah_dikirim, d.status_pengiriman 
                FROM distribusi d
                JOIN inventori_panen p ON d.id_panen = p.id_panen
                JOIN petani pt ON p.id_petani = pt.id_petani
                ORDER BY d.id_distribusi DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()