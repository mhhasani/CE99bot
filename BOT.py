from calendar import c
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
board_member_id = {}
file_member_id = {}

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
}

members = {}
chat_ids = []


# Initialize root directory
MAIN_DIR_NAME = 'root'
current_dir = MAIN_DIR_NAME

board_id = -1  # Initialized By sending the /start command
CHANNEL_ID = "@CE99IUSTBOT"
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
                              callback_data='get_deadlines')],
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
        if 'DELETE' in query.split():
            cursor.execute('PRAGMA foreign_keys = ON;')
        cursor.execute(query, values)
        if is_select_query:
            rows = cursor.fetchall()
            return rows
    finally:
        conn.commit()
        cursor.close()


def courses_reply_markup(chat_id, show_courses=True, jozve=None, user=None):
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

    sql = "SELECT admin FROM Courses WHERE id = ?"
    # print(jozve)
    try:
        value = [int(jozve)]
        admin = do_sql_query2(sql, value, is_select_query=True)[0][0]
    except:
        pass

    keyboard = [
        [
            InlineKeyboardButton("🏠 Home", callback_data='LMS'),
            InlineKeyboardButton("همه کلاس ها",
                                 callback_data='all_courses')
        ],

        [InlineKeyboardButton("⏱ ددلاین ها و کوییز ها ⏱",
                              callback_data='get_deadlines')],
    ]
    if jozve != None:
        keyboard[0].append(InlineKeyboardButton("جزوه ها",
                                                callback_data='jozve ' + str(jozve)))

        if user in admin.split(','):
            keyboard.append(
                [InlineKeyboardButton(
                    "تغییر ددلاین", callback_data='edit_deadline ' + str(jozve)),
                 InlineKeyboardButton(
                    "افزودن ادمین", callback_data='set_admin ' + str(jozve))
                 ]
            )

    elif show_courses:
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


def all_courses(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    keyboard = []
    sql = "SELECT id,name FROM Courses"
    value = []
    courses = do_sql_query2(sql, value, is_select_query=True)
    for course in courses:
        keyboard.append([InlineKeyboardButton(
            course[1], callback_data='course '+str(course[0]))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.bot.send_message(chat_id=chat_id, text='همه دروس:',
                                    parse_mode=ParseMode.HTML, reply_markup=reply_markup)


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
    global board_member_id

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

        board_member_id[chat_id] = query.message.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                                                                       parse_mode=ParseMode.HTML, reply_markup=reply_markup).message_id

        query.message.bot.send_message(
            chat_id=CHANNEL_LOG, text=f'کاربر @{username} روی lms کلیک کرد.')
        # query.message.reply_text(
        #     text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        return ConversationHandler.END


def get_course(query, context: CallbackContext, update=None):
    global jozve_member_id
    global board_member_id

    if update != None:
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        user = update.message.from_user['username']
    else:
        chat_id = query.message.chat_id
        message_id = query.message.message_id
        user = query.from_user['username']

    sql = "SELECT * FROM Courses WHERE id = ?"
    if update != None:
        value = [jozve_member_id[chat_id]]
    else:
        value = [query.data.split()[1]]
    course = do_sql_query2(sql, value, is_select_query=True)[0]
    dead_line = get_deadline(course[0])

    text = ""
    link = 'https://lms.iust.ac.ir/mod/adobeconnect/view.php?id=' + \
        str(course[0])
    text += f"<a href='{link}'>{course[1]}</a>\n"
    days = course[3].split(',')
    for i in range(len(days)-2, -1, -1):
        text += days_dic[days[i]]+' ها'+'\n'
    text += 'ساعت ' + course[2] + '\n\n'

    if dead_line:
        text += "ددلاین ها و کوییز ها:\n\n"
        text += dead_line

    if update != None:
        try:
            update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_member_id[chat_id], text=text,
                                                 parse_mode=ParseMode.HTML, reply_markup=courses_reply_markup(chat_id, show_courses=False, jozve=str(course[0]), user=user))
        except:
            update.message.reply_text(text='ددلاین تغییری نکرد!')
            return False

        # query.message.bot.send_message(text=text, chat_id=chat_id)

    else:
        query.message.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text,
                                            parse_mode=ParseMode.HTML, reply_markup=courses_reply_markup(chat_id, show_courses=False, jozve=str(course[0]), user=user))
        # query.message.bot.send_message(text=text, chat_id=chat_id)
        board_member_id[chat_id] = query.message.bot.send_message(
            chat_id=CHANNEL_LOG, text=f'@{user}({chat_id}) get {course[1]}').message_id
        query.answer(text=course[1])
    return True


