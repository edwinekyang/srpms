"""
A wrapper for the LDAPBackend, in case we need to override it in the future.
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from django_auth_ldap.backend import LDAPBackend


class ANULDAPBackend(LDAPBackend):
    """
    LDAPBackend with custom user build/update behavior
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # TODO: Check expire date on inviting external user
        return super(ANULDAPBackend, self).authenticate(request=request,
                                                        username=username,
                                                        password=password,
                                                        **kwargs)
