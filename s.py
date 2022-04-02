import sqlite3


def do_sql_query(query, values, is_select_query=False):
    try:
        conn = sqlite3.connect('jozve.db')
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
        conn = sqlite3.connect('Data_LMS.db')
        cursor = conn.cursor()
        cursor.execute(query, values)
        if is_select_query:
            rows = cursor.fetchall()
            return rows
    finally:
        conn.commit()
        cursor.close()


sql_create_Directories_table = """ CREATE TABLE IF NOT EXISTS Directories (
                                    id integer PRIMARY KEY,
                                    parent integer,
                                    name text NOT NULL
                                ); """

sql_create_files_table = """ CREATE TABLE IF NOT EXISTS Files (
                                    id integer PRIMARY KEY,
                                    parent integer,
                                    name text NOT NULL
                                ); """

do_sql_query(sql_create_Directories_table, [])
do_sql_query(sql_create_files_table, [])


sql = "SELECT * FROM Courses"
courses = do_sql_query2(sql, [], is_select_query=True)

for course in courses:
    id = course[0]
    name = course[1]
    sql = "INSERT INTO Directories (id,name) VALUES (?,?)"
    try:
        do_sql_query(sql, [id, name])
    except:
        pass
