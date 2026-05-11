import pyodbc
from db_connection import cursor


cursor.execute("SELECT * FROM recipient")
rows = cursor.fetchall()

for row in rows:
    print(row)