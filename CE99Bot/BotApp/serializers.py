
from rest_framework import serializers
from .models import *


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField('get_courses')
    class Meta:
        model = User
        fields = '__all__'

    def get_courses(self, obj):
        return CourseSerializer(obj.courses.all(), many=True).data
