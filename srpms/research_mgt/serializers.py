from rest_framework import serializers
from .models import Course, Contract


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_id', 'course_number', 'name']


class ContractSerializer(serializers.ModelSerializer):
    u_id = serializers.ReadOnlyField(source='u_id.id')

    class Meta:
        model = Contract
        fields = ['contract_id', 'year', 'semester', 'duration', 'res', 'ca_date', 'c_id', 'i_date',
                  'u_id', 's_id', 'is_formal', 'sa_date', 'course_id']
