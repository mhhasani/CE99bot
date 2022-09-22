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
from main_funcs import *


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


def create_course_table_reply_markup(course_info):
    keyboard = []
    main_dir = course_info['main_dir']
    callback_data=CALLBACK_DATA['directory'] + ' ' + main_dir
    text = 'جزوه ها'
    keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])

    return InlineKeyboardMarkup(keyboard)


def show_course_table(update: Update, context: CallbackContext):
    user = get_user_telegram_info_from_update(update, context)
    if user['is_callback']:
        update = update.callback_query
    course_id = update.data.split()[1]
    response = send_request('show_course_table', [course_id])
    if response['status'] == 'OK':
        course_info = response['course_info']
        text = create_course_table_text(course_info)
        reply_markup = create_course_table_reply_markup(course_info)
        update.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    elif response['status'] == 'error':
        update.message.reply_text(RESPONSE_TEXTS['error'])


def create_directory_table_text(directory_info):
    dir_name = directory_info['dir_name']
    sub_dirs = directory_info['sub_dirs']
    files = directory_info['files']

    text = f"💠 {dir_name} \n\n"
    for dir in sub_dirs:
        text += "📂 {0} \n\n".format(dir['name'])
    for file in files:
        file_link = '<a href="{0}">{1}</a>'.format('/file_' + file['telegram_id'], file['name'])
        text += "🗄 {0}\n\n".format(file_link)
    text += f"💢 {len(files)} Files , {len(sub_dirs)} Dirs"

    return text


def create_directory_table_reply_markup(directory_info):
    keyboard = []
    parent_id = directory_info['parent_id']
    if parent_id:
        callback_data=CALLBACK_DATA['directory'] + ' ' + parent_id
        text = 'بازگشت به پوشه قبلی'
        keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])

    c = 0
    bottom2 = []
    for dir in directory_info['sub_dirs']:
        if len(bottom2) == 2:
            keyboard.append(bottom2)
            bottom2 = []
        callback_data=CALLBACK_DATA['directory'] + ' ' + dir['id']
        text = dir['name']
        bottom2.append(InlineKeyboardButton(text, callback_data=callback_data))
        c += 1
        
    return InlineKeyboardMarkup(keyboard)


def show_directory_table(update: Update, context: CallbackContext):
    user = get_user_telegram_info_from_update(update, context)
    if user['is_callback']:
        update = update.callback_query
    dir_id = update.data.split()[1]
    response = send_request('show_directory_table', [dir_id])
    if response['status'] == 'OK':
        directory_info = response
        text = create_directory_table_text(directory_info)
        reply_markup = create_directory_table_reply_markup(directory_info)
        update.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    elif response['status'] == 'error':
        update.message.reply_text(RESPONSE_TEXTS['error'])
