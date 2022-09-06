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

import requests
from const import *

base_url = 'http://127.0.0.1:8000/telegram/'

def send_request(url, options):
    url = base_url + url + '/'
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

    
def start(update: Update, context: CallbackContext):
    user = get_user_telegram_info_from_update(update, context)
    response = send_request('start_bot', [user['chat_id']])
    if response['status'] == 'authenticated':
        update.message.reply_text(f"Welcome {user['first_name']} {user['last_name']}!")
    elif response['status'] in ['not_authenticated', 'created']:
        update.message.reply_text(f"Welcome {user['first_name']} {user['last_name']}!")
        update.message.reply_text(f"Please enter your student number and password to authenticate yourself.")
        return GET_USERPASS
    else:
        update.message.reply_text('Error')
    ConversationHandler.END

def get_userpass(update: Update, context: CallbackContext):
    user = get_user_telegram_info_from_update(update, context)
    lms_username = update.message.text.split('\n')[0]
    lms_password = update.message.text.split('\n')[1]
    response = send_request('get_userpass', [user['chat_id'], lms_username, lms_password])

    if response['status'] == 'OK':
        update.message.reply_text('OK')
        ConversationHandler.END
    elif response['status'] == 'error':
        update.message.reply_text('Error')
        return GET_USERPASS

def static_data_import_db(update: Update, context: CallbackContext):
    response = send_request('static_data_import_db', [])
    if response['status'] == 'OK':
        update.message.reply_text('OK')
    elif response['status'] == 'error':
        update.message.reply_text('Error')
    