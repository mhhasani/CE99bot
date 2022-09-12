from curses.panel import bottom_panel
from datetime import datetime, timedelta
from email import message
import json
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
from main_funcs import *



    
def start(update: Update, context: CallbackContext):
    user = get_user_telegram_info_from_update(update, context)
    response = send_request('start_bot', [user['chat_id'], user['username']])

    if response['status'] == 'authenticated':
        ConversationHandler.END
        return show_main_table(update, context)

    elif response['status'] in ['not_authenticated', 'created']:
        update.message.reply_text(RESPONSE_TEXTS['welcom'])
        update.message.reply_text(RESPONSE_TEXTS['get_userpass'])
        return GET_USERPASS

    else:
        update.message.reply_text(RESPONSE_TEXTS['error'])
        
    return ConversationHandler.END

def get_userpass(update: Update, context: CallbackContext):
    user = get_user_telegram_info_from_update(update, context)
    message = update.message.text
    if len(message.split()) != 2:
        update.message.reply_text(RESPONSE_TEXTS['get_userpass'])
        return GET_USERPASS
        
    lms_username = message.split('\n')[0]
    lms_password = message.split('\n')[1]
    response = send_request('get_userpass', [user['chat_id'], lms_username, lms_password])

    if response['status'] == 'error':
        update.message.reply_text(RESPONSE_TEXTS['lms_error'])
    
    elif response['status'] == 'correct':
        response = send_request('update_status', [user['chat_id']])
        if response['status'] == 'OK':
            update.message.reply_text(RESPONSE_TEXTS['correct_userpass'], parse_mode=ParseMode.HTML)
            return show_main_table(update, context)
        else:
            update.message.reply_text(RESPONSE_TEXTS['error'])


    elif response['status'] == 'wrong':
        response = send_request('update_status', [user['chat_id']])
        if response['status'] == 'OK':
            update.message.reply_text(RESPONSE_TEXTS['incorrect_userpass'])
        else:
            update.message.reply_text(RESPONSE_TEXTS['error'])

    else:
        update.message.reply_text(RESPONSE_TEXTS['error'])

    return ConversationHandler.END


    