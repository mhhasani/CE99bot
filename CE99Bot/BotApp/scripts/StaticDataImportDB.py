import json
from pathlib import Path
from BotApp.models import UserStatus
from CE99Bot.config import *


def apply():
    UserStatus_Insert()



def UserStatus_Insert():
    file = str(Path(TEXT_FILE_PATH, 'constant.json'))
    f = open(file,encoding="utf-8")
    result = json.load(f)
    f.close()

    all_status = UserStatus.objects.all().values_list('name', flat=True)

    for status in result['status_list']:
        if status not in all_status:
            UserStatus.objects.create(name=status)