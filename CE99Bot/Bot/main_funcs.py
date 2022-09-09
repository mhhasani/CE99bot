from datetime import datetime
from telegram import (Update,
                      ParseMode,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.ext import (Updater,
                          CommandHandler,
                          MessageHandler,
                          Filters,
                          CallbackContext,
                          CallbackQueryHandler,
                          ConversationHandler,)

from const import *
import requests

def send_request(url, options):
    url = SERVER_UEL + url + '/'
    for option in options:
        url += f'{option}/'
    response = requests.get(url)
    return response.json()

def get_user_telegram_info_from_update(update: Update, context: CallbackContext):
    result = {}
    result['chat_id'] = update.message.chat_id
    result['first_name'] = update.message.from_user['first_name']
    result['last_name'] = update.message.from_user['last_name']
    result['username'] = update.message.from_user['username']
    result['is_group'] = update.message.chat.type != "private"
    result['language_code'] = update.message.from_user['language_code']
    return result
    
def static_data_import_db(update: Update, context: CallbackContext):
    response = send_request('static_data_import_db', [])

    if response['status'] == 'OK':
        update.message.reply_text('OK')

    elif response['status'] == 'error':
        update.message.reply_text(RESPONSE_TEXTS['error'])


def crawl_teachers_info(update: Update, context: CallbackContext):
    response = send_request('crawl_teachers_info', [])

    if response['status'] == 'OK':
        update.message.reply_text('OK')

    elif response['status'] == 'error':
        update.message.reply_text(RESPONSE_TEXTS['error'])


def create_main_table_text(dailycourse_info):
    # date = datetime.now() + timedelta(hours=4.5)
    date = datetime.now()
    today = DAYS[str((date.weekday()-5) % 7)]
    today_courses = sorted(dailycourse_info[today], key=lambda x: x['course_time'])

    courses = "<b>🏫 کلاس های امروز 🏫</b>\n\n"
    c = 0
    for course in today_courses:
        courses += "🔸" if c % 2 else "🔹"
        course_name = course['course_name']
        course_code = course['course_code']
        course_time = course['course_time']
        course_link = BASE_VIEW_LINK +  course_code
        courses += f"<a href='{course_link}'>{course_name.split('گروه')[0]}</a>ساعت {course_time}\n\n"
        c += 1
    if c == 0:
        courses += "امروز کلاسی نداری:)"
    
    return courses


def create_main_table_reply_markup(courses):
    keyboard = []
    c = 0
    bottom2 = []
    for course in courses:
        course_name = course['course_name']
        course_code = course['course_code']
        if len(bottom2) == 2:
            keyboard.append(bottom2)
            bottom2 = []
        bottom2.append(InlineKeyboardButton(course_name.split('گروه')[0], callback_data=course_code))
        c += 1
    if bottom2:
        keyboard.append(bottom2)

    return InlineKeyboardMarkup(keyboard)


def show_main_table(update: Update, context: CallbackContext):
    user = get_user_telegram_info_from_update(update, context)
    response = send_request('show_main_table', [user['chat_id']])
    if response['status'] == 'OK':
        dailycourse_info = response['dailycourse_info']
        courses = response['courses']
        text = create_main_table_text(dailycourse_info)
        reply_markup = create_main_table_reply_markup(courses)
        update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    elif response['status'] == 'error':
        update.message.reply_text(RESPONSE_TEXTS['error'])