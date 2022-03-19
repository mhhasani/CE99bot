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
import sqlite3
import re

admins = {
    "MHHasani": ["ALL", ['root'], 'root', None, [0]],
    "Sohrab_sajedi": ["TLA", ['root/term4/TLA', 'root/term4/Labs'], 'root', None, [0]],
    "VahidM313":  ["ALL", ['root'], 'root', None, [0]],
    "Zhra_Tabatabaee": ["etemadi", ['root/term4/algorithm/etemadi', 'root/term4/CA/hosseini'], 'root', None, [5, 7]],
    "As_de_Corazones": ["Labs", ['root/term4/Labs', 'root/term4/CA/beit', 'root/term4/Signals'], 'root', None, [4, 9, 8]],
}
members = {}
chat_ids = []
deadline_id = {
    'root/term4/TLA': 2,
    'root/term4/database': 3,
    'root/term4/CA/beit': 4,
    'root/term4/CA/hosseini': 5,
    'root/term4/algorithm/maleki': 6,
    'root/term4/algorithm/etemadi': 7,
    'root/term4/Signals': 8,
    'root/term4/Labs': 9,
}

# Initialize root directory
MAIN_DIR_NAME = 'root'
current_dir = MAIN_DIR_NAME

board_id = -1  # Initialized By sending the /start command
CHANNEL_ID = "@comp_elmos"
CHANNEL_LOG = "@log_ceiust99"
CHANNEL_CHAT_LOG = "@chat_log_ce"
CHANNEL_DEADLINE = "@deadline_ce99"
CHANNEL_NAGHD = "@naghd_CE99_bot"


def create_board(current_dir=current_dir):
    """ Generate main page to display files and directories)"""
    sql = "SELECT name, type, id FROM info WHERE parent = ?"
    rows = do_sql_query(sql, [current_dir], is_select_query=True)
    borad_text = "💠 {0} \n".format(current_dir)
    borad_text += "برای دریافت فایل ها آیدی فایل را تایپ کنید\n\n"
    num_files = 0
    num_dirs = 0
    for row in rows:
        if row[1] == 'dir':
            borad_text += "📂 {0} \n\n".format(row[0])
            num_dirs += 1
    for row in rows:
        if row[1] == 'file':
            borad_text += "🗄 {0}-{1}\n\n".format(row[2], row[0])
            num_files += 1

    return borad_text+"💢 {0} Files , {1} Dirs".format(num_files, num_dirs)


