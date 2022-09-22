from telegram.ext import (Updater,
                          CommandHandler,
                          MessageHandler,
                          Filters,
                          CallbackContext,
                          CallbackQueryHandler,
                          ConversationHandler,)
from start import *
from const import *
from main_funcs import *
from course import *
from inline_buttons import *



def main():
    updater = Updater("5222043208:AAER54ZwJlJFF3oCezDK4Gb1z0TRCk3gSK8", use_context=True)
    dispatcher = updater.dispatcher

    # handlers
    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GET_USERPASS: [MessageHandler(Filters.text, get_userpass)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    static_data_import_db_handler = CommandHandler('static_data_import_db', static_data_import_db)
    crawl_teachers_info_handler = CommandHandler('crawl_teachers_info', crawl_teachers_info)

    call_back_query_handler = CallbackQueryHandler(Inline_buttons)

    # add handlers to dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(static_data_import_db_handler)
    dispatcher.add_handler(crawl_teachers_info_handler)
    dispatcher.add_handler(call_back_query_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()