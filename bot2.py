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

from datetime import datetime, timedelta


all_courses_for_callback = None
all_users_for_callback = None

shanbe = 'شنبه'
yekshanbe = 'یکشنبه'
doshanbe = 'دوشنبه'
seshanbe = 'سه شنبه'
charshanbe = 'چهارشنبه'
panjshanbe = 'پنجشنبه'
jome = 'جمعه'

jozve_member_id = {}

days_dic = {
    '0': shanbe,
    '1': yekshanbe,
    '2': doshanbe,
    '3': seshanbe,
    '4': charshanbe,
    '5': panjshanbe,
    '6': jome,
}

Status = {
    0: 'null',
    1: 'waiting',
    2: 'wrong',
    3: 'correct',
    4: 'ended'
}

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


def create_database():
    sql_create_Courses_table = """ CREATE TABLE IF NOT EXISTS Courses (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        clock text,
                                        days text
                                    ); """
    sql_create_Users_table = """ CREATE TABLE IF NOT EXISTS Users (
                                        chat_id text PRIMARY KEY,
                                        username text,
                                        password text,
                                        id text,
                                        name text ,
                                        department text,
                                        courses text,
                                        status integer DEFAULT 0
                                    ); """
    do_sql_query2(sql_create_Courses_table, values=[])
    do_sql_query2(sql_create_Users_table, values=[])


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
            InlineKeyboardButton("LMS", callback_data='LMS'),
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


def do_sql_query2(query, values, is_select_query=False):
    try:
        conn = sqlite3.connect('Data_LMS.db')
        cursor = conn.cursor()
        cursor.execute(query, values)
        if is_select_query:
            rows = cursor.fetchall()
            return rows
    finally:
        conn.commit()
        cursor.close()


def do_sql_query3(query, values, is_select_query=False):
    try:
        conn = sqlite3.connect('jozve.db')
        cursor = conn.cursor()
        cursor.execute(query, values)
        if is_select_query:
            rows = cursor.fetchall()
            return rows
    finally:
        conn.commit()
        cursor.close()


def courses_reply_markup(chat_id, show_courses=True, jozve=None):
    sql = "SELECT courses FROM Users WHERE chat_id = ?"
    value = [chat_id]
    courses = do_sql_query2(sql, value, is_select_query=True)[
        0][0].split(',')
    my_courses = []
    for i in range(len(courses)-1):
        sql = "SELECT * FROM Courses WHERE id = ?"
        value = [courses[i]]
        course = do_sql_query2(sql, value, is_select_query=True)[0]
        my_courses.append(course)

    keyboard = [
        [
            InlineKeyboardButton("🏠 Home", callback_data='home_button'),
            InlineKeyboardButton("today", callback_data='LMS'),
        ],

        # [InlineKeyboardButton("⏱ ددلاین ها و کوییز ها ⏱",
        #                       callback_data='deadline')],
    ]
    if jozve != None:
        keyboard[0].append(InlineKeyboardButton("جزوه ها",
                                                callback_data='jozve ' + str(jozve)))

    keyboard.append([InlineKeyboardButton("همه کلاس ها",
                                          callback_data='all_courses')],)
    if show_courses:
        for i in range(len(my_courses)):
            if i % 2 == 0:
                keyboard.append([InlineKeyboardButton(my_courses[i][1].split('گروه')[
                                0], callback_data='course '+str(my_courses[i][0]))])
            else:
                c = len(keyboard) - 1
                keyboard[c].append(InlineKeyboardButton(my_courses[i][1].split('گروه')[
                    0], callback_data='course '+str(my_courses[i][0])))

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def courses_board(chat_id):
    date = datetime.now() + timedelta(hours=4.5)
    today = str((date.weekday()-5) % 7)

    sql = "SELECT courses FROM Users WHERE chat_id = ?"
    value = [chat_id]
    courses = do_sql_query2(sql, value, is_select_query=True)[
        0][0].split(',')
    my_courses = []
    for i in range(len(courses)-1):
        sql = "SELECT * FROM Courses WHERE id = ?"
        value = [courses[i]]
        course = do_sql_query2(sql, value, is_select_query=True)[0]
        my_courses.append(course)

    courses = "<b>🏫 کلاس های امروز 🏫</b>\n\n"
    c = 0
    for course in my_courses:
        if today in course[3].split(','):
            if c % 2:
                courses += "🔸"
            else:
                courses += "🔹"
            link = 'https://lms.iust.ac.ir/mod/adobeconnect/view.php?id=' + \
                str(course[0])
            courses += f"<a href='{link}'>{course[1].split('گروه')[0]}</a>ساعت {course[2]}\n\n"
            c += 1
    if c == 0:
        courses += "امروز کلاسی نداری:)"

    return courses


