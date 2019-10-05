from typing import Tuple
from django.db import transaction
from rest_framework import serializers

from accounts.models import SrpmsUser
from . import models


class CourseSerializer(serializers.ModelSerializer):
    contract = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = models.Course
        fields = ['id', 'course_number', 'name', 'contract']


class AssessmentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssessmentTemplate
        fields = ['id', 'name', 'description', 'max_weight', 'min_weight', 'default_weight']


class UserContractSerializer(serializers.ModelSerializer):
    """For serializing user and its associated contracts"""

    own = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    supervise = serializers.SerializerMethodField(read_only=True)
    examine = serializers.SerializerMethodField(read_only=True)
    convene = serializers.SerializerMethodField(read_only=True)
    is_approved_supervisor = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SrpmsUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email',
                  'is_approved_supervisor',
                  'own', 'convene', 'supervise', 'examine']

    # noinspection PyMethodMayBeStatic
    def get_supervise(self, obj: SrpmsUser) -> Tuple[int]:
        return tuple(models.Contract.objects.filter(submit_date__isnull=False,
                                                    supervise__supervisor=obj))

    # noinspection PyMethodMayBeStatic
    def get_examine(self, obj: SrpmsUser) -> Tuple[int]:
        """Show contracts a user examine, the contract must has been approved by supervisor"""
        return tuple(models.Contract.objects.filter(
                assessment_examine__examine__examiner=obj,
                supervise__supervisor_approval_date__isnull=False))

    # noinspection PyMethodMayBeStatic
    def get_convene(self, obj: SrpmsUser) -> Tuple[int]:
        """
        Shows submitted contracts for privileged users.

        TODO: Currently convener can only see contracts when its been approved by supervisor
              and examiners, however convener may need to operate on supervisor/examiner's
              behalf in the case that they don't want to use this system.
        """
        if obj.has_perm('research_mgt.is_mgt_superuser'):
            return tuple(models.Contract.objects.all().values_list('pk', flat=True))
        elif obj.has_perm('research_mgt.can_convene'):
            return tuple(models.Contract.objects.filter(
                    submit_date__isnull=False,
                    supervise__supervisor_approval_date__isnull=False,
                    assessment_examine__examiner_approval_date__isnull=False))
        else:
            return tuple()

    # noinspection PyMethodMayBeStatic
    def get_is_approved_supervisor(self, obj: SrpmsUser) -> bool:
        return obj.has_perm('research_mgt.can_supervise')


class SuperviseSerializer(serializers.ModelSerializer):
    # Contract would be attached automatically to the nested view
    contract = serializers.PrimaryKeyRelatedField(read_only=True)

    is_formal = serializers.ReadOnlyField()
    supervisor_approval_date = serializers.ReadOnlyField()

    nominator = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.Supervise
        fields = ['id', 'contract', 'supervisor', 'is_formal', 'nominator',
                  'is_supervisor_approved', 'supervisor_approval_date']


