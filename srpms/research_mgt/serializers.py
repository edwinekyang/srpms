from datetime import datetime
from rest_framework import serializers

from accounts.models import SrpmsUser
from . import models


@PendingDeprecationWarning
class DateTimeBooleanField(serializers.BooleanField):
    """
    Special field for retrieving approval status.

    The database does not have a field 'is_approved', instead we check if
    the 'approval_date' is empty to see if its approved.

    This field can also used to write the DateTimeField, it'll set the
    source field to datetime.now() if the post date is True.
    """

    def to_representation(self, value: bool) -> bool:
        return value

    def to_internal_value(self, data: str) -> datetime:
        """
        Return the value that would be used to update the DateTimeField. If
        True, return the current date & time, otherwise return None.
        """
        is_approved = data

        # Only allow boolean value
        if not isinstance(is_approved, bool):
            raise serializers.ValidationError('Should be a boolean value')

        return datetime.now() if is_approved else None

    def get_attribute(self, instance) -> bool:
        """
        Get attribute from the instance, the return would be passed to
        `to_representation` function. Note that DRF have this behavior
        that None return would not trigger `to_representation`, so we
        need to explicitly set True/False here
        """
        attr = super(DateTimeBooleanField, self).get_attribute(instance)
        return bool(attr)


class CourseSerializer(serializers.ModelSerializer):
    contract = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = models.Course
        fields = ['id', 'course_number', 'name', 'contract']


class AssessmentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AssessmentTemplate
        fields = ['id', 'name', 'description', 'max_mark', 'min_mark', 'default_mark']


class UserContractSerializer(serializers.ModelSerializer):
    own = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    convene = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = SrpmsUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'own', 'convene',
                  'supervise', 'examine']

    # noinspection PyMethodMayBeStatic
    def get_supervise(self, obj: SrpmsUser) -> tuple:
        """
        User's supervise field was pointed to instances of Supervise relation, not contract
        """
        return obj.supervise.all().values_list('contract').get()

    # noinspection PyMethodMayBeStatic
    def get_examine(self, obj: SrpmsUser) -> tuple:
        """
        User's supervise field was pointed to instances of AssessmentMethod relation, not contract
        """
        return obj.examine.all().values_list('contract').get()


class SuperviseSerializer(serializers.ModelSerializer):
    is_formal = serializers.ReadOnlyField()
    supervisor_approval_date = serializers.ReadOnlyField()

    class Meta:
        model = models.Supervise
        fields = ['id', 'contract', 'supervisor', 'is_formal',
                  'is_supervisor_approved', 'supervisor_approval_date']


class AssessmentMethodSerializer(serializers.ModelSerializer):
    examiner_approval_date = serializers.ReadOnlyField()

    class Meta:
        model = models.AssessmentMethod
        fields = ['id', 'template', 'contract', 'additional_description', 'due', 'max_mark',
                  'examiner', 'is_examiner_approved', 'examiner_approval_date']


class IndividualProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IndividualProject
        fields = ['title', 'objectives', 'description']


class SpecialTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SpecialTopics
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

    individual_project = IndividualProjectSerializer(source='individualproject',
                                                     required=False, allow_null=True)
    special_topics = SpecialTopicSerializer(source='specialtopics',
                                            required=False, allow_null=True)

    # Convener related fields
    # Convener is set automatically to the user who approve the contract
    convener = serializers.PrimaryKeyRelatedField(read_only=True)
    convener_approval_date = serializers.ReadOnlyField()

    # Owner related fields
    # Owner is set automatically to the user that create the contract
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    create_date = serializers.ReadOnlyField()
    submit_date = serializers.ReadOnlyField()

    supervise = SuperviseSerializer(source='supervisor', read_only=True, many=True)
    assessment_method = AssessmentMethodSerializer(read_only=True, many=True)

    class Meta:
        model = models.Contract
        fields = ['id', 'year', 'semester', 'duration', 'resources', 'course',
                  'convener', 'is_convener_approved', 'convener_approval_date',
                  'owner', 'create_date', 'submit_date', 'is_submitted',
                  'individual_project', 'special_topics', 'supervise', 'assessment_method']

    def create(self, validated_data: dict):
        """
        Nested field does not support write by DRF, we have to do it ourselves

        https://www.django-rest-framework.org/api-guide/serializers/#writing-create-methods-for-nested-representations
        """
        if validated_data.get('submit_date', False):
            raise serializers.ValidationError('You can\'t submit a contract on creation')

        try:
            individual_project = validated_data.pop('individualproject')
        except KeyError:
            individual_project = None

        try:
            special_topics = validated_data.pop('specialtopics')
        except KeyError:
            special_topics = None

        # Check only one type of contract is provided, this logic cannot be done in validate()
        # because this checking is different for partial update.
        iterator = iter([individual_project, special_topics])
        has_true = any(iterator)
        has_another_true = any(iterator)
        if not (has_true and not has_another_true):
            raise serializers.ValidationError('Contract must be one and only one type')

        if individual_project:
            return models.IndividualProject.objects.create(**validated_data, **individual_project)
        if special_topics:
            return models.SpecialTopics.objects.create(**validated_data, **special_topics)

    def update(self, instance: models.Contract, validated_data: dict):
        """
        Nested field does not support write by DRF, we have to do it ourselves

        https://www.django-rest-framework.org/api-guide/serializers/#writing-update-methods-for-nested-representations
        """
        try:
            # We can't use get() because we need to treat missing key and
            # key's value is None differently.
            individual_project: dict = validated_data.pop('individualproject')
        except KeyError:
            # PATCH may missing this field, but the request is still valid
            if hasattr(instance, 'individualproject'):
                individual_project = {}
            else:
                individual_project = None

        try:
            # We can't use get() because we need to treat missing key and
            # key's value is None differently.
            special_topics: dict = validated_data.pop('specialtopics')
        except KeyError:
            # PATCH may missing this field, but the request is still valid
            if hasattr(instance, 'specialtopics'):
                special_topics = {}
            else:
                special_topics = None

        # Check only one type of contract is provided, this logic cannot be done in validate()
        # because this checking is different for update.
        iterator = iter([individual_project is not None,
                         special_topics is not None])
        has_true = any(iterator)
        has_another_true = any(iterator)
        if not (has_true and not has_another_true):
            raise serializers.ValidationError('Contract must be one and only one type')

        # Set contract type related data
        if hasattr(instance, 'individualproject') and individual_project is not None:
            instance = instance.individualproject
            for attr, value in individual_project.items():
                setattr(instance, attr, value)
        elif hasattr(instance, 'specialtopics') and special_topics is not None:
            instance = instance.specialtopics
            for attr, value in special_topics.items():
                setattr(instance, attr, value)
        else:
            raise serializers.ValidationError('Illegal data for provided contract type.')

        # Set contract data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
