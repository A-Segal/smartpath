# import pyodbc
#
# server = 'localhost'
# database = 'DeliveryDB'
# username = 'tichnut'
# password = '1234'
#
#
# conn = pyodbc.connect(
#     f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
# )
#
#
# cursor = conn.cursor()





import pyodbc

server = 'localhost'  # או 'localhost\SQLEXPRESS' אם זה SQL Server Express
database = 'DeliveryDB'
username = 'tichnut'
password = '1234'

try:
    conn = pyodbc.connect(
        f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    )
    print("✅ התחברות ל-SQL Server הצליחה!")

    cursor = conn.cursor()
    cursor.execute("SELECT 1")  # בדיקה פשוטה
    row = cursor.fetchone()
    print("בדיקה: ", row[0])

except pyodbc.Error as e:
    print("❌ שגיאה בהתחברות ל-SQL Server:")
    print(e)