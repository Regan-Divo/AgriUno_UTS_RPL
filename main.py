import mysql.connector
from mysql.connector import Error

def koneksi_database():
    try:
        koneksi = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="agriuno",
            port=3306
        )

        if koneksi.is_connected():
            print("Berhasil terhubung ke database AgriUno!")
            return koneksi

    except Error as e:
        print("Koneksi database gagal:", e)

    return None

if __name__ == "__main__":
    db = koneksi_database()

    if db:
        db.close()
        print("Koneksi database ditutup.")