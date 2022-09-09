from django.db import models


class Term(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.term


class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    lms_id = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.name


class UserStatus(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.name


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    chat_id = models.IntegerField(unique=True)
    telegram_username = models.CharField(max_length=500, null=True)
    lms_username = models.CharField(max_length=50, null=True)
    lms_password = models.CharField(max_length=50, null=True)
    student_id = models.CharField(max_length=50, null=True)
    full_name = models.CharField(max_length=256, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    is_super_user = models.BooleanField(default=False)
    status = models.ForeignKey(UserStatus, on_delete=models.CASCADE, null=True)

    
    def __str__(self):
        return self.username



class Course(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, null=True)
    code = models.CharField(max_length=500, null=True, unique=True)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

class ClockTime(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.time

class Day(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.name

class CourseDayClockTime(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    clock_time = models.ForeignKey(ClockTime, on_delete=models.CASCADE)

    def __str__(self):
        return self.course.name + " " + self.day.name + " " + self.clock_time.time


class CourseAdmin(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.course.name + " - " + self.user.username


class UserCourseType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, unique=True)

    def __str__(self):
        return self.name


class UserCourse(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    user_type = models.ForeignKey(UserCourseType, on_delete=models.DO_NOTHING, null=True)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.user.lms_username + " - " + self.course.name


class UserCourse_CUBE(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    dailycourse_info = models.JSONField(null=True)
    courses = models.JSONField(null=True)

    def __str__(self):
        return self.user.username + " - " + self.course.name

        
class Deadline(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    deadline = models.DateTimeField()
    title = models.CharField(max_length=500, null=True)
    description = models.TextField(null=True)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class UserDeadline(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deadline = models.ForeignKey(Deadline, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + " " + self.deadline.title

class Directory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class File(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    directory = models.ForeignKey(Directory, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name