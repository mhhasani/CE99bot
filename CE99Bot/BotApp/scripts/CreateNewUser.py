from select import select
from unicodedata import name
from BotApp.models import *
from django.http import JsonResponse

import requests
from bs4 import BeautifulSoup
from CE99Bot.config import *

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
        return {"status": "OK", "session": session, "soup": soup, "full_name": full_name, "student_id": student_id, "department": department}
    except:
        return {"status": "Error", "session": session}


def set_user_info(user, user_info, departments, statuses):
    status = user_info['status']

    if status == 'OK':
        user.full_name = user_info['full_name']
        user.student_id = user_info['student_id']

        if user_info['department'] in departments:
            user.department = departments.get(user_info['department'])
        else:
            new_department = Department.objects.create(name=user_info['department'])
            user.department = new_department
            departments[user_info['department']] = new_department

        user.status = statuses.get('correct')
        user.save()
        return {"status": "correct"}

    elif status == 'Error':
        return {"status": "error"}


def crawl_course_info(session, soup):
    all_courses = {course.name: course for course in Course.objects.all()}
    # Get the user's courses
    dic_course = {}
    courses = soup.find('li', class_="contentnode courseprofiles").find_all('a')
    response = session.get(courses[-1]['href'])
    soup = BeautifulSoup(response.text, 'lxml')
    courses = soup.find('li', class_="contentnode courseprofiles").find_all('a')
    for i in range(len(courses)):
        course = courses[i]
        course_id = course['href'].split("&course=")[1].split("&")[0]
        course_name = course.text
        course_term = course_name.split(" ")[-1]
        course_term = course_term[1:len(course_term) - 1]
        course_view_link = BASE_VIEW_LINK + course_id    
        course_info_link = BASE_INFO_LINK + course_id
        course_is_active = False
        dic_course[course_name] = {"crawled":False, "id": course_id, "term": course_term, "view_link": course_view_link, "info_link": course_info_link, "is_active": course_is_active}
        if course_name in all_courses:  
            dic_course[course_name]["crawled"] = True

        response = session.get(course_view_link)
        soup = BeautifulSoup(response.text, 'lxml')
        # Get the user's courses' view link
        if soup.find(id="editingbutton"):
            dic_course[course_name]['user_course_type'] = "TA"
        else:
            dic_course[course_name]['user_course_type'] = "student"
        try:
            adobe = soup.find(class_="activity adobeconnect modtype_adobeconnect").find('a')['href']
            # https://lms.iust.ac.ir/mod/adobeconnect/view.php?id=413574
            response = session.get(adobe)
            soup = BeautifulSoup(response.text, 'lxml')
            class_time = soup.find(class_="aconmeetinforow").find_all(
                class_="aconlabeltitle")[-1].text
            d_c = class_time.split('از ساعت')
            days = d_c[0].split('زمان تشکیل جلسه :هر')[-1].split(' و ')
            days_list = []
            for day in days:
                day = day.strip(' ')
                days_list.append(day)
            clock = d_c[-1].split(' ')[1]
            dic_course[course_name]['days'] = days_list
            dic_course[course_name]['clock'] = clock
            dic_course[course_name]['is_active'] = True
        except:
            dic_course[course_name]['days'] = None
            dic_course[course_name]['clock'] = None

    return dic_course 


