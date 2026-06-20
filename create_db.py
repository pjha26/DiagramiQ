import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

try:
    conn = psycopg2.connect(dbname='postgres', user='postgres', password='yourpassword', host='localhost', port='5432')
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('CREATE DATABASE diagramiq')
    cur.close()
    conn.close()
    print("Database created successfully.")
except psycopg2.errors.DuplicateDatabase:
    print("Database already exists.")
except Exception as e:
    print(f"Error creating database: {e}")
    sys.exit(1)