class AssessmentExamineSerializer(serializers.ModelSerializer):
    examiner = serializers.PrimaryKeyRelatedField(source='examine.examiner',
                                                  queryset=SrpmsUser.objects.all())
    nominator = serializers.PrimaryKeyRelatedField(source='examine.nominator', read_only=True)
    examiner_approval_date = serializers.ReadOnlyField()

    class Meta:
        model = models.AssessmentExamine
        fields = ['id', 'examiner', 'nominator', 'examiner_approval_date']

    def create(self, validated_data):
        examiner = validated_data['examine']['examiner']
        nominator = validated_data.pop('nominator')
        examine, _ = models.Examine.objects.get_or_create(contract=validated_data['contract'],
                                                          examiner=examiner,
                                                          defaults={'nominator': nominator})
        validated_data['examine'] = examine
        return super(AssessmentExamineSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        examiner = validated_data['examine']['examiner']
        nominator = validated_data.pop('nominator')
        examine, _ = models.Examine.objects.get_or_create(contract=validated_data['contract'],
                                                          examiner=examiner,
                                                          defaults={'nominator': nominator})
        validated_data['examine'] = examine
        return super(AssessmentExamineSerializer, self).update(instance, validated_data)


class AssessmentSerializer(serializers.ModelSerializer):
    template_info = AssessmentTemplateSerializer(source='template', read_only=True)

    # Contract would be attached automatically to the nested view
    contract = serializers.PrimaryKeyRelatedField(read_only=True)

    assessment_examine = AssessmentExamineSerializer(read_only=True, many=True)

    class Meta:
        model = models.Assessment
        fields = ['id', 'template', 'template_info', 'contract', 'additional_description', 'due',
                  'weight', 'assessment_examine', 'is_all_examiners_approved']


class IndividualProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IndividualProject
        fields = ['title', 'objectives', 'description']


class SpecialTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SpecialTopic
        fields = ['title', 'objectives', 'description']


class ContractSerializer(serializers.ModelSerializer):
    """
    Contract serializer for all types of contract.

    Regardless of the type of contract, they all using the parent class's (i.e. Contract)
    primary key as their primary key, as such it's most convenient to have only one serializer
    to take care of them all.

    In this serializer, different types of contract would be serialized as a nested field. It
    also support write for these nested field by overriding the `create` and `update` method.
    """

    individual_project = IndividualProjectSerializer(required=False, allow_null=True)
    special_topic = SpecialTopicSerializer(required=False, allow_null=True)

    # Convener related fields
    # Convener is set automatically to the user who approve the contract
    convener = serializers.PrimaryKeyRelatedField(read_only=True)
    convener_approval_date = serializers.ReadOnlyField()

    # Owner related fields
    # Owner is set automatically to the user that create the contract
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    create_date = serializers.ReadOnlyField()
    submit_date = serializers.ReadOnlyField()

    supervise = SuperviseSerializer(read_only=True, many=True)
    assessment = AssessmentSerializer(read_only=True, many=True)

    class Meta:
        model = models.Contract
        fields = ['id', 'year', 'semester', 'duration', 'resources', 'course',
                  'convener', 'is_convener_approved', 'convener_approval_date',
                  'owner', 'create_date', 'submit_date', 'is_submitted',
                  'individual_project', 'special_topic',
                  'supervise', 'is_all_supervisors_approved',
                  'assessment', 'is_all_assessments_approved']

    def create(self, validated_data: dict):
        """
        Nested field does not support write by DRF, we have to do it ourselves

        https://www.django-rest-framework.org/api-guide/serializers/#writing-create-methods-for-nested-representations
        """
        if validated_data.get('submit_date', False):
            raise serializers.ValidationError('You can\'t submit a contract on creation')

        try:
            individual_project = validated_data.pop('individual_project')
        except KeyError:
            individual_project = None

        try:
            special_topic = validated_data.pop('special_topic')
        except KeyError:
            special_topic = None

        # Check only one type of contract is provided, this logic cannot be done in validate()
        # because this checking is different for partial update.
        iterator = iter([individual_project, special_topic])
        has_true = any(iterator)
        has_another_true = any(iterator)
        if not (has_true and not has_another_true):
            raise serializers.ValidationError('Contract must be one and only one type')

        if individual_project:
            # Create individual project contract and all its associated assessments, and use
            # transaction to make sure all creation success, otherwise rollback to previous
            # state.
            with transaction.atomic():
                contract = models.IndividualProject.objects.create(**validated_data,
                                                                   **individual_project)
                models.Assessment.objects.create(
                        template=models.AssessmentTemplate.objects.get(name='report'),
                        contract=contract)
                models.Assessment.objects.create(
                        template=models.AssessmentTemplate.objects.get(name='artifact'),
                        contract=contract)
                models.Assessment.objects.create(
                        template=models.AssessmentTemplate.objects.get(name='presentation'),
                        contract=contract)
            return contract
        if special_topic:
            return models.SpecialTopic.objects.create(**validated_data, **special_topic)

    def update(self, instance: models.Contract, validated_data: dict):
        """
        Nested field does not support write by DRF, we have to do it ourselves

        https://www.django-rest-framework.org/api-guide/serializers/#writing-update-methods-for-nested-representations
        """
        try:
            # We can't use get() because we need to treat missing key and
            # key's value is None differently.
            individual_project: dict = validated_data.pop('individual_project')
        except KeyError:
            # PATCH may missing this field, but the request is still valid
            if hasattr(instance, 'individual_project'):
                individual_project = {}
            else:
                individual_project = None

        try:
            # We can't use get() because we need to treat missing key and
            # key's value is None differently.
            special_topic: dict = validated_data.pop('special_topic')
        except KeyError:
            # PATCH may missing this field, but the request is still valid
            if hasattr(instance, 'special_topic'):
                special_topic = {}
            else:
                special_topic = None

        # Check only one type of contract is provided, this logic cannot be done in validate()
        # because this checking is different for update.
        iterator = iter([individual_project is not None,
                         special_topic is not None])
        has_true = any(iterator)
        has_another_true = any(iterator)
        if not (has_true and not has_another_true):
            raise serializers.ValidationError('Contract must be one and only one type')

        # Set contract type related data
        if hasattr(instance, 'individual_project') and individual_project is not None:
            instance = instance.individual_project
            for attr, value in individual_project.items():
                setattr(instance, attr, value)
        elif hasattr(instance, 'special_topic') and special_topic is not None:
            instance = instance.special_topic
            for attr, value in special_topic.items():
                setattr(instance, attr, value)
        else:
            raise serializers.ValidationError('Illegal data for provided contract type.')

        # Set contract data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
