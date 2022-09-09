from .models import *
from .decorators import is_authenticated
from .scripts import StaticDataImportDB, CreateNewUser, UserCourseCUBE

from django.http import JsonResponse
from django.db.models import F


def static_data_import_db(request):
    try:
        StaticDataImportDB.apply()
        return JsonResponse({"status": "OK"})
    except:
        return JsonResponse({"status": "error"})

def create_usercourse_cube(request):
    UserCourseCUBE.apply()
    return JsonResponse({"status": "OK"})


def crawl_users_info(request):
    # try:
        CreateNewUser.apply()
        return JsonResponse({"status": "OK"})
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
        return crawl_users_info(request)
    else:
        return JsonResponse({"status": "error"})


def show_main_table(request, chat_id):
    user_courses = UserCourse_CUBE.objects.get(user__chat_id=chat_id)
    dailycourse_info = user_courses.dailycourse_info
    courses = user_courses.courses

    return JsonResponse({"status": "OK", "dailycourse_info": dailycourse_info, "courses": courses})