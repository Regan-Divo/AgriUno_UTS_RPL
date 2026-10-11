import mysql.connector

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="agriuno"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None