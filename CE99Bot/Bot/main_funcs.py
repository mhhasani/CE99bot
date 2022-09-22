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
    url = SERVER_URL + url + '/'
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



