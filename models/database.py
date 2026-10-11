import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Menginisialisasi koneksi terpusat ke database MySQL (Laragon)"""
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            database='agriuno',
            user='root',
            password=''
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Gagal terhubung ke database MySQL: {e}")
        return None

def insert_panen(id_petani, jenis_komoditas, jumlah_berat, tgl_panen):
    """Menyimpan data setoran panen baru dengan Prepared Statement untuk mencegah SQL Injection"""
    conn = get_db_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO inventori_panen (id_petani, jenis_komoditas, jumlah_berat, tgl_panen) VALUES (%s, %s, %s, %s)"
            values = (id_petani, jenis_komoditas, jumlah_berat, tgl_panen)
            cursor.execute(query, values)
            conn.commit()
            return True
        except Error as e:
            conn.rollback()
            print(f"Error transaksi database: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False