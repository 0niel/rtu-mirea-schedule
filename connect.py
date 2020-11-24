import sqlite3
import os

 
def connect_to_sqlite():
    try:
        basedir = os.path.abspath(os.path.dirname(__file__))
        conn = sqlite3.connect(os.path.join(basedir, 'output/timetable.db'))
        cursor = conn.cursor()
        #print("База данных создана и успешно подключена к SQLite")
        sqlite_select_Query = "select sqlite_version();"
        cursor.execute(sqlite_select_Query)
        record = cursor.fetchall()
        print("Версия базы данных SQLite: ", record)
    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    return cursor
if __name__ == "__main__":
    connect_to_sqlite()
 