def jozve_board(id):
    """ Generate main page to display files and directories)"""
    id = int(id)

    sql = "SELECT parent,name FROM SubDirs WHERE id = ?"
    parent = do_sql_query2(sql, [id], is_select_query=True)

    if not parent:
        sql = "SELECT id, name FROM Courses WHERE id = ?"
        parent = do_sql_query2(sql, [id], is_select_query=True)

    sql = "SELECT id, name FROM SubDirs WHERE parent = ?"
    dirs = do_sql_query2(sql, [id], is_select_query=True)

    sql = "SELECT id, name FROM Files WHERE parent = ?"
    files = do_sql_query2(sql, [id], is_select_query=True)

    print(parent)
    borad_text = "💠 {0} \n\n".format(parent[0][1])
    # borad_text += "برای دریافت فایل ها آیدی فایل را تایپ کنید\n\n"
    num_files = 0
    num_dirs = 0
    for dir in dirs:
        borad_text += "📂 {0} \n\n".format(dir[1])
        num_dirs += 1
    for file in files:
        borad_text += "🗄 {0}-{1}\n\n".format(file[0], file[1])
        num_files += 1

    return borad_text+"💢 {0} Files , {1} Dirs".format(num_files, num_dirs)


def get_inline_jozve(id, user):
    """Return Inline Keyboard"""
    id = int(id)

    sql = "SELECT parent,name FROM SubDirs WHERE id = ?"
    parent = do_sql_query2(sql, [id], is_select_query=True)

    if not parent:
        sql = "SELECT id, name FROM Courses WHERE id = ?"
        parent = do_sql_query2(sql, [id], is_select_query=True)

    sql = "SELECT id, name FROM SubDirs WHERE parent = ?"
    dirs = do_sql_query2(sql, [id], is_select_query=True)

    parent = parent[0][0]

    # print(parent)

    try:
        parent = int(parent)
    except:
        parent = id

    keyboard = [
        [
            InlineKeyboardButton("🏠 Home", callback_data='LMS'),
            InlineKeyboardButton("همه کلاس ها", callback_data='all_courses'),
            InlineKeyboardButton(
                "🔙 Back", callback_data='jozve ' + str(parent)),
        ],
        [InlineKeyboardButton("دریافت همه فایل های پوشه",
                              callback_data='get_all ' + str(id))],
    ]

    Parent = parent

    while True:
        try:
            sql = "SELECT parent FROM SubDirs WHERE id = ?"
            parent = do_sql_query2(sql, [parent], is_select_query=True)[0][0]
        except:
            break

    sql = "SELECT admin FROM Courses WHERE id = ?"
    admin = do_sql_query2(sql, [parent], is_select_query=True)[0][0]

    for i in range(len(dirs)):
        if i % 2 == 0:
            keyboard.append([InlineKeyboardButton(
                "📂 {0}".format(dirs[i][1]), callback_data='jozve ' + str(dirs[i][0]))])
        else:
            c = len(keyboard) - 1
            keyboard[c].append(InlineKeyboardButton(
                "📂 {0}".format(dirs[i][1]), callback_data='jozve ' + str(dirs[i][0])))

    if user in admin.split(','):
        keyboard.append([
            InlineKeyboardButton(
                "افزودن پوشه", callback_data='add_dir ' + str(id)),
            InlineKeyboardButton(
                "افزودن فایل", callback_data='add_file ' + str(id)),
        ],)
        keyboard.append([
            InlineKeyboardButton(
                "حذف پوشه", callback_data='remove_dir ' + str(id)),
            InlineKeyboardButton(
                "حذف فایل", callback_data='remove_file ' + str(id)),
        ],)

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def LMS(update: Update, context: CallbackContext):
    global board_id
    global board_member_id
    global current_dir
    global chat_ids

    chat_id = update.message.chat_id
    user = update.message.from_user['username']

    update.message.bot.send_message(
        chat_id=CHANNEL_LOG, text=f'@{user} started bot!')

    add_user_to_chat_ids(chat_id)
    set_directory(update)

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

    welcome_text = 'به ربات CE99 خوش آمدید!\nبرای استفاده از امکانات ربات باید دروس خود را ثبت کنید.\nلطفا نام کاربری خود در سامانه lms را وارد کنید:\nدر صورت انصراف روی /cancel کلیک کنید.'

    if not user:
        sql = "INSERT INTO Users (chat_id) VALUES (?)"
        value = [chat_id]
        user = do_sql_query2(sql, value)
        update.message.reply_text(text=welcome_text)
        return 1
    elif not user[0][2]:
        update.message.reply_text(text=welcome_text)
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
        board_member_id[chat_id] = update.message.reply_text(
            text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup).message_id
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
    global board_member_id

    sql = "SELECT * FROM Courses"
    courses = do_sql_query2(sql, [], is_select_query=True)

    # for course in courses:
    #     id = course[0]
    #     name = course[1]
    #     sql = "INSERT INTO Directories (id,name) VALUES (?,?)"
    #     try:
    #         do_sql_query2(sql, [id, name])
    #     except:
    #         pass

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
                    board_member_id[chat_id] = update.message.bot.send_message(
                        chat_id=chat_id, text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup).message_id
            update.message.reply_text("lms database edited!")
        else:
            update.message.reply_text("lms database is already update!")


