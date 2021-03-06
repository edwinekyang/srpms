"""
Define serializer and de-serializer behavior for model instance. Also include custom create()
and update() method for a given instance, for the purpose of applying business logic.

Note that business logic related to requester (i.e. user who send the HTTP request), should be
put in side views.py
"""

__author__ = "Dajie (Cooper) Yang, and Euikyum (Edwin) Yang"
__credits__ = ["Dajie Yang", "Euikyum Yang"]

__maintainer__ = "Dajie (Cooper) Yang"
__email__ = "dajie.yang@anu.edu.au"

from typing import Tuple
from django.db import transaction
from rest_framework import serializers

from accounts.models import SrpmsUser
from research_mgt.models import (Course, AssessmentTemplate,
                                 Contract, IndividualProject, SpecialTopic, Supervise, Examine,
                                 Assessment, AssessmentExamine)


class CourseSerializer(serializers.ModelSerializer):
    contract = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = Course
        fields = ['id', 'course_number', 'name', 'units', 'contract']


class AssessmentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentTemplate
        fields = ['id', 'name', 'description', 'max_weight', 'min_weight', 'default_weight']


class UserContractSerializer(serializers.ModelSerializer):
    """For serializing user and its associated contracts"""

    own = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    supervise = serializers.SerializerMethodField(read_only=True)
    examine = serializers.SerializerMethodField(read_only=True)
    convene = serializers.SerializerMethodField(read_only=True)
    is_approved_supervisor = serializers.SerializerMethodField(read_only=True)
    is_course_convener = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SrpmsUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'display_name', 'uni_id',
                  'is_approved_supervisor', 'is_course_convener',
                  'own', 'convene', 'supervise', 'examine']

    # noinspection PyMethodMayBeStatic
    def get_supervise(self, obj: SrpmsUser) -> Tuple[int]:
        """
        Show contracts a user supervise

        Args:
            obj: the user that is being serialized currently
        """
        return tuple(Contract.objects.filter(submit_date__isnull=False,
                                             supervise__supervisor=obj)
                     .values_list('pk', flat=True).distinct())

    # noinspection PyMethodMayBeStatic
    def get_examine(self, obj: SrpmsUser) -> Tuple[int]:
        """
        Show contracts a user examine, the contract must has been approved by supervisor

        Args:
            obj: the user that is being serialized currently
        """
        return tuple(Contract.objects.filter(
                assessment_examine__examine__examiner=obj,
                supervise__supervisor_approval_date__isnull=False)
                     .values_list('pk', flat=True).distinct())

    # noinspection PyMethodMayBeStatic
    def get_convene(self, obj: SrpmsUser) -> Tuple[int]:
        """
        Shows submitted contracts for privileged users.

        Args:
            obj: the user that is being serialized currently
        """
        if obj.has_perm('research_mgt.is_mgt_superuser'):
            return tuple(Contract.objects.all().values_list('pk', flat=True))
        elif obj.has_perm('research_mgt.can_convene'):
            return tuple(Contract.objects.filter(
                    submit_date__isnull=False,
                    supervise__supervisor_approval_date__isnull=False,
                    assessment_examine__examiner_approval_date__isnull=False)
                         .values_list('pk', flat=True).distinct())
        else:
            return tuple()

    # noinspection PyMethodMayBeStatic
    def get_is_approved_supervisor(self, obj: SrpmsUser) -> bool:
        """
        Show whether the current user have 'can_supervise' permission

        Args:
            obj: the user that is being serialized currently
        """
        return obj.has_perm('research_mgt.can_supervise')

    # noinspection PyMethodMayBeStatic
    def get_is_course_convener(self, obj: SrpmsUser) -> bool:
        """
        Show whether the current user have 'can_convene' permission

        Args:
            obj: the user that is being serialized currently
        """
        return obj.has_perm('research_mgt.can_convene')


class SuperviseSerializer(serializers.ModelSerializer):
    # Contract would be attached automatically to the nested view
    contract = serializers.PrimaryKeyRelatedField(read_only=True)

    is_formal = serializers.ReadOnlyField()
    supervisor_approval_date = serializers.ReadOnlyField()

    nominator = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Supervise
        fields = ['id', 'contract', 'supervisor', 'is_formal', 'nominator',
                  'is_supervisor_approved', 'supervisor_approval_date']

    def create(self, validated_data: dict):
        """
        Forbid more than 1 formal supervisor for individual project
        TODO: Non-formal supervisor would not get any notification currently

        Args:
            validated_data: a dictionary contain the data a request sent, already validated
        """
        contract: Contract = validated_data['contract']
        if hasattr(contract, 'individual_project') and validated_data['is_formal'] and \
                len(Supervise.objects.filter(contract=contract, is_formal=True)) >= 1:
            raise serializers.ValidationError(
                    'Individual project does not allowed more than 1 formal supervisor.')

        return super(SuperviseSerializer, self).create(validated_data)

    def update(self, instance: Supervise, validated_data: dict):
        """
        Clear supervisor's approval if the supervisor field is being updated.
        TODO: Non-formal supervisor would not get any notification currently

        Args:
            instance: the object that is being updated
            validated_data: a dictionary contain the data a request sent, already validated
        """
        new_supervisor = validated_data.get('supervisor', None)
        if new_supervisor and instance.supervisor_approval_date and \
                instance.supervisor != validated_data['supervisor']:
            instance.supervisor_approval_date = None
            # TODO: Notify supervisor that his/her approval has been cleared

        return super(SuperviseSerializer, self).update(instance, validated_data)


