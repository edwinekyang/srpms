"""
Define database models for user through Django ORM (Object-relation Mapping).
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, Permission, Group


class SrpmsUser(AbstractUser):
    """
    Table for additional user attributes for SRPMS application.

    Note that the AbstractUser model already includes the following fields:
    - username
    - password
    - first_name
    - last_name
    - email
    - is_staff

    For external user nomination, we currently configure it to be null if the
    nominator is deleted, however the expire date would remain.

    The ANU user would have their uni id in here as well. It would be null in
    the case of external user.

    TODO: If the user is authenticated through ANU LDAP, forbid anyone to update but only LDAP
    TODO: Validate expire date on user login
    """
    # External user related field
    nominator = models.ForeignKey('self', on_delete=models.SET_NULL, default=None, blank=True,
                                  null=True)
    expire_date = models.DateTimeField(default=None, blank=True, null=True)

    # ANU Account related field
    uni_id = models.CharField("Uni ID", max_length=8, default='', blank=True, null=False)

    display_name = models.CharField(default='', max_length=150, blank=True, null=False)

    def get_display_name(self) -> str:
        """Get display name for the user"""
        display_name = ' '.join([self.first_name, self.last_name])
        if not display_name.replace(' ', ''):
            # First name and last name both empty would make display name empty
            return self.username
        return display_name

    def clean(self):
        """
        Apply constraint to the model
        """
        if any([self.nominator, self.expire_date]) and not all([self.nominator, self.expire_date]):
            raise ValidationError('Both nominator and expire date is required on nomination')

    def save(self, *args, **kwargs):
        self.full_clean()
        self.display_name = self.get_display_name()
        super(SrpmsUser, self).save(*args, **kwargs)