def start(update: Update, context: CallbackContext):

    global board_id
    global board_member_id
    global current_dir
    global chat_ids

    chat_id = update.message.chat_id
    user = update.message.from_user['username']

    update.message.bot.send_message(
        chat_id=CHANNEL_LOG, text=f'@{user} started bot!')

    add_user_to_chat_ids(chat_id)
    set_directory(update)

    board_member_id[chat_id] = update.message.reply_text(text=create_board(
        current_dir), parse_mode=ParseMode.HTML, reply_markup=get_inline_keyboard(current_dir)).message_id

    return ConversationHandler.END


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


def is_dir_exists(dir_name, parent):
    sql = "SELECT * FROM SubDirs WHERE name = ? AND parent = ?"
    values = [dir_name, int(parent)]
    dir = do_sql_query2(sql, values, is_select_query=True)
    return dir


def add_dir(update: Update, context: CallbackContext):
    """Create a new directory in the current directory when the command /mkdir is issued"""
    global jozve_member_id
    global board_member_id

    chat_id = update.message.chat_id
    new_dir_name = update.message.text
    parent = jozve_member_id[chat_id]
    user = update.message.from_user['username']

    if is_dir_exists(new_dir_name, parent):
        message = "directory has exist!"
        update.message.reply_text(text=message)
    else:
        sql = "SELECT id FROM SubDirs"
        values = []
        try:
            id = do_sql_query2(sql, values, is_select_query=True)[-1][0] + 1
        except:
            id = 1
        sql = "INSERT INTO SubDirs (id, parent, name) VALUES (?,?,?)"
        values = [id, parent, new_dir_name]
        do_sql_query2(sql, values)

        update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_member_id[chat_id], text=jozve_board(
            parent), parse_mode=ParseMode.HTML, reply_markup=get_inline_jozve(parent, user))

        message = "succesfully created!"
        update.message.reply_text(text=message)
    return ConversationHandler.END


