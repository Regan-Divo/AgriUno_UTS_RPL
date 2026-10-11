import mysql.connector
from mysql.connector import Error

class DatabaseManager:
    """
    Kelas Model Terpusat untuk Manajemen Pangkalan Data MySQL (Laragon).
    Menerapkan pola desain Singleton-like connection dan transaksi atomik.
    """
    
    _HOST = '127.0.0.1'
    _DATABASE = 'agriuno'
    _USER = 'root'
    _PASSWORD = ''
    _PORT = 3306

    @classmethod
    def get_connection(cls):
        """Membuat koneksi terenkapsulasi ke server basis data."""
        try:
            connection = mysql.connector.connect(
                host=cls._HOST,
                database=cls._DATABASE,
                user=cls._USER,
                password=cls._PASSWORD,
                port=cls._PORT
            )
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"[CRITICAL ERROR] Gagal terhubung ke MySQL: {e}")
            return None

    @classmethod
    def execute_non_query(cls, query, params=None):
        """Menjalankan kueri DML (INSERT, UPDATE, DELETE) dengan rollback pengaman."""
        conn = cls.get_connection()
        if not conn:
            return False, "Koneksi ke basis data terputus."
        
        cursor = conn.cursor()
        try:
            conn.start_transaction()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return True, "Operasi basis data berhasil dieksekusi."
        except Error as e:
            conn.rollback()
            return False, f"Kesalahan transaksi basis data: {e}"
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def fetch_records(cls, query, params=None):
        """Mengambil sekumpulan data (SELECT) dengan hasil berupa kamus data terstruktur."""
        conn = cls.get_connection()
        if not conn:
            return []
        
        cursor = conn.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"[ERROR FETCH] Gagal mengambil data: {e}")
            return []
        finally:
            cursor.close()
            conn.close()