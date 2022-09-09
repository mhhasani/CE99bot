import json
from pathlib import Path
from BotApp.models import UserCourseType, UserStatus, Day
from CE99Bot.config import *


def apply():
    UserStatus_Insert()
    Day_Insert()
    UserCourseType_Insert()



def UserStatus_Insert():
    file = str(Path(TEXT_FILE_PATH, 'constant.json'))
    f = open(file,encoding="utf-8")
    result = json.load(f)
    f.close()

    all_status = UserStatus.objects.all().values_list('name', flat=True)

    for status in result['status_list']:
        if status not in all_status:
            UserStatus.objects.create(name=status)

def Day_Insert():
    file = str(Path(TEXT_FILE_PATH, 'constant.json'))
    f = open(file,encoding="utf-8")
    result = json.load(f)
    f.close()

    all_day = Day.objects.all().values_list('name', flat=True)

    for day in result['day_list']:
        if day not in all_day:
            Day.objects.create(name=day)

def UserCourseType_Insert():
    file = str(Path(TEXT_FILE_PATH, 'constant.json'))
    f = open(file,encoding="utf-8")
    result = json.load(f)
    f.close()

    all_type = UserCourseType.objects.all().values_list('name', flat=True)

    for type in result['user_course_type']:
        if type not in all_type:
            UserCourseType.objects.create(name=type)