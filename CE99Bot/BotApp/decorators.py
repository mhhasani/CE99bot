from .models import *
from django.http import JsonResponse
from .views import *

def get_user_status(request, chat_id):
    user = User.objects.filter(chat_id=chat_id).first()
    if user:
        status = user.status.name
        return status in ["correct", "ended"]
    return

def is_authenticated(func):
    def wrapper(request, chat_id):
        if get_user_status(request, chat_id):
            return func(request, chat_id)
        else:
            return JsonResponse({"status": "not_authenticated"})
    return wrapper
    
