from .models import User, UserStatus
from .decorators import is_authenticated
from .scripts import StaticDataImportDB, CreateNewUser

from django.http import JsonResponse


def static_data_import_db(request):
    try:
        StaticDataImportDB.apply()
        return JsonResponse({"status": "OK"})
    except:
        return JsonResponse({"status": "error"})


def crawl_users_info(request):
    CreateNewUser.apply()
    return JsonResponse({"status": "OK"})


def start_bot(request, chat_id):
    user = User.objects.filter(chat_id=chat_id).first()
    if user:
        if user.status.name in ["correct", "ended"]:
            return JsonResponse({"status": "authenticated"})
        else:
            return JsonResponse({"status": "not_authenticated"})
    else:
        return initial_create_user(request, chat_id)


def initial_create_user(request, chat_id):
    try:
        status = UserStatus.objects.get(name="null")
        User.objects.create(chat_id=chat_id, status=status)
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
        return JsonResponse({"status": "OK"})
    else:
        return JsonResponse({"status": "error"})

