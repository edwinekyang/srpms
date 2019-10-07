from datetime import datetime
from django.utils import timezone
from rest_framework.serializers import BooleanField, ValidationError, Serializer, CharField


class DateTimeBooleanField(BooleanField):
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
        # Only allow boolean value
        if not isinstance(data, bool):
            raise ValidationError('Should be a boolean value')

        return timezone.now() if data else None

    def get_attribute(self, instance) -> bool:
        """
        Get attribute from the instance, the return would be passed to
        `to_representation` function. Note that DRF have this behavior
        that None return would not trigger `to_representation`, so we
        need to explicitly set True/False here
        """
        attr = super(DateTimeBooleanField, self).get_attribute(instance)
        return bool(attr)


class SubmitSerializer(Serializer):
    """For converting boolean to current server time only, model unrelated"""

    submit = DateTimeBooleanField(write_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ApproveSerializer(Serializer):
    """For converting boolean to current server time only, model unrelated"""

    approve = DateTimeBooleanField(write_only=True)
    message = CharField(write_only=True, max_length=500, required=False, default='')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