def addfile(update: Update, context: CallbackContext):
    """Save the received file"""

    global CHANNEL_ID
    global file_member_id

    chat_id = update.message.chat_id
    message_id = update.message.message_id
    file_name = get_file_name(update)

    if file_name != -1:
        file_id = update.message.bot.forward_message(
            CHANNEL_ID, from_chat_id=chat_id, message_id=message_id).message_id
        file_member_id[chat_id] = [update, file_id, file_name]
        message_text = 'Please send file name or send /skip to set default or send /cancel.'
        update.message.reply_text(text=message_text)
        return 4
    else:
        return ConversationHandler.END


def get_filename(update: Update, context: CallbackContext):
    global board_member_id
    global file_member_id
    global jozve_member_id

    chat_id = update.message.chat_id
    parent = jozve_member_id[chat_id]
    command = update.message.text
    file_name = file_member_id[chat_id][2]
    file_id = file_member_id[chat_id][1]
    user = update.message.from_user['username']

    if command != "/skip":
        file_name = update.message.text
        file_member_id[chat_id][2] = file_name

    # message = ""
    # message += f"✅ یک فایل با آیدی {file_id} اضافه شد!\n"
    # message += "نام فایل: "
    # message += file_name + "\n"
    # message += "آدرس: "
    # message += parent

    # sql = "INSERT INTO Files (id, parent, name) VALUES (?,?,?)"
    # values = [file_id, parent, file_name]
    # do_sql_query2(sql, values)

    # if file_id != None:
    #     data = f'get {file_id}'
    #     keyboard = [[InlineKeyboardButton(
    #         "دریافت", callback_data=str(data))]]
    #     reply_markup = InlineKeyboardMarkup(keyboard)

    # update.message.reply_text(text=message, reply_markup=reply_markup)

    message_text = 'برای ارسال اطلاعیه اضافه شدن فایل روی کامند /yes و در غیر این صورت روی کامند /no  و در صورت انصراف روی /cancel کلیک کنید.'
    update.message.reply_text(text=message_text)

    return 5


def ADD_File_Log(update: Update, context: CallbackContext):
    global board_member_id
    global file_member_id
    global jozve_member_id
    global all_users_for_callback

    chat_id = update.message.chat_id
    parent = jozve_member_id[chat_id]
    Parent = jozve_member_id[chat_id]
    command = update.message.text
    file_name = file_member_id[chat_id][2]
    file_id = file_member_id[chat_id][1]
    user = update.message.from_user['username']

    message = ""
    message += f"✅ یک فایل با آیدی {file_id} اضافه شد!\n"
    message += "نام فایل: "
    message += file_name + "\n"
    message += "آدرس: "
    message += parent

    sql = "INSERT INTO Files (id, parent, name) VALUES (?,?,?)"
    values = [file_id, parent, file_name]
    do_sql_query2(sql, values)

    if not all_users_for_callback:
        sql = "SELECT chat_id, courses FROM Users WHERE status = ?"
        value = [4]
        all_users_for_callback = do_sql_query2(
            sql, value, is_select_query=True)

    while True:
        try:
            sql = "SELECT parent FROM SubDirs WHERE id = ?"
            parent = do_sql_query2(sql, [parent], is_select_query=True)[0][0]
        except:
            break

    sql = "SELECT id,name FROM Courses WHERE id = ?"
    course = do_sql_query2(sql, [parent], is_select_query=True)
    course_name = course[0][1]
    course_id = course[0][0]
    message += f'({course_name})'

    users = []
    if command == "/yes":
        for user in all_users_for_callback:
            if str(course_id) in user[1].split(","):
                users.append(user[0])
        send_to_all(update, message, file_id, users)

    elif command == "/no":
        update.message.reply_text(text=message)

    try:
        update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_member_id[chat_id], text=jozve_board(
            Parent), parse_mode=ParseMode.HTML, reply_markup=get_inline_jozve(Parent, user))
    except:
        pass

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


def change_dead_line_log(update: Update, dltext):
    message = f"✅ یک ددلاین ویرایش شد!"
    message += "\n"
    message += dltext
    send_to_all(update, message)


