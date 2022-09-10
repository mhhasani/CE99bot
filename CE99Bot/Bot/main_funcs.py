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


def cancel(update: Update, context: CallbackContext):
    """Cancels and ends the conversation."""
    update.message.reply_text(text='ended!')
    return ConversationHandler.END

    
def get_user_telegram_info_from_update(update: Update, context: CallbackContext):
    result = {}
    if update.callback_query:
        update = update.callback_query
        result['is_callback'] = True
    else:
        result['is_callback'] = False
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
        course_name = courses[course]['course_name']
        course_code = courses[course]['course_code']
        if len(bottom2) == 2:
            keyboard.append(bottom2)
            bottom2 = []
        callback_data=CALLBACK_DATA['course'] + ' ' +  course_code
        text = course_name.split('گروه')[0]
        bottom2.append(InlineKeyboardButton(text, callback_data=callback_data))
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


def create_course_table_text(course_info):
    course_name = course_info['course_name']
    course_code = course_info['course_code']
    course_days = course_info['course_days']
    course_times = course_info['course_times']
    course_link = BASE_VIEW_LINK + course_code
    course_teacher = course_info['course_teacher']
    # user_type = course_info['user_type']


    text = f"<b>📚 اطلاعات درس 📚</b>\n\n"
    text += f"🔸<a href='{course_link}'>{course_name}</a>\n"
    text += f"🔸روز ها: {' '.join(course_days)}\n"
    text += f"🔸ساعت: {course_times}\n"
    text += f"🔸استاد: {course_teacher}\n"
    # text += f"🔸نوع کاربر: {user_type}\n"


    return text


def show_course_table(update: Update, context: CallbackContext):
    user = get_user_telegram_info_from_update(update, context)
    if user['is_callback']:
        update = update.callback_query
    course_id = update.data.split()[1]
    response = send_request('show_course_table', [course_id])
    if response['status'] == 'OK':
        course_info = response['course_info']
        text = create_course_table_text(course_info)
        update.message.edit_text(text, parse_mode=ParseMode.HTML)

    elif response['status'] == 'error':
        update.message.reply_text(RESPONSE_TEXTS['error'])


def Inline_buttons(update: Update, context: CallbackContext):
    user = get_user_telegram_info_from_update(update, context)
    query = update.callback_query
    request = query.data.split()[0]
    request_id = query.data.split()[1]

    if request == 'course': 
        show_course_table(update, context)   
        query.answer(text="دریافت شد")