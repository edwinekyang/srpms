from django.db import models
from django.contrib.auth.models import User

from enum import Enum


class AuthMethods(Enum):
    ANU = "ANU_LDAP"  # Use ANU LDAP API for authentication
    SIT = "Site"  # Use the password stored in this site's database


class SrpmsUser(models.Model):
    """
    Table for additional user attributes for application use

    Note that the default User model already include fields like last name,
    first name, email, etc.
    """
    user = models.OneToOneField(User, related_name='srpms', on_delete=models.CASCADE)
    uni_id = models.CharField("Uni ID", max_length=8, blank=True)
    auth_method = models.CharField(
            max_length=10,
            choices=[(tag, tag.value) for tag in AuthMethods]
    )

    # Contact email might be different from user email
    contact_email = models.EmailField("contact email", blank=True)
