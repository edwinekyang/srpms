"""
Utilities that simplify the test process, and avoid hard coding data in multiple places.
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from typing import Dict
from rest_framework.test import APIClient
from rest_framework.response import Response
from django.test import TestCase
from django.contrib.auth.models import Group

from accounts.models import SrpmsUser


class ApiUrls(object):
    """List of API URLs"""
    mgt_user = '/api/research_mgt/users/'
    assess_temp = '/api/research_mgt/assessment-templates/'
    course = '/api/research_mgt/courses/'
    contract = '/api/research_mgt/contracts/'

    # Below are nested view name
    supervise = 'supervise'
    assessment = 'assessments'
    examine = 'examine'

    # GET method would be tested on these, nested url are not testable.
    all = [mgt_user, assess_temp, course, contract]


def get_contract_url(contract_id: int = None, submit: bool = False, approve: bool = False,
                     print: bool = False) -> str:
    """
    Return contract list url, or contract detail url, depending on whether the contract_id
    is specified. Note that 'submit' and 'approve' are only valid when contract_id is given.

    Args:
        contract_id: for generating contract detail url
        submit: for generating submission url given a contract
        approve: for generating approval url given a contract
    """

    if not contract_id:
        return ApiUrls.contract
    else:
        if submit:
            return '{}{}/submit/'.format(ApiUrls.contract, contract_id)
        elif approve:
            return '{}{}/approve/'.format(ApiUrls.contract, contract_id)
        elif print:
            return '{}{}/print/'.format(ApiUrls.contract, contract_id)
        else:
            return '{}{}/'.format(ApiUrls.contract, contract_id)


def get_supervise_url(contract_id: int, supervise_id: int = None, approve: bool = False) -> str:
    """
    Return supervise list url, or supervise detail url, depending on whether the supervise_formal_id
    is specified. Note that 'approve' is only valid when supervise_formal_id is given.

    Args:
        contract_id: for specifying parent url
        supervise_id: for generating supervise detail url
        approve: for generating approval url given a supervise_formal_id
    """

    if not supervise_id:
        return '{}{}/{}/'.format(ApiUrls.contract, contract_id, ApiUrls.supervise)
    else:
        if approve:
            return '{}{}/{}/{}/approve/'.format(ApiUrls.contract, contract_id,
                                                ApiUrls.supervise, supervise_id)
        else:
            return '{}{}/{}/{}/'.format(ApiUrls.contract, contract_id,
                                        ApiUrls.supervise, supervise_id)


def get_assessment_url(contract_id: int, assessment_id: int = None) -> str:
    """
    Return assessment list url, or assessment detail url, depending on whether the assessment_id
    is specified.

    Args:
        contract_id: for specifying parent url
        assessment_id: for generating assessment detail url
    """

    if not assessment_id:
        return '{}{}/{}/'.format(ApiUrls.contract, contract_id, ApiUrls.assessment)
    else:
        return '{}{}/{}/{}/'.format(ApiUrls.contract, contract_id,
                                    ApiUrls.assessment, assessment_id)


def get_examine_url(contract_id: int, assessment_id: int, examine_id: int = None,
                    approve: bool = False) -> str:
    """
    Return assessment examine list url, or assessment examine detail url, depending on whether the
    examine_id is specified. Note that 'approve' is only valid when examine_id is given.

    Args:
        contract_id: for specifying parent url
        assessment_id: for specifying parent url
        examine_id: for generating assessment examine detail url
        approve: for generating approval url given a examine_id
    """

    if not examine_id:
        return '{}{}/{}/{}/{}/'.format(ApiUrls.contract, contract_id,
                                       ApiUrls.assessment, assessment_id,
                                       ApiUrls.examine)
    else:
        if approve:
            return '{}{}/{}/{}/{}/{}/approve/'.format(ApiUrls.contract, contract_id,
                                                      ApiUrls.assessment, assessment_id,
                                                      ApiUrls.examine, examine_id)
        else:
            return '{}{}/{}/{}/{}/{}/'.format(ApiUrls.contract, contract_id,
                                              ApiUrls.assessment, assessment_id,
                                              ApiUrls.examine, examine_id)


class Client(APIClient):
    """
    The client wrapper for the original APIClient, so that some parameters won't need to be
    specified over and over again.

    `follow=True``  because of the security settings there would be redirect after success
    `secure=True`   force passing secure related check
    `format='json`  only this format is allowed in production environment

    Also note that by using `**{'data': data, 'follow': True, **extra}` we can allow keys being
    repeated in `**extra`, in which case value in `**extra` would be used.
    """

    def get(self, path: str, data: Dict = None, **extra) -> Response:
        return super(Client, self).get(path, **{'data': data, 'follow': True, **extra})

    def post(self, path: str, data: Dict = None, content_type=None, **extra) -> Response:
        return super(Client, self).post(path, **{'data': data, 'content_type': content_type,
                                                 'format': 'json', 'follow': True, 'secure': True,
                                                 **extra})

    def put(self, path: str, data: Dict = None, content_type=None, **extra) -> Response:
        return super(Client, self).put(path, **{'data': data, 'content_type': content_type,
                                                'format': 'json', 'follow': True, 'secure': True,
                                                **extra})

    def patch(self, path: str, data: Dict = None, content_type=None, **extra) -> Response:
        return super(Client, self).patch(path, **{'data': data, 'content_type': content_type,
                                                  'format': 'json', 'follow': True, 'secure': True,
                                                  **extra})

    def delete(self, path: str, data: Dict = None, content_type=None, **extra) -> Response:
        return super(Client, self).delete(path, **{'data': data, 'content_type': content_type,
                                                   'format': 'json', 'follow': True, 'secure': True,
                                                   **extra})


class User(object):
    """
    A user object for conveniently define user information for API testing. It would includes
    raw information (i.e. in string) about the user, and the corresponding SrpmsUser object,
    as well as a APIClient with this user's login information
    """

    def __init__(self, username, password, first_name='', last_name='', email='', uni_id='',
                 is_approved_supervisor=False, is_convener=False, is_superuser=False):
        """Class initialization"""

        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.uni_id = uni_id

        self.obj = SrpmsUser.objects.create_user(username=username, password=password,
                                                 first_name=first_name, last_name=last_name,
                                                 email=email,
                                                 uni_id=uni_id)

        self.id = self.obj.id

        if is_approved_supervisor:
            self.obj.groups.add(Group.objects.get(name='approved_supervisors'))
            self.obj = SrpmsUser.objects.get(username=username)  # Avoid permission caching

        if is_convener:
            self.obj.groups.add(Group.objects.get(name='course_convener'))
            self.obj = SrpmsUser.objects.get(username=username)  # Avoid permission caching

        if is_superuser:
            self.obj.groups.add(Group.objects.get(name='mgt_superusers'))
            self.obj = SrpmsUser.objects.get(username=username)  # Avoid permission caching

        self.client = Client()
        self.client.login(username=username, password=password)

    def get(self, *args, **kwargs):
        """Wrapper for APIClient method"""
        return self.client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Wrapper for APIClient method"""
        return self.client.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        """Wrapper for APIClient method"""
        return self.client.put(*args, **kwargs)

    def patch(self, *args, **kwargs):
        """Wrapper for APIClient method"""
        return self.client.patch(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Wrapper for APIClient method"""
        return self.client.delete(*args, **kwargs)


class SrpmsTest(TestCase):
    """A TestCase class that set up common data for API testing."""

    def setUp(self) -> None:
        """
        Set up testing data, note that when inheriting from this class, this
        class's (i.e. super class) setUp() method should be called first, before
        your own test class's setUp() method (if you have one).
        """

        # Users ------------------------------------------------------------------------------------

        self.user_01 = User('user_01', 'Basic_12345', '01', 'User', 'user.01@example.com')
        self.user_02 = User('user_02', 'Basic_23456', '02', 'User', 'user.02@example.com')
        self.user_03 = User('user_03', 'Basic_56789', '03', 'User', 'user.03@example.com')
        self.user_04 = User('user_04', 'Basic_67890', '04', 'User', 'user.04@example.com')

        self.supervisor_non_formal = User('supervisor_non_formal', 'Sup_12345',
                                          'Non Formal', 'Supervisor',
                                          'supervisor.non.formal@example.com')

        self.supervisor_formal = User('supervisor_formal', 'Sup_23456',
                                      'Formal', 'Supervisor', 'supervisor.formal@example.com',
                                      is_approved_supervisor=True)

        self.convener = User('convener', 'Con_12345', '01', 'Convener', 'convener.01@example.com',
                             is_convener=True)

        self.superuser = User('superuser', 'Super_12345', '01', 'Superuser',
                              'superuser.01@example.com', is_superuser=True)

        # Clients ----------------------------------------------------------------------------------

        self.client_nologin = Client()
