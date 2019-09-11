from rest_framework import serializers
from .models import Course, Contract


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_id', 'course_number', 'name']
