import psycopg2
from psycopg2 import OperationalError

def create_connection():
    try:
        connection = psycopg2.connect(
            database="NRYDE_db",
            user="new_user",
            password="new_password",
            host="127.0.0.1",
            port="5432"
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection

create_connection()
