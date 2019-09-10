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
class LoginTestCase(TestCase):
    def setUp(self):
        self.user_01_name = 'test_basic'
        self.user_01_passwd = 'Basic_12345'
        self.user_01_email = 'test.basic@example.com'
        self.user_01_first_name = 'Test'
        self.user_01_last_name = 'Basic'
        SrpmsUser.objects.create_user(username=self.user_01_name, password=self.user_01_passwd,
                                      email='test.basic@example.com', first_name='Test',
                                      last_name='Basic')
        self.user_01 = SrpmsUser.objects.get(username=self.user_01_name)

    def test_create_user(self):
        print('Test create valid user ...')
        SrpmsUser.objects.create(username='test_valid', password='Basic_12345')

        print('Test create invalid user ...')
        # Have expire date but no nominator
        with self.assertRaises(ValidationError):
            SrpmsUser.objects.create(username='test_invalid', password='Basic_12345',
                                     expire_date=timezone.now())
        # Have nominator but no expire date
        with self.assertRaises(ValidationError):
            SrpmsUser.objects.create(username='test_invalid', password='Basic_12345',
                                     nominator=SrpmsUser.objects.get(username='test_basic'))

    def test_update_user(self):
        # TODO: forbid ANU LDAP user from being updated
        pass

    def test_login_basic(self):
        client = APIClient()

        print('Test GET on login page ...')
        response = client.get('/api/accounts/login/', secure=True)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print('Test valid credential login ...')
        response: RESTResponse = client.post('/api/accounts/login/',
                                             {'username': self.user_01_name,
                                              'password': self.user_01_passwd},
                                             format='json', secure=True, follow=True)
        self.assertRedirects(response, '/api/accounts/user/{}/'.format(self.user_01.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        print('Test retrieving user details ...')
        self.assertEqual(response.data['username'], self.user_01_name)
        self.assertEqual(response.data['first_name'], self.user_01_first_name)
        self.assertEqual(response.data['last_name'], self.user_01_last_name)
        self.assertEqual(response.data['email'], self.user_01_email)

        print('Test wrong password login ...')
        response = client.post('/api/accounts/login/',
                               {'username': self.user_01_name, 'password': 'Basic_54321'},
                               format='json', secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        print('Test empty password login ...')
        response = client.post('/api/accounts/login/',
                               {'username': 'test_basic', 'password': ''},
                               format='json', secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_ldap(self):
        print('Test LDAP connection ...')

        ldap_user = _LDAPUser(LDAPBackend(), username='u6513788')
        self.assertEqual(ldap_user.attrs['uid'][0], 'u6513788')

        if not settings.TEST:
            print('Test LDAP login ... not under test environment, skip')
        else:
            print('Test LDAP login  ...')
            client = APIClient()
            ldap_test_username = settings.get_env('', 'LDAP_TEST_USERNAME_FILE')

            print('Test LDAP login with valid credential ...')
            response = client.post('/api/accounts/login/',
                                   {'username': ldap_test_username,
                                    'password': settings.get_env('', 'LDAP_TEST_PASSWORD_FILE')},
                                   format='json', secure=True, follow=True)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            print('Test LDAP user attribute mapping ...')
            srpms_user = SrpmsUser.objects.get(username=ldap_test_username)
            self.assertEqual(ldap_user.attrs['uid'][0], srpms_user.username)
            self.assertEqual(ldap_user.attrs['givenname'][0], srpms_user.first_name)
            self.assertEqual(ldap_user.attrs['sn'][0], srpms_user.last_name)
            self.assertEqual(ldap_user.attrs['mail'][0], srpms_user.email)

            print('Test LDAP login with invalid credential ...')
            response = client.post('/api/accounts/login/',
                                   {'username': ldap_test_username,
                                    'password': 'aoiuyf7868enkjer23!@#98'},
                                   format='json', secure=True)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_edges(self):
        client = APIClient()

        print('Test repeat login ...')
        client.post('/api/accounts/login/',
                    {'username': self.user_01_name, 'password': self.user_01_passwd},
                    format='json', secure=True, follow=True)
        response = client.post('/api/accounts/login/',
                               {'username': self.user_01_name, 'password': self.user_01_passwd},
                               format='json', secure=True, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_basic(self):
        client = APIClient()

        print('Test GET on logout page without login ...')
        response = client.get('/api/accounts/logout/', secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        print('Test GET on logout page after login ...')
        client.post('/api/accounts/login/',
                    {'username': self.user_01_name, 'password': self.user_01_passwd},
                    format='json', secure=True)
        response = client.get('/api/accounts/logout/', secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