def get_courses(query, context: CallbackContext, show_courses=False):
    create_database()

    global board_id

    chat_id = query.message.chat_id
    message_id = query.message.message_id
    username = query.message.chat.username

    sql = "SELECT chat_id, username, password, id FROM Users WHERE chat_id = ?"
    value = [chat_id]
    user = do_sql_query2(sql, value, is_select_query=True)

    if not user:
        query.message.reply_text(
            text='اطلاعات شما در ربات ثبت نشده است.برای ثبت اطلاعات روی /lms کلیک کنید.')
        return
    elif not user[0][2]:
        query.message.reply_text(
            text='اطلاعات شما در ربات ثبت نشده است.برای ثبت اطلاعات روی /lms کلیک کنید.')
        return
    elif not user[0][3]:
        query.message.reply_text(
            text='فرایند بارگیری دیتا از lms مدتی طول می کشد.لطفا صبور باشید.\nدر صورتی که نام کاربری یا رمز عبور خود را اشتباه ثبت کرده اید روی /change کلیک کنید.')
        query.message.bot.send_message(
            chat_id=CHANNEL_LOG, text=f'کاربر @{username} منتظر دریافت اطلاعات دروس خود می باشد.')
        return ConversationHandler.END
    else:
        reply_markup = courses_reply_markup(chat_id, show_courses=show_courses)
        text = courses_board(chat_id)

        board_id = query.message.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                                                       parse_mode=ParseMode.HTML, reply_markup=reply_markup).message_id

        query.message.bot.send_message(
            chat_id=CHANNEL_LOG, text=f'کاربر @{username} روی lms کلیک کرد.')
        # query.message.reply_text(
        #     text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        return ConversationHandler.END


def get_course(query, context: CallbackContext):
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    user = query.from_user['username']

    sql = "SELECT * FROM Courses WHERE id = ?"
    value = [query.data.split()[1]]
    course = do_sql_query2(sql, value, is_select_query=True)[0]
    text = ""
    link = 'https://lms.iust.ac.ir/mod/adobeconnect/view.php?id=' + \
        str(course[0])
    text += f"<a href='{link}'>{course[1]}</a>\n"
    days = course[3].split(',')
    for i in range(len(days)-2, -1, -1):
        text += days_dic[days[i]]+' ها'+'\n'
    text += 'ساعت ' + course[2] + '\n'
    query.message.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                                        parse_mode=ParseMode.HTML, reply_markup=courses_reply_markup(chat_id, show_courses=False, jozve=str(course[0])))
    # query.message.bot.send_message(text=text, chat_id=chat_id)
    board_id = query.message.bot.send_message(
        chat_id=CHANNEL_LOG, text=f'@{user}({chat_id}) get {course[1]}').message_id
    query.answer(text=course[1])


