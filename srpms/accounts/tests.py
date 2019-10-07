"""
Test cases for accounts app.
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.response import Response as RESTResponse
from django_auth_ldap.backend import LDAPBackend, _LDAPUser

from .models import SrpmsUser
from srpms import settings


# Create your tests here.
class AccountsTest(TestCase):
    def setUp(self):
        """Give basic information that can be reused through different test case"""

        self.user_01_name = 'test_basic'
        self.user_01_passwd = 'Basic_12345'
        self.user_01_email = 'test.basic@example.com'
        self.user_01_first_name = 'Test'
        self.user_01_last_name = 'Basic'
        SrpmsUser.objects.create_user(username=self.user_01_name, password=self.user_01_passwd,
                                      email='test.basic@example.com', first_name='Test',
                                      last_name='Basic', uni_id='')
        self.user_01 = SrpmsUser.objects.get(username=self.user_01_name)

    def test_create_user(self):
        """Test create user using SrpmsUser model"""

        # Test create valid user
        SrpmsUser.objects.create(username='test_valid', password='Basic_12345', uni_id='')

        # Test create invalid user
        # Have expire date but no nominator
        with self.assertRaises(ValidationError):
            SrpmsUser.objects.create(username='test_invalid', password='Basic_12345',
                                     expire_date=timezone.now())
        # Have nominator but no expire date
        with self.assertRaises(ValidationError):
            SrpmsUser.objects.create(username='test_invalid', password='Basic_12345',
                                     nominator=SrpmsUser.objects.get(username='test_basic'))

    def test_api_root(self):
        """Test API root of this app"""
        client = APIClient()
        response = client.get('/api/accounts', format='json', secure=True, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_session(self):
        """Test session based login API, only run when DEBUG=True"""

        # Session based login view would only exist when DEBUG is True
        if settings.DEBUG:
            client = APIClient()

            # Login invalid
            response = client.post('/api/accounts/login/',
                                   {'username': self.user_01_name,
                                    'password': 'asdasdioeur9827389423'},
                                   format='json', secure=True, follow=True)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            # Login
            response = client.post('/api/accounts/login/',
                                   {'username': self.user_01_name,
                                    'password': self.user_01_passwd},
                                   format='json', secure=True, follow=True)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Logout
            response = client.get('/api/accounts/logout/',
                                  format='json', secure=True, follow=True)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Logout again
            response = client.get('/api/accounts/logout/',
                                  format='json', secure=True, follow=True)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_token(self):
        """Test token based login API"""

        client = APIClient()

        # Test GET on login page
        response = client.get('/api/accounts/token/', secure=True)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test valid credential login
        response: RESTResponse = client.post('/api/accounts/token/',
                                             {'username': self.user_01_name,
                                              'password': self.user_01_passwd},
                                             format='json', secure=True, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test wrong password login
        response = client.post('/api/accounts/token/',
                               {'username': self.user_01_name, 'password': 'Basic_54321'},
                               format='json', secure=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test empty password login
        response = client.post('/api/accounts/token/',
                               {'username': 'test_basic', 'password': ''},
                               format='json', secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_ldap(self):
        """
        Test SRPMS can communicate to ANU LDAP, make sure you set up environment properly
        before running this test.
        """

        # Test LDAP connection
        ldap_user = _LDAPUser(LDAPBackend(), username='u6513788')
        self.assertEqual(ldap_user.attrs['uid'][0], 'u6513788', 'ANU LDAP server connection failed')

        if not settings.TEST:
            pass  # Not under test environment, skip LDAP login testing
        else:
            # LDAP testing account is store in docker secret, we need to retrieve that first
            client = APIClient()
            ldap_test_username = settings.get_env('', 'LDAP_TEST_USERNAME_FILE')

            # Test LDAP login with valid credential
            response = client.post('/api/accounts/token/',
                                   {'username': ldap_test_username,
                                    'password': settings.get_env('', 'LDAP_TEST_PASSWORD_FILE')},
                                   format='json', secure=True, follow=True)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Test LDAP user attribute mapping
            srpms_user = SrpmsUser.objects.get(username=ldap_test_username)
            self.assertEqual(ldap_user.attrs['uid'][0], srpms_user.username)
            self.assertEqual(ldap_user.attrs['givenname'][0], srpms_user.first_name)
            self.assertEqual(ldap_user.attrs['sn'][0], srpms_user.last_name)
            self.assertEqual(ldap_user.attrs['mail'][0], srpms_user.email)

            # Test LDAP login with invalid credential
            response = client.post('/api/accounts/token/',
                                   {'username': ldap_test_username,
                                    'password': 'aoiuyf7868enkjer23!@#98'},
                                   format='json', secure=True)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_detail(self):
        """Test retrieving user information through API"""

        client = APIClient()

        # Test retrieving user details
        client.login(username=self.user_01_name, password=self.user_01_passwd)
        response = client.get('/api/accounts/user/{}'.format(self.user_01.id),
                              secure=True, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        client.logout()
        response = client.get('/api/accounts/user/{}'.format(self.user_01.id),
                              secure=True, follow=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         "Should failed if not authorized.")
