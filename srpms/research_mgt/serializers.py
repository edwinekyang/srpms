from rest_framework import serializers
from .models import Course, IndividualProject, AssessmentMethod, Supervise


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'course_number', 'name']


class IndividualProjectSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = IndividualProject
        fields = ['title', 'object', 'description', 'id', 'year', 'semester', 'duration', 'resources',
                  'convener_approval_date', 'convener', 'create_date', 'owner', 'course']


class AssessmentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentMethod
        fields = ['id', 'template', 'contract', 'due', 'max', 'additional_description',
                  'examiner', 'examiner_approval_date']


class SuperviseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervise
        fields = ['id', 'supervisor', 'is_formal', 'supervisor_approval_date', 'contract']
