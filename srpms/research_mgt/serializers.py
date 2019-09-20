from rest_framework import serializers

from accounts.models import SrpmsUser
from . import models


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'course_number', 'name']


class IndividualProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IndividualProject
        fields = ['title', 'objectives', 'description']


class SpecialTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SpecialTopics
        fields = ['title', 'objectives', 'description']


class ContractSerializer(serializers.ModelSerializer):
    individual_project = IndividualProjectSerializer(source='individualproject',
                                                     required=False, allow_null=True)
    special_topics = SpecialTopicSerializer(source='specialtopics',
                                            required=False, allow_null=True)

    class Meta:
        model = models.Contract
        fields = ['id', 'year', 'semester', 'duration', 'resources', 'course', 'convener',
                  'convener_approval_date', 'owner', 'create_date',
                  'individual_project', 'special_topics']

    def validate(self, attrs: dict):
        """Validate to check only one type of contract is provided"""
        iterator = iter([attrs['individualproject'], attrs['specialtopics']])
        has_true = any(iterator)
        has_another_true = any(iterator)
        if not (has_true and not has_another_true):
            raise serializers.ValidationError("Contract must be one and only one type")
        return attrs

    def create(self, validated_data: dict):
        """
        Nested field does not support write by DRF, we have to do it ourselves

        https://www.django-rest-framework.org/api-guide/serializers/#writing-create-methods-for-nested-representations
        """
        individual_project = validated_data.pop('individualproject')
        special_topics = validated_data.pop('specialtopics')
        if individual_project:
            return models.IndividualProject.objects.create(**validated_data, **individual_project)
        if special_topics:
            return models.SpecialTopics.objects.create(**validated_data, **special_topics)

    def update(self, instance: models.Contract, validated_data: dict):
        """
        Nested field does not support write by DRF, we have to do it ourselves

        https://www.django-rest-framework.org/api-guide/serializers/#writing-update-methods-for-nested-representations
        """
        individual_project: dict = validated_data.pop('individualproject')
        special_topics: dict = validated_data.pop('specialtopics')

        # Set sub-contract related data
        if hasattr(instance, 'individualproject') and individual_project:
            instance = instance.individualproject
            for attr, value in individual_project.items():
                setattr(instance, attr, value)
        elif hasattr(instance, 'specialtopics') and special_topics:
            instance = instance.specialtopics
            for attr, value in special_topics.items():
                setattr(instance, attr, value)
        else:
            raise serializers.ValidationError("Illegal data for provided contract type.")

        # Set contract data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class SuperviseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Supervise
        fields = ['id', 'supervisor', 'is_formal', 'supervisor_approval_date', 'contract']


class AssessmentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssessmentTemplate
        fields = ['id', 'name', 'description', 'max_mark', 'min_mark', 'default_mark']


class AssessmentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssessmentMethod
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
