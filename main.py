import sqlite3
import requests
from bs4 import BeautifulSoup

shanbe = 'شنبه'
yekshanbe = 'یکشنبه'
doshanbe = 'دوشنبه'
seshanbe = 'سه شنبه'
charshanbe = 'چهارشنبه'
panjshanbe = 'پنجشنبه'
jome = 'جمعه'

days_dic = {
    shanbe: 0,
    yekshanbe: 1,
    doshanbe: 2,
    seshanbe: 3,
    charshanbe: 4,
    panjshanbe: 5,
    jome: 6,
}


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
        conn = sqlite3.connect('jozve.db')
        cursor = conn.cursor()
        cursor.execute(query, values)
        if is_select_query:
            rows = cursor.fetchall()
            return rows
    finally:
        conn.commit()
        cursor.close()


sql_create_Courses_table = """ CREATE TABLE IF NOT EXISTS Courses (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    clock text,
                                    days text
                                ); """
sql_create_Users_table = """ CREATE TABLE IF NOT EXISTS Users (
                                    chat_id text PRIMARY KEY,
                                    username text,
                                    password text,
                                    id text,
                                    name text ,
                                    department text,
                                    courses text,
                                    status integer DEFAULT 0
                                ); """
do_sql_query(sql_create_Courses_table, values=[])
do_sql_query(sql_create_Users_table, values=[])


sql_create_Subdirs_table = """ CREATE TABLE IF NOT EXISTS SubDirs (
                                    id integer PRIMARY KEY,
                                    parent integer NOT NULL,
                                    name text NOT NULL,
                                    FOREIGN KEY (parent) REFERENCES SubDirs(id) ON DELETE CASCADE
                                ); """

sql_create_files_table = """ CREATE TABLE IF NOT EXISTS Files (
                                    id integer PRIMARY KEY,
                                    parent integer NOT NULL,
                                    name text NOT NULL,
                                    FOREIGN KEY (parent) REFERENCES SubDirs(id) ON DELETE CASCADE
                                ); """

# do_sql_query2(sql_create_Directories_table, [])
do_sql_query(sql_create_Subdirs_table, [])
do_sql_query(sql_create_files_table, [])

# try:
#     sql = """ALTER TABLE Courses
#                                 ADD deadline text;"""
#     do_sql_query(sql, [])
# except:
#     pass

# try:
#     sql = """DROP TABLE Directories;"""
#     do_sql_query2(sql, [])
# except:
#     pass


# try:
#     sql = """ALTER TABLE Courses
#                                 ADD admin text DEFAULT MHHasani;"""
#     do_sql_query(sql, [])
# except:
#     pass


def start(chat_id, username, password):
    dic_course = {}
    user = {}
    url = 'https://lms.iust.ac.ir/login/index.php'
    with requests.session() as session:
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        url = soup.find(class_="btn btn-primary btn-block")['href']
        response = session.get(url)
        data = {
            'name': username,
            "pass": password,
            # "form_build_id": "form-I0t7Yj6NBHjmQPhNqOaulhhjaf4BEqcKxpTDZbfwYvk",
            "form_id": "oauth2_server_authenticate_form",
            "op": "ورود"
        }
        response = session.post(
            'https://its.iust.ac.ir/oauth2/autheticate', data=data)
        response = session.get('https://lms.iust.ac.ir/user/profile.php')
        soup = BeautifulSoup(response.text, 'lxml')

        user['name'] = soup.find(class_="contentnode fullname").span.text

        user['id'] = soup.find(
            class_="contentnode idnumber aduseropt").dd.text.strip('S:')
        user['department'] = soup.find(
            class_="contentnode department aduseropt").dd.text
        user['chat_id'] = chat_id

        courses = soup.find(
            'li', class_="contentnode courseprofiles").find_all('a')
        response = session.get(courses[-1]['href'])
        soup = BeautifulSoup(response.text, 'lxml')
        courses = soup.find(
            'li', class_="contentnode courseprofiles").find_all('a')
        for i in range(len(courses)):
            course = courses[i]
            dic_course[course.text] = {'id': "https://lms.iust.ac.ir/course/view.php?id=" +
                                       course['href'].split("&course=")[1]}
        for key, course in dic_course.items():
            response = session.get(course['id'])
            soup = BeautifulSoup(response.text, 'lxml')
            try:
                adobe = soup.find(
                    class_="activity adobeconnect modtype_adobeconnect").find('a')['href']
            except:
                break
            # https://lms.iust.ac.ir/mod/adobeconnect/view.php?id=413574
            dic_course[key]['id'] = adobe.split('id=')[-1]

            response = session.get(adobe)
            soup = BeautifulSoup(response.text, 'lxml')
            class_time = soup.find(class_="aconmeetinforow").find_all(
                class_="aconlabeltitle")[-1].text
            d_c = class_time.split('از ساعت')
            days = d_c[0].split('زمان تشکیل جلسه :هر')[-1].split(' و ')
            days_list = ""
            for day in days:
                day = day.strip(' ')
                days_list += str(days_dic[day])+","
            clock = d_c[-1].split(' ')[1]
            dic_course[key]['days'] = days_list
            dic_course[key]['clock'] = clock

        str_courses_id = ""
        for k, v in dic_course.items():
            sql = "INSERT INTO Courses (id,name,clock,days) VALUES (?,?,?,?)"
            try:
                values = [dic_course[k]['id'], k, dic_course[k]
                          ['clock'], str(dic_course[k]['days'])]
            except:
                break
            str_courses_id += dic_course[k]['id'] + ","
            try:
                do_sql_query(sql, values)
            except:
                continue

        sql = "UPDATE Users SET id = ?, name = ?, department = ?, courses = ? ,status = ? WHERE chat_id = ?"
        values = [user['id'], user['name'], user['department'],
                  str_courses_id, 3, user['chat_id']]
        do_sql_query(sql, values)
        return dic_course


sql = "SELECT * FROM Users"
Users = do_sql_query(sql, [], is_select_query=True)
for User in Users:
    if User[0] and User[1] and User[2] and not User[3]:
        try:
            start(User[0], User[1], User[2])
            print(User[0])
        except:
            sql = "DELETE FROM Users WHERE chat_id = ?"
            value = [User[0]]
            do_sql_query(sql, value)
            sql = "INSERT INTO Users (chat_id,status) VALUES (?,?)"
            value = [User[0], 2]
            do_sql_query(sql, value)

sql = "SELECT * FROM Courses"
courses = do_sql_query(sql, [], is_select_query=True)


# sql = "DELETE FROM ID WHERE id = ?"
# sql = "INSERT INTO ID (id) VALUES (?)"
# values = ["40958349085"]
# do_sql_query(sql, ["2133278030"])
# do_sql_query(sql, values)

# sql = "SELECT id FROM ID"
# rows = do_sql_query(sql, [], is_select_query=True)
# print(rows)


# response = session.get(adobe)
# soup = BeautifulSoup(response.text, 'lxml')
# adobe = soup.find(class_="aconbtnjoin").input['onclick']
# adobe = adobe.split("'")[1]
# response = session.get(adobe)
# soup = BeautifulSoup(response.text, 'lxml')
# with open('index.html', 'w') as f:
#     f.write(str(soup))
