from BotApp.models import *
from CE99Bot.config import * 

def apply():
    # users = {user.id: user for user in User.objects.all()}
    # courses = {course.id: course for course in Course.objects.all()}
    # days = {day.id: day for day in Day.objects.all()}
    # clock_times = {clock_time.id: clock_time for clock_time in ClockTime.objects.all()}
    UserCourse_CUBE.objects.all().delete()
    for user in User.objects.all():
        days_dict = {day.name: [] for day in Day.objects.all()}
        user_active_courses = UserCourse.objects.filter(user=user, course__term__name=CURRENT_TERM)
        course_day_clock_time_list = CourseDayClockTime.objects.filter(course__in=user_active_courses.values('course'))
        for cdc in course_day_clock_time_list:
            days_dict[cdc.day.name].append({
                'course_name': cdc.course.name,
                'course_code': cdc.course.code,
                'course_time': cdc.clock_time.time
            })

        user_courses = {}
        for user_course in user_active_courses:
            cdc = CourseDayClockTime.objects.filter(course=user_course.course)
            user_courses[user_course.course.code] = {
                'course_name': user_course.course.name,
                'course_code': user_course.course.code,
                'course_teacher': user_course.course.teacher.name if user_course.course.teacher else None,
                'course_term': user_course.course.term.name,
                # 'course_department': course.department.name,
                'course_days': [c.day.name for c in cdc],
                'course_times': cdc.first().clock_time.time,
                'user_type': user_course.user_type.name,
            }


        UserCourse_CUBE.objects.create(user=user, dailycourse_info=days_dict, courses=user_courses)
