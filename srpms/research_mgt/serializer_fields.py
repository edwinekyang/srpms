from datetime import datetime
from rest_framework import serializers


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
