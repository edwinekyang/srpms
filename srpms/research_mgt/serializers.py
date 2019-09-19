from rest_framework import serializers

from accounts.models import SrpmsUser
from .models import Course, IndividualProject, Supervise, AssessmentMethod


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'course_number', 'name']


class IndividualProjectSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = IndividualProject
        fields = ['title', 'objectives', 'description', 'id', 'year', 'semester', 'duration', 'resources',
                  'convener_approval_date', 'convener', 'create_date', 'owner', 'course']


class AssessmentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentMethod
        fields = ['id', 'template', 'contract', 'additional_description', 'due', 'max_mark',
                  'examiner', 'examiner_approval_date']


class SuperviseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervise
        fields = ['id', 'supervisor', 'is_formal', 'supervisor_approval_date', 'contract']


class UserContractSerializer(serializers.ModelSerializer):
    own = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    convene = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    supervise = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    examine = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = SrpmsUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'own', 'convene',
                  'supervise', 'examine']
