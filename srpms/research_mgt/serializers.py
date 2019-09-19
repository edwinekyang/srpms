from rest_framework import serializers

from accounts.models import SrpmsUser
from .models import Course, Contract, AssessmentMethod


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


class AssessmentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentMethod
        fields = ['id', 'template', 'contract', 'additional_description', 'due', 'max_mark',
                  'examiner', 'examiner_approval_date']


class UserContractSerializer(serializers.ModelSerializer):
    own = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    convene = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    supervise = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    examine = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = SrpmsUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'own', 'convene',
                  'supervise', 'examine']