def get_inline_keyboard(current_dir=current_dir):
    """Return Inline Keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🏠 Home", callback_data='home_button'),
            # InlineKeyboardButton("❌ close", callback_data='close'),
            InlineKeyboardButton("🔙 Back", callback_data='back_button'),
        ],
        [InlineKeyboardButton("⏱ ددلاین ها و کوییز ها ⏱",
                              callback_data='deadline')],
        # [InlineKeyboardButton("👎 انتقادات و پیشنهادات 👍",
        #                       callback_data='naghd')]
    ]

    sql = "SELECT name, type, id FROM info WHERE parent = ?"
    rows = do_sql_query(sql, [current_dir], is_select_query=True)

    for i in range(len(rows)):
        if rows[i][1] == 'dir':
            if i % 2 == 0:
                keyboard.append([InlineKeyboardButton(
                    "📂 {0}".format(rows[i][0]), callback_data=current_dir+f"/{rows[i][0]}")])
            else:
                c = len(keyboard) - 1
                keyboard[c].append(InlineKeyboardButton(
                    "📂 {0}".format(rows[i][0]), callback_data=current_dir+f"/{rows[i][0]}"))

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def do_sql_query(query, values, is_select_query=False, has_regex=False):
    """ Connects to the database, executes the query, and returns results, if any.s
    Args:
        query(str): query to execute
        values(list): a list of parameters in the query
        is_select_query(boolean): Indicates whether the sent query is 'select query' or not
        has_regex(boolean): Indicates whether the sent query contains regex or not
    """
    try:
        conn = sqlite3.connect('Data.db')
        if has_regex:
            conn.create_function("REGEXP", 2, regexp)
        cursor = conn.cursor()
        cursor.execute(query, values)
        if is_select_query:
            rows = cursor.fetchall()
            return rows
    finally:
        conn.commit()
        cursor.close()


def get_and_set_id(update=None, context=None):
    global chat_ids
    sql = "SELECT id FROM ID"
    rows = do_sql_query(sql, [], is_select_query=True)
    ids = [str(row[0]) for row in rows]
    for id in ids:
        if str(id) not in chat_ids:
            chat_ids.append(id)

    sql = "INSERT INTO ID (id) VALUES (?)"
    for id in chat_ids:
        if str(id) not in ids:
            do_sql_query(sql, [str(id)])

    if update != None:
        update.message.reply_text("database edited!")


def start(update: Update, context: CallbackContext):

    global board_id
    global current_dir
    global chat_ids

    chat_id = update.message.chat_id
    user = update.message.from_user['username']

    update.message.bot.send_message(
        chat_id=CHANNEL_LOG, text=f'@{user} started bot!')

    add_user_to_chat_ids(chat_id)
    set_directory(update)

    board_id = update.message.reply_text(text=create_board(
        current_dir), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard(current_dir)).message_id

    return ConversationHandler.END


def remove_file(update: Update, context: CallbackContext):
    """Remove specific file in the current directory when the command /rm is issued"""
    global board_id
    global current_dir

    chat_id = update.message.chat_id
    message_text = update.message.text
    dir_names = message_text.split(" ")
    user = admins.get(update.message.from_user['username'])

    if not user:
        return

    if len(dir_names) >= 2:
        for i in range(1, len(dir_names)):

            sql = "SELECT parent FROM info WHERE type = 'file' AND id = ?"
            values = [dir_names[i]]
            address = do_sql_query(
                sql, values, is_select_query=True)[0][0]

            user_admin = user[1]
            for dir in user_admin:
                if address.find(dir) == 0:
                    current_dir = address
                    break
            else:
                continue

            sql = "DELETE FROM info WHERE type = 'file' AND id = ?"
            values = [dir_names[i]]
            do_sql_query(sql, values)

    update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(
        current_dir), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard(current_dir))


def regexp(regex, expression):
    """ Receives an expression and specifies if it matches the received regex or not
    Args:
        regex(str): sent regex
        expression(str): The expression sent to check if it matches the regex
    """
    try:
        return True if re.match(regex, expression) else False
    except Exception as e:
        return False


def remove_dir(update: Update, context: CallbackContext):
    """Remove specific directory in the current directory when the command /rmdir is issued"""
    IsAdmin = is_admin(update)
    if not IsAdmin:
        return

    global board_id
    global current_dir

    chat_id = update.message.chat_id
    message_text = update.message.text
    dir_name = message_text.split("-r")[1].strip() if len(message_text.split(
        "-r")) >= 2 else ' '.join(message_text.split(" ")[1:]).strip()

    if len(message_text.split("-r")) >= 2:
        sql = "DELETE FROM info WHERE name REGEXP ? AND parent = ? AND type = 'dir'"
        values = [dir_name, current_dir]
    else:
        sql = "DELETE FROM info WHERE name = ? AND parent = ? AND type = 'dir'"
        values = [dir_name, current_dir]

    do_sql_query(sql, values, has_regex=True)

    update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(
        current_dir), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard(current_dir))


def is_directory_exists(dir_name):
    """ Determines if the directory name sent exists in the current directory
    Args:
        dir_name(str): directory name
    """
    global current_dir

    sql = "SELECT COUNT(*) FROM info WHERE name = ? AND parent = ?"
    values = [dir_name, current_dir]
    count = do_sql_query(sql, values, is_select_query=True)[0]
    return True if int(count[0]) > 0 else False


def create_directory(update: Update, context: CallbackContext):
    """Create a new directory in the current directory when the command /mkdir is issued"""
    IsAdmin = is_admin(update)
    if not IsAdmin:
        return

    global current_dir
    global board_id

    chat_id = update.message.chat_id
    new_dir_name = ' '.join(update.message.text.split(' ')[1:])

    if is_directory_exists(new_dir_name):
        message = "directory has exist!"
        update.message.bot.send_message(chat_id=chat_id, text=message)
    else:
        sql = "INSERT INTO info (parent, name, type, id) VALUES (?,?,?,?)"
        values = [current_dir, new_dir_name, "dir", "null"]
        do_sql_query(sql, values)

        update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(
            current_dir), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard(current_dir))

        message = "succesfully created!"
        update.message.bot.send_message(chat_id=chat_id, text=message)


def get_file_name(update):
    if update.message.audio:
        return update.message.audio.file_name
    elif update.message.document:
        return update.message.document.file_name
    elif update.message.video:
        return update.message.video.file_name
    elif update.message.voice:
        return update.message.voice.file_unique_id
    elif update.message.photo:
        # The best quality of an image is selected when several different qualities are available
        return update.message.photo[len(update.message.photo)-1].file_unique_id
    else:
        return -1


def add_file(update: Update, context: CallbackContext):
    """Save the received file"""
    IsAdmin = is_admin(update, False)
    if not IsAdmin:
        return ConversationHandler.END

    global CHANNEL_ID

    chat_id = update.message.chat_id
    message_id = update.message.message_id
    user = admins.get(update.message.from_user['username'])
    file_name = get_file_name(update)

    if file_name != -1:
        file_id = update.message.bot.forward_message(
            CHANNEL_ID, from_chat_id=chat_id, message_id=message_id).message_id
        user[3] = [update, file_id, file_name]
        message_text = 'Please send file name or send /skip to set default or send /cancel.'
        update.message.reply_text(text=message_text)
        return 1
    else:
        return ConversationHandler.END


def getfilename(update: Update, context: CallbackContext):
    """Stores the selected gender and asks for a photo."""
    user = admins.get(update.message.from_user['username'])
    command = update.message.text[0:5]

    if command == "/skip":
        update = user[3][0]
        file_name = user[3][2]
    else:
        file_name = update.message.text
        user[3][2] = file_name
        update = user[3][0]

    message_text = 'برای ارسال اطلاعیه اضافه شدن فایل روی کامند /yes و در غیر این صورت روی کامند /no  و در صورت انصراف روی /cancel کلیک کنید.'
    update.message.reply_text(text=message_text)

    return 2


def add_file_log(update: Update, context: CallbackContext):
    user = admins.get(update.message.from_user['username'])
    current_dir = members.get(update.message.from_user['username'])
    chat_id = update.message.chat_id
    command = update.message.text
    update = user[3][0]
    file_name = user[3][2]
    file_id = user[3][1]

    message = ""
    message += f"✅ یک فایل با آیدی {file_id} اضافه شد!\n"
    message += "نام فایل: "
    message += file_name + "\n"
    message += "آدرس: "
    message += current_dir
    if command == "/yes":
        sql = "INSERT INTO info (parent, name, type, id) VALUES (?,?,?,?)"
        values = [current_dir, file_name, "file", str(file_id)]
        do_sql_query(sql, values)
        send_to_all(update, message, file_id)

    elif command == "/no":
        sql = "INSERT INTO info (parent, name, type, id) VALUES (?,?,?,?)"
        values = [current_dir, file_name, "file", str(file_id)]
        do_sql_query(sql, values)
        update.message.reply_text(text=message)
    try:
        update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(
            current_dir), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard(current_dir))
    except:
        pass
    return ConversationHandler.END


def change_dead_line_log(update: Update, dltext):
    message = f"✅ یک ددلاین ویرایش شد!"
    message += "\n"
    message += dltext
    send_to_all(update, message)


def send_to_all(update: Update, message, file_id=None):
    get_and_set_id()
    message_id = update.message.bot.send_message(
        chat_id=CHANNEL_CHAT_LOG, text=message).message_id

    if file_id != None:
        data = f'get {file_id}'
        keyboard = [[InlineKeyboardButton(
            "دریافت", callback_data=str(data))]]
        reply_markup = InlineKeyboardMarkup(keyboard)

    print(chat_ids)
    if file_id != None:
        for id in chat_ids:
            try:
                update.message.bot.send_message(
                    chat_id=id, text=message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
            except:
                print(id)
    else:
        for id in chat_ids:
            try:
                update.message.bot.copy_message(
                    chat_id=id, from_chat_id=CHANNEL_CHAT_LOG, message_id=message_id)
            except:
                print(id)
    update.message.reply_text(text='ended!')


def set_directory(update: Update):
    global current_dir
    user = update.message.from_user['username']
    current_dir = MAIN_DIR_NAME
    members[user] = MAIN_DIR_NAME


def message(update: Update, context: CallbackContext):
    """Stores the selected gender and asks for a photo."""
    IsAdmin = is_admin(update)
    if not IsAdmin:
        return ConversationHandler.END

    message_text = 'Please send me your message or send /cancel .'
    update.message.reply_text(text=message_text)
    return 1


def cancel(update: Update, context: CallbackContext):
    """Cancels and ends the conversation."""
    update.message.reply_text(text='ended!')
    return ConversationHandler.END


def send_to_all_user(update: Update, context: CallbackContext):
    get_and_set_id()
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    print(chat_ids)
    for id in chat_ids:
        try:
            update.message.bot.copy_message(
                chat_id=id, from_chat_id=chat_id, message_id=message_id)
        except:
            print(id)
    return cancel(update, context)


def is_admin(update: Update, have_message=True):
    global current_dir
    chat_id = update.message.chat_id
    is_group = update.message.chat.type != "private"
    user = admins.get(update.message.from_user['username'])
    current_dir = members.get(update.message.from_user['username'])

    if is_group:
        if have_message:
            message = "this command is not allowed in groups!"
            update.message.reply_text(text=message)
        return False

    try:
        user_base_dirs = user[1]
    except:
        if have_message:
            message = "you are not admin!"
            update.message.bot.send_message(chat_id=chat_id, text=message)
        return False

    for user_base_dir in user_base_dirs:
        if current_dir.find(user_base_dir) == 0:
            break
    else:
        message = "you are not admin's of this section!"
        update.message.reply_text(text=message)
        return False
    return True


def rename_dir_or_file(update: Update, context: CallbackContext):
    """Rename specific directory in the current directory when the command /rename is issued"""
    IsAdmin = is_admin(update)
    if not IsAdmin:
        return

    global current_dir
    global board_id

    chat_id = update.message.chat_id
    command = update.message.text[1:4]
    recieved_params = update.message.text[5:]
    old_name = recieved_params.split(",")[0]
    new_name = recieved_params.split(",")[1]
    current_dir = members.get(update.message.from_user['username'])

    if command == "rnd":
        sql = "SELECT parent, name FROM info"
        dirs = do_sql_query(sql, [], is_select_query=True)
        for dir in dirs:
            old_parent = current_dir + f"/{old_name}"
            if dir[0].find(old_parent) == 0:
                sql = "UPDATE info SET parent = ? WHERE parent = ?"
                values = [current_dir +
                          f"/{new_name}" + dir[0][len(old_parent):], dir[0]]
                do_sql_query(sql, values)
        sql = "UPDATE info SET name = ? WHERE type = 'dir' AND name = ? AND parent = ?"
        values = [new_name, old_name, current_dir]
        do_sql_query(sql, values)
        message = "succesfully changed!"
        update.message.bot.send_message(chat_id=chat_id, text=message)

    elif command == 'rnf':
        sql = "UPDATE info SET name = ? WHERE type = 'file' AND id = ?"
        values = [new_name, old_name]
        try:
            do_sql_query(sql, values)
            message = "succesfully changed!"
            update.message.bot.send_message(chat_id=chat_id, text=message)
        except:
            message = "error in database!"
            update.message.bot.send_message(chat_id=chat_id, text=message)

    try:
        update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=create_board(
            current_dir), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard(current_dir))
    except:
        pass


def get_files(update: Update, context: CallbackContext):
    """Send specific file in the current directory when the command /get is issued"""
    global CHANNEL_ID
    chat_id = update.message.chat_id
    message_text = str(update.message.text)
    username = update.message.from_user['username']
    is_group = update.message.chat.type != "private"

    add_user_to_chat_ids(chat_id)

    if message_text.isalnum():
        try:
            update.message.reply_copy(
                from_chat_id=CHANNEL_ID, message_id=message_text)
            update.message.bot.copy_message(
                chat_id=CHANNEL_LOG, from_chat_id=CHANNEL_ID, message_id=message_text,
                caption=f'@{username}({chat_id}) get {message_text}')
        except:
            pass

    if message_text == "ددلاین":
        if is_group:
            message = "مشاهده ددلاین ها در گروه مجاز نیست!"
            update.message.reply_text(text=message)
            return
        try:
            for address, id in deadline_id.items():
                update.message.bot.copy_message(
                    chat_id, from_chat_id=CHANNEL_DEADLINE, message_id=id)
            update.message.bot.send_message(
                chat_id=CHANNEL_LOG, text=f'@{username}({chat_id}) get ددلاین')
        except:
            pass

    # try:
    #     update.message.bot.forward_message(
    #         chat_id=CHANNEL_CHAT_LOG, from_chat_id=chat_id, message_id=message_id)
    # except:
    #     pass


def clear_illegal_commands(update: Update, context: CallbackContext):
    """Clears illegal messages and commands in chat"""
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    update.message.bot.delete_message(chat_id=chat_id, message_id=message_id)


def add_user_to_chat_ids(chat_id):
    global chat_ids
    if str(chat_id) not in chat_ids:
        chat_ids.append(str(chat_id))


def get_dead_line(dir):
    global deadline_id
    for address, id in deadline_id.items():
        if dir.find(address) == 0:
            return id
    return -1


def dead_line(update: Update, context: CallbackContext):
    IsAdmin = is_admin(update)
    if not IsAdmin:
        return

    global CHANNEL_DEADLINE

    chat_id = update.message.chat_id
    username = update.message.from_user['username']
    current_dir = members.get(username)

    dead_id = get_dead_line(current_dir)

    if dead_id != -1:
        update.message.bot.copy_message(
            chat_id=chat_id, from_chat_id=CHANNEL_DEADLINE, message_id=str(dead_id))
        message_text = 'Please send me new deadline or send /cancel.'
        update.message.reply_text(text=message_text)
        return 1
    else:
        message_text = 'this directory doesn\'t have deadline!'
        update.message.reply_text(text=message_text)
        return ConversationHandler.END


def edit_dead_line(update: Update, context: CallbackContext):
    IsAdmin = is_admin(update)
    if not IsAdmin:
        return ConversationHandler.END

    global CHANNEL_DEADLINE

    text = update.message.text
    username = update.message.from_user['username']
    current_dir = members.get(username)

    dead_id = get_dead_line(current_dir)

    if dead_id != -1:
        try:
            update.message.bot.edit_message_text(
                chat_id=CHANNEL_DEADLINE, message_id=str(dead_id), text=text)
            message_text = 'succesfully edited!'
            update.message.reply_text(text=message_text)
            change_dead_line_log(update, text)
        except:
            message_text = 'succesfully saved with no change!'
            update.message.reply_text(text=message_text)
        return ConversationHandler.END
    else:
        message_text = 'this directory doesn\'t have deadline!'
        update.message.reply_text(text=message_text)
        return ConversationHandler.END


def Inline_buttons(update: Update, context: CallbackContext):
    """Responses to buttons clicked in the inline keyboard"""
    global current_dir
    global deadline_id

    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    user = update.callback_query.from_user['username']
    is_group = query.message.chat.type != "private"

    add_user_to_chat_ids(chat_id)

    try:
        current_dir = members[user]
    except:
        members[user] = MAIN_DIR_NAME
        current_dir = members[user]

    if query.data == 'back_button':
        previous_dir = current_dir.rsplit('/', 1)[0]
        current_dir = previous_dir
        members[user] = current_dir
        try:
            update.callback_query.edit_message_text(text=create_board(
                current_dir), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard(current_dir))
        except:
            pass
        query.answer(text=current_dir)

    elif query.data == 'home_button':
        current_dir = MAIN_DIR_NAME
        members[user] = current_dir
        try:
            update.callback_query.edit_message_text(text=create_board(
                current_dir), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard(current_dir))
        except:
            pass
        query.answer(text=MAIN_DIR_NAME)

    elif query.data.split()[0] == 'get':
        id = query.data.split()[1]

        add_user_to_chat_ids(chat_id)

        if is_group:
            query.message.bot.copy_message(
                chat_id, from_chat_id=CHANNEL_ID, message_id=id, caption=f'@{user}')
        else:
            query.message.bot.copy_message(
                chat_id, from_chat_id=CHANNEL_ID, message_id=id)
        query.message.bot.copy_message(
            chat_id=CHANNEL_LOG, from_chat_id=CHANNEL_ID, message_id=id,
            caption=f'@{user}({chat_id}) get {id} with button!')
        query.answer(text="دریافت شد")

    elif query.data == 'close':
        query.message.bot.delete_message(
            chat_id=chat_id, message_id=message_id)

    elif query.data == 'naghd':
        message_text = 'لطفا انتقاد یا پیشنهاد خود را بنویسید یا در صورت انصراف روی /cancel کلیک کنید.'
        try:
            query.message.reply_text(text=message_text)
            query.answer(text="انتقادات و پیشنهادات")
            return 1
        except:
            pass

    elif query.data == 'deadline':
        if is_group:
            message = "مشاهده ددلاین ها در گروه مجاز نیست!"
            query.message.reply_text(text=message)
        else:
            try:
                for address, id in deadline_id.items():
                    query.message.bot.copy_message(
                        chat_id, from_chat_id=CHANNEL_DEADLINE, message_id=id)
                query.message.bot.send_message(
                    chat_id=CHANNEL_LOG, text=f'@{user}({chat_id}) get ددلاین')
            except:
                pass
        query.answer(text="ددلاین ها")

    else:
        current_dir = query.data
        members[user] = current_dir
        try:
            update.callback_query.edit_message_text(text=create_board(
                current_dir), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard(current_dir))
        except:
            pass
        query.answer(text=current_dir)


def send_naghd(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    username = update.message.from_user['username']

    try:
        update.message.bot.send_message(
            chat_id=CHANNEL_NAGHD, text=f"کاربر @{username} یک نقد ثبت کرد:")
        update.message.bot.copy_message(
            chat_id=CHANNEL_NAGHD, from_chat_id=chat_id, message_id=message_id)
        update.message.reply_text(text="پیام شما با موفقیت ارسال شد!")
    except:
        pass

    return ConversationHandler.END


def main():
    """Starts the bot"""
    # Create the Updater and pass it your bot's token.
    updater = Updater("5222043208:AAER54ZwJlJFF3oCezDK4Gb1z0TRCk3gSK8")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("mkdir", create_directory))
    dispatcher.add_handler(CommandHandler("rm", remove_file))
    dispatcher.add_handler(CommandHandler("rmdir", remove_dir))
    dispatcher.add_handler(CommandHandler("rnf", rename_dir_or_file))
    dispatcher.add_handler(CommandHandler("rnd", rename_dir_or_file))
    dispatcher.add_handler(CommandHandler("update", get_and_set_id))

    dead_line_handler = ConversationHandler(
        entry_points=[CommandHandler("deadline", dead_line)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, edit_dead_line)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(dead_line_handler)

    send_handler = ConversationHandler(
        entry_points=[CommandHandler('send', message)],
        states={
            1: [MessageHandler(Filters.all & ~Filters.command, send_to_all_user)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(send_handler)

    naghd_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(Inline_buttons)],
        states={
            1: [MessageHandler(Filters.all & ~Filters.command, send_naghd)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(naghd_handler)

    send_file_handler = ConversationHandler(
        entry_points=[MessageHandler(
            Filters.all & ~Filters.command & ~Filters.text, add_file)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, getfilename),
                CommandHandler('skip', getfilename)],
            2: [CommandHandler('yes', add_file_log),
                CommandHandler('no', add_file_log)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(send_file_handler)

    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, get_files))
    dispatcher.add_handler(CallbackQueryHandler(Inline_buttons))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