def set_user_courses(user, course_info, courses):
    terms = {term.name: term for term in Term.objects.all()}
    user_courses = {user_course.course: user_course for user_course in UserCourse.objects.all().filter(user=user)}
    days = {day.name: day for day in Day.objects.all()}
    clocks = {clock.time: clock for clock in ClockTime.objects.all()}
    user_course_type = {usertype.name: usertype for usertype in UserCourseType.objects.all()}


    for course_name, course in course_info.items():
        if course['crawled']:
            course_obj = Course.objects.get(name=course_name)
            if course_obj not in user_courses:
                user_type = user_course_type.get(course['user_course_type'])
                user_course = UserCourse.objects.create(user=user, course=course_obj, user_type=user_type)
                user_courses[course_obj] = user_course
            continue
               
        term = None
        if course['term'] in terms:
            term = terms.get(course['term'])
        elif course['term']:
            new_term = Term.objects.create(name=course['term'])
            term = new_term
            terms[course['term']] = new_term

        if course_name in courses:
            course_obj = courses.get(course_name)
        else:
            course_obj = Course.objects.create(name=course_name, code=course['id'], term=term)
            courses[course_name] = course_obj

        if course['clock'] in clocks:
            clock_obj = clocks.get(course['clock'])
        elif course['clock']:
            new_clock = ClockTime.objects.create(time=course['clock'])
            clock_obj = new_clock
            clocks[course['clock']] = new_clock

        if course['days']:
            for day in course['days']:
                if day in days:
                    day_obj = days.get(day)
                elif day:
                    new_day = Day.objects.create(name=day)
                    day_obj = new_day
                    days[day] = new_day

                course_day_clocktime = CourseDayClockTime.objects.filter(course=course_obj, day=day_obj, clock_time=clock_obj)
                if not course_day_clocktime:
                    CourseDayClockTime.objects.create(course=course_obj, day=day_obj, clock_time=clock_obj)
                    

        if course_obj in user_courses:
            user_course = user_courses.get(course_obj)
        else:
            user_type = user_course_type.get(course['user_course_type'])
            user_course = UserCourse.objects.create(user=user, course=course_obj, user_type=user_type)
            user_courses[course_obj] = user_course
   

def crawl_teachers_info():
    # login
    session = login(USERNAME, PASSWORD)
    if not session:
        return None
    print(USERNAME, "login!")
    print("Getting teacher courses...")
    # Get the user's courses' info link
    dic_course = {}
    courses = Course.objects.all().filter(teacher__isnull=True)
    for course in courses:
        course_name = course.name
        course_id = course.code
        course_info_link = BASE_INFO_LINK + course_id
        dic_course[course_name] = {"id": course_id}
        try:
            response = session.get(course_info_link)
            soup = BeautifulSoup(response.text, 'lxml')
            teacher = soup.find(class_="teachers").find('a')
            teacher_name = teacher.text
            teacher_id = teacher['href'].split('id=')[-1].split('&')[0]
            dic_course[course_name]['teacher_name'] = teacher_name
            dic_course[course_name]['teacher_id'] = teacher_id
        except:
            dic_course[course_name]['teacher_name'] = None
            dic_course[course_name]['teacher_id'] = None  

    return set_courses_teacher(dic_course) 


def set_courses_teacher(course_info):
    print("Setting teacher courses...")
    selected_courses = Course.objects.all().filter(teacher__isnull=True)
    courses = {course.name: course for course in selected_courses}
    teachers = {teacher.lms_id: teacher for teacher in Teacher.objects.all()}

    for course_name, course in courses.items():
        teacher = None
        curr_course_info = course_info.get(course_name)
        if not curr_course_info:
            continue
        if curr_course_info['teacher_id'] in teachers:
            teacher = teachers.get(curr_course_info['teacher_id'])
        elif curr_course_info['teacher_id']:
            teacher = Teacher.objects.create(name=curr_course_info['teacher_name'], lms_id=curr_course_info['teacher_id'])
            teachers[curr_course_info['teacher_id']] = teacher 

        course.teacher = teacher
    
    selected_courses.bulk_update(selected_courses, ['teacher'])



def apply(chat_id):
    user = User.objects.all().filter(chat_id=chat_id).first()
    departments = {department.name: department for department in Department.objects.all()}
    statuses = {status.name: status for status in UserStatus.objects.all()}
    courses = {course.name: course for course in Course.objects.all()}

    session = login(user.lms_username, user.lms_password)
    if not session:
        user.status = statuses.get('wrong')
        user.save()
        print(user.lms_username, "login failed!")
        return 'error'

    print(user.lms_username, "login!")
    print("Getting user info...")
    user_info = crawl_user_info(session, user)
    print("Setting user info...")
    status = set_user_info(user, user_info, departments, statuses)['status']
    if status == 'error':
        return 'wrong'

    elif status == 'correct':
        print("Getting user courses...")
        course_info = crawl_course_info(session, user_info['soup'])
        print("Setting user courses...")
        set_user_courses(user, course_info, courses)

    return 'correct'

