from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient
from django_auth_ldap.backend import LDAPBackend, _LDAPUser

from .models import SrpmsUser
from srpms import settings


# Create your tests here.
class LoginTestCase(TestCase):
    def setUp(self):
        SrpmsUser.objects.create_user(username='test_basic', password='Basic_12345')

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

    def test_login_basic(self):
        client = APIClient()

        print('Test valid credential login ...')
        response = client.post('/api/accounts/login/',
                               {'username': 'test_basic', 'password': 'Basic_12345'},
                               format='json', secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        print('Test wrong password login ...')
        response = client.post('/api/accounts/login/',
                               {'username': 'test_basic', 'password': 'Basic_54321'},
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

            print('Test LDAP login with valid credential ...')
            response = client.post('/api/accounts/login/',
                                   {'username': settings.get_env('', 'LDAP_TEST_USERNAME_FILE'),
                                    'password': settings.get_env('', 'LDAP_TEST_PASSWORD_FILE')},
                                   format='json', secure=True)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            print('Test LDAP login with invalid credential ...')
            response = client.post('/api/accounts/login/',
                                   {'username': 'u6513788',
                                    'password': 'aoiuyf7868enkjer23!@#98'},
                                   format='json', secure=True)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


