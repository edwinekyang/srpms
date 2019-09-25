from typing import Dict
from rest_framework.test import APIClient
from rest_framework.response import Response
from django.test import TestCase
from django.contrib.auth.models import Group

from accounts.models import SrpmsUser


class ApiUrls(object):
    mgt_user = '/api/research_mgt/users/'
    assess_temp = '/api/research_mgt/assessment-templates/'
    assess_meth = '/api/research_mgt/assessment-methods/'
    course = '/api/research_mgt/course/'
    contract = '/api/research_mgt/contracts/'
    supervise = '/api/research_mgt/supervise/'

    all = [mgt_user, assess_temp, assess_meth, course, contract, supervise]


class Client(APIClient):
    """
    follow=True:   because of the security settings there would be redirect after success
    secure=True:   force passing secure related check
    format='json': only this format is allowed for production
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
    def __init__(self, username, password, first_name="", last_name="", email="", uni_id="",
                 is_approved_supervisor=False, is_convener=False, is_superuser=False):
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
        return self.client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.client.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self.client.put(*args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.client.patch(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.client.delete(*args, **kwargs)


class SrpmsTest(TestCase):
    def setUp(self):
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