def send_to_all(update: Update, message, file_id=None, users=[]):
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
        if users:
            for id in users:
                try:
                    update.message.bot.send_message(
                        chat_id=id, text=message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
                except:
                    print(id)
        else:
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
    return True


def rename_dir_or_file(update: Update, context: CallbackContext):
    """Rename specific directory or file in the current directory when the command /rnd or /rnf is issued"""
    IsAdmin = is_admin(update)
    if not IsAdmin:
        return

    global current_dir
    global board_id
    global board_member_id

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
        update.message.bot.edit_message_text(chat_id=chat_id, message_id=board_member_id[chat_id], text=create_board(
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


def get_all_files(query):
    """Send specific file in the current directory when id is issued"""
    global CHANNEL_ID
    global CHANNEL_LOG
    chat_id = query.message.chat_id
    username = query.from_user['username']
    dir_id = query.data.split()[1]
    print(dir_id)
    sql = "SELECT id FROM Files WHERE parent = ?"
    values = [int(dir_id)]
    file_ids = do_sql_query2(sql, values, is_select_query=True)
    print(file_ids)
    c = 0
    for file_id in file_ids:
        # try:
        query.message.reply_copy(
            from_chat_id=CHANNEL_ID, message_id=file_id[0])
        c += 1
        # except:
        #     pass
    if c:
        query.message.bot.send_message(
            chat_id=CHANNEL_LOG, text=f'@{username}({chat_id}) get all files from {dir_id}')
    else:
        query.message.bot.send_message(
            chat_id=chat_id, text='فایلی در این پوشه وجود ندارد!')


def clear_illegal_commands(update: Update, context: CallbackContext):
    """Clears illegal messages and commands in chat"""
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    update.message.bot.delete_message(chat_id=chat_id, message_id=message_id)


def add_user_to_chat_ids(chat_id):
    global chat_ids
    if str(chat_id) not in chat_ids:
        chat_ids.append(str(chat_id))


def get_deadline(course_id):
    sql = "SELECT deadline FROM Courses WHERE id = ?"
    values = [int(course_id)]
    deadline = do_sql_query2(sql, values, is_select_query=True)
    try:
        return deadline[0][0]
    except:
        return None


def set_deadline(update: Update, context: CallbackContext):
    global jozve_member_id

    chat_id = update.message.chat_id
    course_id = jozve_member_id[chat_id]
    text = update.message.text
    if text == "/null":
        text = ''
    sql = "UPDATE Courses SET deadline = ? WHERE id = ?"
    values = [text, course_id]
    deadline = do_sql_query2(sql, values)
    text = 'برای ارسال اطلاعیه تغییر ددلاین روی کامند /yes و در غیر این صورت روی کامند /no  و در صورت انصراف روی /cancel کلیک کنید.'
    update.message.reply_text(text=text)
    return 13


def change_deadline_log(update: Update, context: CallbackContext):
    global jozve_member_id
    global all_users_for_callback

    chat_id = update.message.chat_id
    command = update.message.text

    sql = "SELECT * FROM Courses WHERE id = ?"
    value = [jozve_member_id[chat_id]]
    Course = do_sql_query2(sql, value, is_select_query=True)

    if not all_users_for_callback:
        sql = "SELECT chat_id, courses FROM Users WHERE status = ?"
        value = [4]
        all_users_for_callback = do_sql_query2(
            sql, value, is_select_query=True)

    if not get_course(update, context, update):
        return ConversationHandler.END

    sql = "SELECT name, deadline FROM Courses WHERE id = ?"
    value = [int(Course[0][0])]
    this_course = do_sql_query2(
        sql, value, is_select_query=True)[0]
    name = this_course[0].split('گروه')[0]
    text = f'✅ ددلاین درس {name} ویرایش شد!\n\n'
    text += this_course[1]
    keyboard = [[InlineKeyboardButton(
        f'{name}', callback_data='course '+str(Course[0][0]))]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if command == "/yes":
        for user in all_users_for_callback:
            for course in user[1].split(','):
                if course == str(Course[0][0]):
                    try:
                        update.message.bot.send_message(
                            chat_id=user[0], text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
                    except:
                        pass
    else:
        try:
            update.message.reply_text(
                text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        except:
            pass

    update.message.reply_text(text='ددلاین با موفقیت ویرایش شد!')

    update.message.bot.send_message(
        chat_id=CHANNEL_LOG, text=text, parse_mode=ParseMode.HTML)

    return ConversationHandler.END


def set_admin(update: Update, context: CallbackContext):
    global jozve_member_id
    chat_id = update.message.chat_id
    new_admin = update.message.text.split('@')[-1]

    sql = "SELECT admin FROM Courses WHERE id = ?"
    value = [jozve_member_id[chat_id]]
    admins = do_sql_query2(sql, value, is_select_query=True)[0][0]

    if new_admin in admins.split(','):
        update.message.reply_text(text=f"@{new_admin} is already admin!")
    else:
        sql = "UPDATE Courses SET admin = ? WHERE id = ?"
        value = [admins + ',' + new_admin, int(jozve_member_id[chat_id])]
        do_sql_query2(sql, value)
        update.message.reply_text(text=f"@{new_admin} is admin from now!")
    return ConversationHandler.END


def get_deadlines(update: Update, context: CallbackContext, query=None):
    global board_member_id

    if query:
        update = query
        user = update.from_user['username']
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        board_member_id[chat_id] = message_id
    else:
        user = update.message.from_user['username']
        chat_id = update.message.chat_id

    sql = "SELECT courses FROM Users WHERE chat_id = ?"
    value = [chat_id]
    courses = do_sql_query2(sql, value, is_select_query=True)

    if not courses or not courses[0][0]:
        sql = "SELECT * FROM Courses"
        courses = do_sql_query2(sql, [], is_select_query=True)
        text = ''
        for course in courses:
            if course[4]:
                text += '▫️' + course[1] + ':' + '\n'
                text += course[4] + '\n\n'
        try:
            update.message.bot.send_message(chat_id=chat_id, text=text)
            update.message.bot.send_message(
                chat_id=CHANNEL_LOG, text=f'@{user}({chat_id}) get deadline')
        except:
            if text:
                pass
            else:
                update.message.reply_text(text='ددلاینی وجود ندارد!')
        return

    courses = courses[0][0].split(',')
    text = ""
    for i in range(len(courses)-1):
        sql = "SELECT * FROM Courses WHERE id = ?"
        value = [courses[i]]
        course = do_sql_query2(sql, value, is_select_query=True)[0]
        if course[4]:
            text += '▫️' + course[1].split('گروه')[0] + ':' + '\n'
            text += course[4] + '\n\n'
    try:
        if query:
            reply_markup = courses_reply_markup(chat_id, show_courses=False)
            update.message.bot.edit_message_text(
                chat_id=chat_id, message_id=board_member_id[chat_id], text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        else:
            reply_markup = courses_reply_markup(chat_id, show_courses=False)
            message_id = update.message.bot.send_message(
                chat_id=chat_id, text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup).message_id
            board_member_id[chat_id] = message_id
    except:
        if text:
            pass
        else:
            update.message.reply_text(text='ددلاینی وجود ندارد!')

    update.message.bot.send_message(
        chat_id=CHANNEL_LOG, text=f'@{user}({chat_id}) get ددلاین')


def Inline_buttons(update: Update, context: CallbackContext):
    """Responses to buttons clicked in the inline keyboard"""
    global current_dir
    global jozve_member_id
    global board_member_id

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

    elif query.data.split()[0] == 'get_all':
        get_all_files(query)
        query.answer(text="دریافت شد")

    elif query.data == 'close':
        query.message.bot.delete_message(
            chat_id=chat_id, message_id=message_id)

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
                query.data.split()[1]), parse_mode=ParseMode.HTML, reply_markup=get_inline_jozve(query.data.split()[1], user))
        except:
            get_course(query, context)

        query.answer(text='جزوه ها')

    elif query.data.split()[0] == 'edit_deadline':
        global jozve_member_id
        global board_member_id

        board_member_id[chat_id] = message_id

        course_id = int(query.data.split()[1])
        jozve_member_id[chat_id] = course_id
        dead_line = get_deadline(course_id)
        try:
            query.message.reply_text(text=dead_line)
        except:
            pass
        query.message.reply_text(
            text='ددلاین ویرایش شده را ارسال کنید:\nبرای انصراف روی /cancel کلیک کنید.\nدر صورتی که قصد پاک کردن ددلاین را دارید روی /null کلیک کنید.')
        query.answer(text='تغییر ددلاین')
        return 11

    elif query.data.split()[0] == 'add_dir':
        board_member_id[chat_id] = query.message.message_id
        jozve_member_id[chat_id] = query.data.split()[1]
        query.message.reply_text(
            text='نام پوشه را وارد کنید:\nبرای انصراف روی /cancel کلیک کنید.')
        query.answer(text='افزودن پوشه')
        return 1

    elif query.data.split()[0] == 'remove_dir':
        course_id = int(query.data.split()[1])
        board_member_id[chat_id] = message_id

        sql = "SELECT id, name FROM SubDirs WHERE parent = ?"
        dirs = do_sql_query2(sql, [course_id], is_select_query=True)
        keyboard = []

        for i in range(len(dirs)):
            if i % 2 == 0:
                keyboard.append([InlineKeyboardButton(
                    "📂 {0}".format(dirs[i][1]), callback_data='remove_selected_dir ' + str(dirs[i][0]))])
            else:
                c = len(keyboard) - 1
                keyboard[c].append(InlineKeyboardButton(
                    "📂 {0}".format(dirs[i][1]), callback_data='remove_selected_dir ' + str(dirs[i][0])))

        reply_markup = InlineKeyboardMarkup(keyboard)
        if reply_markup["inline_keyboard"]:
            text = 'پوشه ای که قصد حذف آن را دارید انتخاب کنید:'
            query.message.reply_text(text=text, reply_markup=reply_markup)
        else:
            query.message.reply_text(text='پوشه ای وجود ندارد!')
        query.answer(text='حذف پوشه')

    elif query.data.split()[0] == 'remove_selected_dir':
        dir_id = int(query.data.split()[1])
        sql = "SELECT parent,name FROM SubDirs WHERE id = ?"
        parent = do_sql_query2(sql, [dir_id], is_select_query=True)

        if not parent:
            sql = "SELECT id, name FROM Courses WHERE id = ?"
            parent = do_sql_query2(sql, [dir_id], is_select_query=True)

        parent = parent[0][0]
        parent = str(parent)

        sql = "DELETE FROM SubDirs WHERE id = ?"
        dirs = do_sql_query2(sql, [dir_id])

        text = 'پوشه با موفقیت حذف شد!'
        query.message.bot.edit_message_text(
            text=text, message_id=message_id, chat_id=chat_id)
        query.message.bot.edit_message_text(chat_id=chat_id, message_id=board_member_id[chat_id], text=jozve_board(
            parent), parse_mode=ParseMode.HTML, reply_markup=get_inline_jozve(parent, user))
        query.answer(text='حذف پوشه')

    elif query.data.split()[0] == 'add_file':
        board_member_id[chat_id] = query.message.message_id
        jozve_member_id[chat_id] = query.data.split()[1]
        query.message.reply_text(
            text='فایل خود را ارسال کنید:\nبرای انصراف روی /cancel کلیک کنید.')
        query.answer(text='افزودن فایل')
        return 3

    elif query.data.split()[0] == 'remove_file':
        course_id = int(query.data.split()[1])

        sql = "SELECT id, name FROM Files WHERE parent = ?"
        files = do_sql_query2(sql, [course_id], is_select_query=True)
        keyboard = []

        for i in range(len(files)):
            if i % 2 == 0:
                keyboard.append([InlineKeyboardButton(
                    "📂 {0}".format(files[i][1]), callback_data='remove_selected_file ' + str(files[i][0]))])
            else:
                c = len(keyboard) - 1
                keyboard[c].append(InlineKeyboardButton(
                    "📂 {0}".format(files[i][1]), callback_data='remove_selected_file ' + str(files[i][0])))

        reply_markup = InlineKeyboardMarkup(keyboard)
        if reply_markup["inline_keyboard"]:
            text = 'فایلی که قصد حذف آن را دارید انتخاب کنید:'
            query.message.reply_text(text=text, reply_markup=reply_markup)
        else:
            query.message.reply_text(text='فایلی وجود ندارد!')
        query.answer(text='حذف فایل')

    elif query.data.split()[0] == 'remove_selected_file':
        course_id = int(query.data.split()[1])
        sql = "DELETE FROM Files WHERE id = ?"
        files = do_sql_query2(sql, [course_id], is_select_query=True)
        text = 'فایل با موفقیت حذف شد!'
        query.message.bot.edit_message_text(
            text=text, message_id=message_id, chat_id=chat_id)
        query.message.bot.edit_message_text(chat_id=chat_id, message_id=board_member_id[chat_id], text=jozve_board(
            jozve_member_id[chat_id]), parse_mode=ParseMode.HTML, reply_markup=get_inline_jozve(jozve_member_id[chat_id], user))
        query.answer(text='حذف فایل')

    elif query.data == "get_deadlines":
        get_deadlines(None, None, query)
        query.answer(text='ددلاین ها')

    elif query.data.split()[0] == 'set_admin':
        jozve_member_id[chat_id] = int(query.data.split()[1])
        query.message.reply_text(
            text="آیدی ادمین را وارد کنید:\nبرای انصراف روی /cancel کلیک کنید.")
        query.answer(text='ادمین')
        return 12

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
                    # context.bot.send_message(
                    #     chat_id=CHANNEL_LOG, text=text + f'\nارسال شده برای {user[0]}', parse_mode=ParseMode.HTML)
                    counter += 1
                except:
                    pass
    context.bot.send_message(
        chat_id=CHANNEL_LOG, text=f'تعداد {counter} اطلاعیه ارسال شد.', parse_mode=ParseMode.HTML)


def message(update: Update, context: CallbackContext):
    IsAdmin = is_admin(update)
    if not IsAdmin:
        return ConversationHandler.END

    message_text = 'Please send me your message or send /cancel .'
    update.message.reply_text(text=message_text)
    return 1


def main():
    updater = Updater(
        "5222043208:AAER54ZwJlJFF3oCezDK4Gb1z0TRCk3gSK8", use_context=True)

    dispatcher = updater.dispatcher
    j = updater.job_queue
    j.run_repeating(callback_minute, interval=1800, first=1380)

    LMS_handler = ConversationHandler(
        entry_points=[CommandHandler("start", LMS)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, get_username)],
            2: [MessageHandler(Filters.text & ~Filters.command, get_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(LMS_handler)

    dispatcher.add_handler(CommandHandler("rnf", rename_dir_or_file))
    dispatcher.add_handler(CommandHandler("rnd", rename_dir_or_file))
    dispatcher.add_handler(CommandHandler("update", get_and_set_id))
    dispatcher.add_handler(CommandHandler("all_courses", all_courses))
    dispatcher.add_handler(CommandHandler("deadline", get_deadlines))

    send_handler = ConversationHandler(
        entry_points=[CommandHandler('send', message)],
        states={
            1: [MessageHandler(Filters.all & ~Filters.command, send_to_all_user)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(send_handler)

    add_remove_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(Inline_buttons)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, add_dir)],
            2: [CallbackQueryHandler(Inline_buttons)],
            3: [MessageHandler(Filters.all & ~Filters.command & ~Filters.text, addfile)],
            4: [MessageHandler(Filters.text & ~Filters.command, get_filename),
                CommandHandler('skip', get_filename)],
            5: [CommandHandler('yes', ADD_File_Log),
                CommandHandler('no', ADD_File_Log)],
            11: [MessageHandler(Filters.text & ~Filters.command, set_deadline),
                 CommandHandler('null', set_deadline)],
            12: [MessageHandler(Filters.text & ~Filters.command, set_admin)],
            13: [CommandHandler('yes', change_deadline_log), CommandHandler('no', change_deadline_log)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(add_remove_handler)

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

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