def jozve_board(id):
    """ Generate main page to display files and directories)"""
    id = int(id)

    sql = "SELECT * FROM Directories WHERE id = ?"
    parent = do_sql_query3(sql, [id], is_select_query=True)

    if not parent:
        sql = "SELECT * FROM SubDirs WHERE id = ?"
        parent = do_sql_query3(sql, [id], is_select_query=True)

    sql = "SELECT * FROM SubDirs WHERE parent = ?"
    dirs = do_sql_query3(sql, [id], is_select_query=True)

    if not dirs:
        sql = "SELECT * FROM Directories WHERE parent = ?"
        dirs = do_sql_query3(sql, [id], is_select_query=True)

    sql = "SELECT * FROM Files WHERE parent = ?"
    files = do_sql_query3(sql, [id], is_select_query=True)

    borad_text = "💠 {0} \n\n".format(parent[0][2])
    # borad_text += "برای دریافت فایل ها آیدی فایل را تایپ کنید\n\n"
    num_files = 0
    num_dirs = 0
    for dir in dirs:
        borad_text += "📂 {0} \n\n".format(dir[2])
        num_dirs += 1
    for file in files:
        borad_text += "🗄 {0}-{1}\n\n".format(file[0], file[2])
        num_files += 1

    return borad_text+"💢 {0} Files , {1} Dirs".format(num_files, num_dirs)


def get_inline_jozve(id):
    """Return Inline Keyboard"""
    id = int(id)

    sql = "SELECT * FROM Directories WHERE parent = ?"
    dirs = do_sql_query3(sql, [id], is_select_query=True)

    if not dirs:
        sql = "SELECT * FROM SubDirs WHERE parent = ?"
        dirs = do_sql_query3(sql, [id], is_select_query=True)

    sql = "SELECT parent FROM SubDirs WHERE id = ?"
    parent = do_sql_query3(sql, [id], is_select_query=True)

    if not parent:
        sql = "SELECT parent FROM Directories WHERE id = ?"
        parent = do_sql_query3(sql, [id], is_select_query=True)
    parent = parent[0][0]
    print(parent)

    try:
        parent = int(parent)
    except:
        parent = id

    keyboard = [
        [
            InlineKeyboardButton("🏠 Home", callback_data='home_button'),
            InlineKeyboardButton("today", callback_data='LMS'),
            InlineKeyboardButton(
                "🔙 Back", callback_data='jozve ' + str(parent)),
        ],
        [
            InlineKeyboardButton("همه کلاس ها", callback_data='all_courses'),
            # InlineKeyboardButton(
            #     "جزوه ها", callback_data='jozve ' + str(id)),
        ],
        # [InlineKeyboardButton("⏱ ددلاین ها و کوییز ها ⏱",
        #                       callback_data='deadline')],
        [
            InlineKeyboardButton(
                "افزودن پوشه", callback_data='add_dir ' + str(id)),
            InlineKeyboardButton(
                "افزودن فایل", callback_data='add_file ' + str(id)),
        ],
    ]

    for i in range(len(dirs)):
        if i % 2 == 0:
            keyboard.append([InlineKeyboardButton(
                "📂 {0}".format(dirs[i][2]), callback_data='jozve ' + str(dirs[i][0]))])
        else:
            c = len(keyboard) - 1
            keyboard[c].append(InlineKeyboardButton(
                "📂 {0}".format(dirs[i][2]), callback_data='jozve ' + str(dirs[i][0])))

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def LMS(update: Update, context: CallbackContext):
    global board_id
    is_group = update.message.chat.type != "private"
    username = update.message.chat.username

    if is_group:
        message = "مشاهده دروس شما در گروه ها امکان پذیر نمی باشد."
        update.message.reply_text(text=message)
        return ConversationHandler.END

    create_database()

    chat_id = update.message.chat_id
    sql = "SELECT chat_id, username, password, id FROM Users WHERE chat_id = ?"
    value = [chat_id]
    user = do_sql_query2(sql, value, is_select_query=True)

    if not user:
        sql = "INSERT INTO Users (chat_id) VALUES (?)"
        value = [chat_id]
        user = do_sql_query2(sql, value)
        update.message.reply_text(
            text='لطفا نام کاربری خود در سامانه lms را وارد کنید:' +
            '\n در صورت انصراف روی /cancel کلیک کنید.')
        return 1
    elif not user[0][2]:
        update.message.reply_text(
            text='لطفا نام کاربری خود در سامانه lms را وارد کنید:' +
            '\n در صورت انصراف روی /cancel کلیک کنید.')
        return 1
    elif not user[0][3]:
        update.message.reply_text(
            text='فرایند بارگیری دیتا از lms مدتی طول می کشد.لطفا صبور باشید.\nدر صورتی که نام کاربری یا رمز عبور خود را اشتباه ثبت کرده اید روی /change کلیک کنید.')
        update.message.bot.send_message(
            chat_id=CHANNEL_LOG, text=f'کاربر @{username} منتظر دریافت اطلاعات دروس خود می باشد.')
        return ConversationHandler.END
    else:
        reply_markup = courses_reply_markup(chat_id, show_courses=False)
        text = courses_board(chat_id)
        board_id = update.message.reply_text(
            text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup).message_id
        update.message.bot.send_message(
            chat_id=CHANNEL_LOG, text=f'کاربر @{username} روی /lms کلیک کرد.')
        return ConversationHandler.END