class AssessmentExamineSerializer(serializers.ModelSerializer):
    examiner = serializers.PrimaryKeyRelatedField(source='examine.examiner',
                                                  queryset=SrpmsUser.objects.all())
    nominator = serializers.PrimaryKeyRelatedField(source='examine.nominator', read_only=True)
    examiner_approval_date = serializers.ReadOnlyField()

    class Meta:
        model = AssessmentExamine
        fields = ['id', 'examiner', 'nominator', 'examiner_approval_date']

    def create(self, validated_data) -> AssessmentExamine:
        """
        Allow write for nested examiner field, automatically create missing Examine
        relation for new AssessmentExamine relation. Also apply constraint to forbid
        some contract type to have more than one examiner for each assessment.

        Args:
            validated_data: a dictionary contain the data a request sent, already validated
        """
        examiner = validated_data['examine']['examiner']
        nominator = validated_data.pop('nominator')
        examine, _ = Examine.objects.get_or_create(contract=validated_data['contract'],
                                                   examiner=examiner,
                                                   defaults={'nominator': nominator})
        validated_data['examine'] = examine

        # Forbid individual project and special topic contract to have more than one
        # examiner for each assessment
        assessment: Assessment = validated_data['assessment']
        if hasattr(assessment.contract, 'individual_project') and \
                len(AssessmentExamine.objects.filter(assessment=assessment)) >= 1:
            raise serializers.ValidationError('Individual project cannot have more than one '
                                              'examiner for each assessment.')
        if hasattr(assessment.contract, 'special_topic') and \
                len(AssessmentExamine.objects.filter(assessment=assessment)) >= 1:
            raise serializers.ValidationError('Special topic cannot have more than one examiner '
                                              'for each assessment.')

        return super(AssessmentExamineSerializer, self).create(validated_data)

    def update(self, instance: AssessmentExamine, validated_data) -> AssessmentExamine:
        """
        Allow write for nested examiner field, automatically create missing Examine
        relation for new AssessmentExamine relation.

        Args:
            instance: the object that is being updated
            validated_data: a dictionary contain the data a request sent, already validated
        """
        examiner = validated_data['examine']['examiner']
        nominator = validated_data.pop('nominator')
        examine, _ = Examine.objects.get_or_create(contract=validated_data['contract'],
                                                   examiner=examiner,
                                                   defaults={'nominator': nominator})
        validated_data['examine'] = examine

        # On examiner change, if the assessment has been approved, reset examiner's approval, and
        # notify the previous examiner.
        # This is for the case where convener disapprove examiner, in this case the existing
        # examiner might already approved, but the supervisor's approval has been cleared because
        # of convener's disapprove.
        if examine and instance.examine.examiner != examine.examiner and \
                instance.examiner_approval_date:
            validated_data['examiner_approval_date'] = None
            # TODO: Notify examiner that his/her approval has been cleared

        return super(AssessmentExamineSerializer, self).update(instance, validated_data)


class AssessmentSerializer(serializers.ModelSerializer):
    template_info = AssessmentTemplateSerializer(source='template', read_only=True)

    # Contract would be attached automatically to the nested view
    contract = serializers.PrimaryKeyRelatedField(read_only=True)

    assessment_examine = AssessmentExamineSerializer(read_only=True, many=True)

    class Meta:
        model = Assessment
        fields = ['id', 'template', 'template_info', 'contract', 'additional_description', 'due',
                  'weight', 'assessment_examine', 'is_all_examiners_approved']


class IndividualProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndividualProject
        fields = ['title', 'objectives', 'description']


class SpecialTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialTopic
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
    was_submitted = serializers.ReadOnlyField()

    supervise = SuperviseSerializer(read_only=True, many=True)
    assessment = AssessmentSerializer(read_only=True, many=True)

    class Meta:
        model = Contract
        fields = ['id', 'year', 'semester', 'duration', 'resources', 'course',
                  'convener', 'is_convener_approved', 'convener_approval_date',
                  'owner', 'create_date', 'submit_date', 'is_submitted', 'was_submitted',
                  'individual_project', 'special_topic',
                  'supervise', 'is_all_supervisors_approved',
                  'assessment', 'is_all_assessments_approved',
                  'is_examiner_nominated']

    def create(self, validated_data: dict) -> Contract:
        """
        Nested field does not support write by DRF, we have to do it ourselves

        https://www.django-rest-framework.org/api-guide/serializers/#writing-create-methods-for-nested-representations

        Args:
            validated_data: a dictionary contain the data a request sent, already validated
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
                contract = IndividualProject.objects.create(**validated_data, **individual_project)
                Assessment.objects.create(
                        template=AssessmentTemplate.objects.get(name='report'),
                        contract=contract)
                Assessment.objects.create(
                        template=AssessmentTemplate.objects.get(name='artifact'),
                        contract=contract)
                Assessment.objects.create(
                        template=AssessmentTemplate.objects.get(name='presentation'),
                        contract=contract)
            return contract
        if special_topic:
            return SpecialTopic.objects.create(**validated_data, **special_topic)

    def update(self, instance: Contract, validated_data: dict) -> Contract:
        """
        Nested field does not support write by DRF, we have to do it ourselves

        https://www.django-rest-framework.org/api-guide/serializers/#writing-update-methods-for-nested-representations

        Args:
            instance: the object that is being updated
            validated_data: a dictionary contain the data a request sent, already validated
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
