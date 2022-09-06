from BotApp.models import *
from django.http import JsonResponse

import requests
from bs4 import BeautifulSoup


def login(username, password):
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
        response = session.post('https://its.iust.ac.ir/oauth2/autheticate', data=data)
        if response.status_code == 200:
            return session
        else:
            return None


def crawl_user_info(session, user):
    # Get the user's info
    try:
        response = session.get('https://lms.iust.ac.ir/user/profile.php')
        soup = BeautifulSoup(response.text, 'lxml')
        full_name = soup.find(class_="contentnode fullname").span.text
        student_id = soup.find(class_="contentnode idnumber aduseropt").dd.text.strip('S:')
        department = soup.find(class_="contentnode department aduseropt").dd.text
        return {"full_name": full_name, "student_id": student_id, "department": department}
    except:
        return False
    

# def crawl_course_info(session, user):
#     # Get the user's courses
#     dic_course = {}
#     courses = soup.find('li', class_="contentnode courseprofiles").find_all('a')
#     response = session.get(courses[-1]['href'])
#     soup = BeautifulSoup(response.text, 'lxml')
#     courses = soup.find('li', class_="contentnode courseprofiles").find_all('a')
#     for i in range(len(courses)):
#         course = courses[i]
#         dic_course[course.text] = {'id': "https://lms.iust.ac.ir/course/view.php?id=" + course['href'].split("&course=")[1]}
    
#     for key, course in dic_course.items():
#         response = session.get(course['id'])
#         soup = BeautifulSoup(response.text, 'lxml')
#         try:
#             adobe = soup.find(class_="activity adobeconnect modtype_adobeconnect").find('a')['href']
#         except:
#             break
#         # https://lms.iust.ac.ir/mod/adobeconnect/view.php?id=413574
#         dic_course[key]['id'] = adobe.split('id=')[-1]

#         response = session.get(adobe)
#         soup = BeautifulSoup(response.text, 'lxml')
#         class_time = soup.find(class_="aconmeetinforow").find_all(
#             class_="aconlabeltitle")[-1].text
#         d_c = class_time.split('از ساعت')
#         days = d_c[0].split('زمان تشکیل جلسه :هر')[-1].split(' و ')
#         days_list = ""
#         for day in days:
#             day = day.strip(' ')
#             days_list += str(days_dic_lms[day])+","
#         clock = d_c[-1].split(' ')[1]
#         dic_course[key]['days'] = days_list
#         dic_course[key]['clock'] = clock

#     str_courses_id = ""
#     for k, v in dic_course.items():
#         sql = "INSERT INTO Courses (id,name,clock,days) VALUES (?,?,?,?)"
#         try:
#             values = [dic_course[k]['id'], k, dic_course[k]
#                     ['clock'], str(dic_course[k]['days'])]
#         except:
#             break
#         str_courses_id += dic_course[k]['id'] + ","
#         try:
#             do_sql_query2(sql, values)
#         except:
#             continue

#     sql = "UPDATE new_users SET id = ?, name = ?, department = ?, courses = ? ,status = ? WHERE chat_id = ?"
#     values = [user['id'], user['name'], user['department'],
#             str_courses_id, 3, user['chat_id']]
#     do_sql_query2(sql, values)
# print(new_user[0]) 
   


def apply():
    users = User.objects.all().filter(status__name='waiting')
    departments = Department.objects.all()
    statuses = UserStatus.objects.all()

    for user in users:
        session = login(user.lms_username, user.lms_password)
        if session:
            user_info = crawl_user_info(session, user)
            if user_info:
                user.full_name = user_info['full_name']
                user.student_id = user_info['student_id']
                if user_info['department'] in departments:
                    user.department = departments.get(name=user_info['department'])
                user.status = statuses.get(name='correct')
            else:
                user.status = statuses.get(name='wrong')
    users.bulk_update(users, ['status', 'full_name', 'student_id', 'department'])