def change(update: Update, context: CallbackContext):
    is_group = update.message.chat.type != "private"

    if is_group:
        message = "تغییر نام کاربری و رمز عبور برای گروه تعریف نشده است!"
        update.message.reply_text(text=message)
        return ConversationHandler.END

    chat_id = update.message.chat_id
    sql = "DELETE FROM Users WHERE chat_id = ?"
    value = [chat_id]
    do_sql_query2(sql, value, is_select_query=True)

    sql = "INSERT INTO Users (chat_id) VALUES (?)"
    value = [chat_id]
    do_sql_query2(sql, value)
    update.message.reply_text(
        text='لطفا نام کاربری خود در سامانه lms را وارد کنید:' +
        '\n در صورت انصراف روی /cancel کلیک کنید.')
    return 1


def get_username(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    sql = 'UPDATE Users SET username = ? WHERE chat_id = ?'
    value = [text, chat_id]
    user = do_sql_query2(sql, value)
    update.message.reply_text(
        text='لطفا رمز عبور خود در سامانه lms را وارد کنید:' +
        '\n در صورت انصراف روی /cancel کلیک کنید.')
    return 2


def get_password(update: Update, context: CallbackContext):
    user = update.message.from_user['username']
    chat_id = update.message.chat_id

    text = update.message.text
    sql = 'UPDATE Users SET password = ? , status = ? WHERE chat_id = ?'
    value = [text, 1, chat_id]
    do_sql_query2(sql, value)
    update.message.reply_text(
        text='فرایند بارگیری دیتا از lms مدتی طول می کشد.لطفا صبور باشید.\nدر صورتی که نام کاربری یا رمز عبور خود را اشتباه ثبت کرده اید روی /change کلیک کنید.')
    update.message.bot.send_message(
        chat_id=CHANNEL_LOG, text=f'کاربر @{user} اطلاعات lms خود را ثبت کرد.')
    return ConversationHandler.END


def get_and_set_id(update=None, context=None):
    global chat_ids
    global board_id

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

        sql = "SELECT chat_id, status FROM Users WHERE status = ? OR status = ?"
        value = [2, 3]
        users = do_sql_query2(sql, value, is_select_query=True)
        if users:
            for user in users:
                chat_id = user[0]
                status = user[1]
                if Status[status] == 'wrong':
                    sql = "DELETE FROM Users WHERE chat_id = ?"
                    value = [chat_id]
                    do_sql_query2(sql, value, is_select_query=True)
                    text = "❌ نام کاربری یا رمز عبور شما اشتباه است!\nبرای اصلاح روی /lms کلیک کنید."
                    update.message.bot.send_message(
                        chat_id=chat_id, text=text)
                elif Status[status] == 'correct':
                    sql = 'UPDATE Users SET status = ? WHERE chat_id = ?'
                    value = [4, chat_id]
                    do_sql_query2(sql, value)
                    text = "✅ اطلاعات کلاس های شما با موفقیت از سامانه LMS دریافت شد!\nبرای تغییر نام کاربری و رمز عبور خود در سامانه می توانید روی "
                    text += f"<a href='https://its.iust.ac.ir/user/password'>لینک</a>"
                    text += " کلیک کنید."
                    update.message.bot.send_message(
                        chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)

                    reply_markup = courses_reply_markup(
                        chat_id, show_courses=False)

                    text = courses_board(chat_id)
                    board_id = update.message.bot.send_message(
                        chat_id=chat_id, text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup).message_id
            update.message.reply_text("lms database edited!")
        else:
            update.message.reply_text("lms database is already update!")


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


def is_dir_exists(dir_name, parent):
    sql = "SELECT * FROM Directories WHERE name = ? AND parent = ?"
    values = [dir_name, int(parent)]
    dir = do_sql_query3(sql, values, is_select_query=True)
    return dir


def add_dir(update: Update, context: CallbackContext):
    """Create a new directory in the current directory when the command /mkdir is issued"""
    global jozve_member_id

    chat_id = update.message.chat_id
    new_dir_name = update.message.text
    parent = jozve_member_id[chat_id]

    if is_dir_exists(new_dir_name, parent):
        message = "directory has exist!"
        update.message.reply_text(text=message)
    else:
        sql = "SELECT id FROM SubDirs"
        values = []
        try:
            id = do_sql_query3(sql, values, is_select_query=True)[-1][0] + 1
        except:
            id = 1
        sql = "INSERT INTO SubDirs (id, parent, name) VALUES (?,?,?)"
        values = [id, parent, new_dir_name]
        do_sql_query3(sql, values)

        update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_id, text=jozve_board(
            parent), parse_mode=ParseMode.HTML, reply_markup=get_inline_jozve(parent))

        message = "succesfully created!"
        update.message.reply_text(text=message)
    return ConversationHandler.END


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
    """Rename specific directory or file in the current directory when the command /rnd or /rnf is issued"""
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
    """Send specific file in the current directory when id is issued"""
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
    try:
        IsAdmin = is_admin(update)
        if not IsAdmin:
            return
    except:
        update.message.reply_text(text='ابتدا ربات را استارت کنید.')
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
    global jozve_member_id
    global board_id

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

    elif query.data == 'back_lms':
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

    # elif query.data == 'naghd':
    #     message_text = 'لطفا انتقاد یا پیشنهاد خود را بنویسید یا در صورت انصراف روی /cancel کلیک کنید.'
    #     try:
    #         query.message.reply_text(text=message_text)
    #         query.answer(text="انتقادات و پیشنهادات")
    #         return 1
    #     except:
    #         pass

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

    elif query.data == 'LMS':
        if is_group:
            message = "مشاهده دروس شما در گروه ها امکان پذیر نمی باشد."
            query.message.reply_text(text=message)
        else:
            try:
                get_courses(query, context, show_courses=False)
            except:
                pass
        query.answer(text="LMS")

    elif query.data == 'all_courses':
        if is_group:
            message = "مشاهده دروس شما در گروه ها امکان پذیر نمی باشد."
            query.message.reply_text(text=message)
        else:
            try:
                get_courses(query, context, show_courses=True)
            except:
                pass
        query.answer(text="LMS")

    elif query.data.split()[0] == 'course':
        get_course(query, context)

    elif query.data.split()[0] == 'jozve':
        try:
            update.callback_query.edit_message_text(text=jozve_board(
                query.data.split()[1]), parse_mode=ParseMode.HTML, reply_markup=get_inline_jozve(query.data.split()[1]))
        except:
            get_course(query, context)

        query.answer(text='جزوه ها')

    elif query.data.split()[0] == 'add_dir':
        board_id = query.message.message_id
        jozve_member_id[chat_id] = query.data.split()[1]
        query.message.reply_text(text='نام پوشه را وارد کنید:')
        query.answer(text='افزودن فایل')
        return 1

    else:
        current_dir = query.data
        members[user] = current_dir
        try:
            update.callback_query.edit_message_text(text=create_board(
                current_dir), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard(current_dir))
        except:
            pass
        query.answer(text=current_dir)

    return ConversationHandler.END


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


