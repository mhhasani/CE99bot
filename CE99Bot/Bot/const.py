GET_USERPASS = 'get_userpass'

SERVER_UEL = 'http://127.0.0.1:8000/telegram/'
BASE_VIEW_LINK = "https://lms.iust.ac.ir/course/view.php?id="

RESPONSE_TEXTS = {
    'error': 'مشکلی پیش اومده...',
    'welcom': 'سلام دوست عزیز :)\nخیلی خوش اومدی 🌺\n\nبرای این که بتونیم ربات رو برای شما شخصی سازی کنیم نیاز داریم که اطلاعات دروس شما رو از سامانه lms استخراج کنیم.\n\nاین رو هم بگیم که اطلاعات شما محرمانه خواهد ماند و بعد از استخراج می توانید برای تغییر رمز عبور خود در سامانه lms اقدام کنین.',
    'get_userpass': 'لطفا نام کاربری و رمز عبورت در سامانه lms رو برامون در دو خط مثل این بنویس:\n\nنام کاربری\nرمز عبور',
    'correct_userpass': '',
    'incorrect_userpass': '',
}

DAYS = {
    '0': 'شنبه',
    '1': 'یکشنبه',
    '2': 'دوشنبه',
    '3': 'سه شنبه',
    '4': 'چهارشنبه',
    '5': 'پنجشنبه',
    '6': 'جمعه',
}