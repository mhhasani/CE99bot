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
from course import *
from main_funcs import *

def Inline_buttons(update: Update, context: CallbackContext):
    user = get_user_telegram_info_from_update(update, context)
    query = update.callback_query
    request = query.data.split()[0]
    request_id = query.data.split()[1]

    if request == 'course': 
        show_course_table(update, context)   
        query.answer(text="دریافت شد")

    elif request == 'directory':
        show_directory_table(update, context)
        query.answer(text="دریافت شد")