def is_online(clock, now):
    clock = clock.split(':')
    hour = clock[0]
    minute = clock[1]
    res1 = int(hour)*60 + int(minute)
    now = now.split(':')
    hour = now[0]
    minute = now[1]
    res2 = int(hour)*60 + int(minute)
    return res1 >= res2 and res1-res2 <= 30


def callback_minute(context: CallbackContext):
    global all_courses_for_callback
    global all_users_for_callback

    from datetime import datetime
    now = datetime.now() + timedelta(hours=4.5)
    today = str((now.weekday()-5) % 7)
    now = now.strftime("%H:%M")

    now_course = []

    if not all_courses_for_callback:
        sql = "SELECT * FROM Courses"
        all_courses_for_callback = do_sql_query2(sql, [], is_select_query=True)

    for course in all_courses_for_callback:
        if today in course[3].split(','):
            if is_online(course[2], now):
                now_course.append(str(course[0]))

    if not all_users_for_callback:
        sql = "SELECT chat_id, courses FROM Users WHERE status = ?"
        value = [4]
        all_users_for_callback = do_sql_query2(
            sql, value, is_select_query=True)

    counter = 0

    for user in all_users_for_callback:
        for course in user[1].split(','):
            if course in now_course:
                sql = "SELECT name, clock FROM Courses WHERE id = ?"
                value = [int(course)]
                this_course = do_sql_query2(
                    sql, value, is_select_query=True)[0]
                name = this_course[0].split('گروه')[0]
                clock = this_course[1]
                text = '❌ کلاس "{}" ساعت {} برگزار خواهد شد.'.format(
                    f'<b>{name}</b>', clock)
                keyboard = [[InlineKeyboardButton(
                    f'لینک کلاس {name}', callback_data='course '+str(course))]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                try:
                    context.bot.send_message(
                        chat_id=user[0], text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
                    context.bot.send_message(
                        chat_id=CHANNEL_LOG, text=text + f'\nارسال شده برای {user[0]}', parse_mode=ParseMode.HTML)
                    counter += 1
                except:
                    pass
    context.bot.send_message(
        chat_id=CHANNEL_LOG, text=f'تعداد {counter} اطلاعیه ارسال شد.', parse_mode=ParseMode.HTML)


def main():
    """Starts the bot"""
    # Create the Updater and pass it your bot's token.
    updater = Updater(
        "5222043208:AAER54ZwJlJFF3oCezDK4Gb1z0TRCk3gSK8", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    j = updater.job_queue
    j.run_repeating(callback_minute, interval=1200, first=1200)

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

    # naghd_handler = ConversationHandler(
    #     entry_points=[CallbackQueryHandler(Inline_buttons)],
    #     states={
    #         1: [MessageHandler(Filters.all & ~Filters.command, send_naghd)],
    #     },
    #     fallbacks=[CommandHandler('cancel', cancel)]
    # )

    # dispatcher.add_handler(naghd_handler)

    add_remove_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(Inline_buttons)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, add_dir)],
            2: [CallbackQueryHandler(Inline_buttons)],
            # 3: [MessageHandler(Filters.all & ~Filters.command & ~Filters.text, add_file)],
            # 4: [MessageHandler(~Filters.command & Filters.text, rm_file)],
            # 11: [MessageHandler(~Filters.command & Filters.text, get_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(add_remove_handler)

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

    LMS_handler = ConversationHandler(
        entry_points=[CommandHandler("lms", LMS)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, get_username)],
            2: [MessageHandler(Filters.text & ~Filters.command, get_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(LMS_handler)

    change_handler = ConversationHandler(
        entry_points=[CommandHandler("change", change)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, get_username)],
            2: [MessageHandler(Filters.text & ~Filters.command, get_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(change_handler)

    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, get_files))

    # dispatcher.add_handler(CallbackQueryHandler(Inline_buttons))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
