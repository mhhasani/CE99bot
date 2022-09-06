from telegram.ext import (Updater,
                          CommandHandler,
                          MessageHandler,
                          Filters,
                          CallbackContext,
                          CallbackQueryHandler,
                          ConversationHandler,)
from start import *
from const import *

def cancel(update: Update, context: CallbackContext):
    """Cancels and ends the conversation."""
    update.message.reply_text(text='ended!')
    return ConversationHandler.END

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

    # add handlers to dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(static_data_import_db_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()