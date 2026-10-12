"""
==========================================
KONFIGURASI DATABASE MYSQL - AGRIUNO
Database: agriuno (Laragon)
==========================================
"""
import mysql.connector
from mysql.connector import Error

class DatabaseConnection:
    @staticmethod
    def connect():
        try:
            connection = mysql.connector.connect(
                host='localhost',
                database='agriuno',
                user='root',
                password=''
            )
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Kesalahan Koneksi Database: {e}")
        return None