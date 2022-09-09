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


def static_data_import_db(update: Update, context: CallbackContext):
    response = send_request('static_data_import_db', [])

    if response['status'] == 'OK':
        update.message.reply_text('OK')

    elif response['status'] == 'error':
        update.message.reply_text('Error')


def crawl_teachers_info(update: Update, context: CallbackContext):
    response = send_request('crawl_teachers_info', [])

    if response['status'] == 'OK':
        update.message.reply_text('OK')

    elif response['status'] == 'error':
        update.message.reply_text('Error')