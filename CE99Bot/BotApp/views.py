from .models import *
from .decorators import is_authenticated
from .scripts import StaticDataImportDB, CreateNewUser, UserCourseCUBE

from django.http import JsonResponse
from django.db.models import F
import threading


def static_data_import_db(request):
    try:
        StaticDataImportDB.apply()
        return JsonResponse({"status": "OK"})
    except:
        return JsonResponse({"status": "error"})


def create_usercourse_cube(request):
    UserCourseCUBE.apply()
    return JsonResponse({"status": "OK"})


def crawl_users_info(request, chat_id):
    # try:
        status = CreateNewUser.apply(chat_id)
        return JsonResponse({"status": status})
    # except:
    #     return JsonResponse({"status": "error"})


def crawl_teachers_info(request):
    # try:
        CreateNewUser.crawl_teachers_info()
        return JsonResponse({"status": "OK"})
    # except:
    #     return JsonResponse({"status": "error"})


def start_bot(request, chat_id, username):
    user = User.objects.filter(chat_id=chat_id).first()
    if user:
        user.telegram_username = username
        user.save()
        if user.status.name in ["correct", "ended"]:
            return JsonResponse({"status": "authenticated"})
        else:
            return JsonResponse({"status": "not_authenticated"})
    else:
        return initial_create_user(request, chat_id, username)


def initial_create_user(request, chat_id, username):
    try:
        status = UserStatus.objects.get(name="null")
        User.objects.create(chat_id=chat_id, status=status, telegram_username=username)
        return JsonResponse({"status": "created"})
    except:
        return JsonResponse({"status": "error"})


def get_userpass(request, chat_id, lms_username, lms_password):
    user = User.objects.filter(chat_id=chat_id).first()
    if user:
        user.lms_username = lms_username
        user.lms_password = lms_password
        user.status = UserStatus.objects.get(name="waiting")
        user.save()
        return crawl_users_info(request, user.chat_id)
    else:
        return JsonResponse({"status": "error"})


def show_main_table(request, chat_id):
    user_courses = UserCourse_CUBE.objects.get(user__chat_id=chat_id)
    dailycourse_info = user_courses.dailycourse_info
    courses = user_courses.courses

    return JsonResponse({"status": "OK", "dailycourse_info": dailycourse_info, "courses": courses})


def show_course_table(request, course_id):
    cdc = CourseDayClockTime.objects.filter(course__code=course_id)
    course = Course.objects.get(code=course_id)
    main_dir = Directory.objects.get(course=course, parent__isnull=True)
    course_info = {
        'course_name': course.name,
        'course_code': course.code,
        'course_teacher': course.teacher.name if course.teacher else None,
        'course_term': course.term.name,
        # 'course_department': course.department.name,
        'course_days': [c.day.name for c in cdc],
        'course_times': cdc.first().clock_time.time,
        'main_dir': main_dir
    }

    return JsonResponse({"status": "OK", "course_info": course_info})


def show_directory_table(request, dir_id):
    dir_name = Directory.objects.get(id=dir_id).name
    sub_dirs = Directory.objects.filter(parent__id=dir_id)
    files = File.objects.filter(directory__id=dir_id)
    parent_id = Directory.objects.get(id=dir_id).parent.id if Directory.objects.get(id=dir_id).parent else None

    subdirs_info = []
    for sub_dir in sub_dirs:
        subdirs_info.append({
            'id': sub_dir.id,
            'name': sub_dir.name,
        })
    files_info = []
    for file in files:
        files_info.append({
            'telegram_id': file.id,
            'name': file.name,
        })

    return JsonResponse({"status": "OK", "dir_name": dir_name, "sub_dirs": subdirs_info, "files": files_info, "parent_id": parent_id})


def update_status(request, chat_id):
    user = User.objects.filter(chat_id=chat_id).first()
    if user:
        if user.status.name == "correct":
            user.status = UserStatus.objects.get(name="ended")
        elif user.status.name == "wrong":
            user.status = UserStatus.objects.get(name="null")
        user.save()
        return JsonResponse({"status": "OK"})
    else:
        return JsonResponse({"status": "error"})


def create_new_folder(request, current_folder, new_folder_name):
    pass


def create_new_file(request):
    pass


def create_deadline(request):
    pass


def edit_deadline(request):
    pass


def delete_deadline(request):
    pass
