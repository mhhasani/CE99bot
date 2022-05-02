import sqlite3


def do_sql_query(query, values, is_select_query=False):
    try:
        conn = sqlite3.connect('Data_LMS.db')
        cursor = conn.cursor()
        cursor.execute(query, values)
        if is_select_query:
            rows = cursor.fetchall()
            return rows
    finally:
        conn.commit()
        cursor.close()


def do_sql_query2(query, values, is_select_query=False):
    try:
        conn = sqlite3.connect('Data.db')
        cursor = conn.cursor()
        cursor.execute(query, values)
        if is_select_query:
            rows = cursor.fetchall()
            return rows
    finally:
        conn.commit()
        cursor.close()


try:
    sql = """ALTER TABLE Users
                                ADD tel_username text;"""
    do_sql_query(sql, [])
except:
    pass

sql = "SELECT id FROM ID"
ids = do_sql_query2(sql, [], True)
for id in ids:
    sql = "INSERT INTO Users (chat_id) VALUES (?)"
    values = [id[0]]
    try:
        do_sql_query(sql, values)
    except:
        pass
