from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient

from .models import SrpmsUser


# Create your tests here.
class LoginTestCase(TestCase):

    def test_create_user(self):
        print('Test create valid user ...')
        SrpmsUser.objects.create(username='test_basic', password='Basic_12345')

        with self.assertRaises(ValidationError):
            print('Test create invalid user ...')
            SrpmsUser.objects.create(username='test_invalid', password='Basic_12345',
                                     expire_date=timezone.now())

    def test_login_basic(self):
        SrpmsUser.objects.create_user(username='test_basic', password='Basic_12345')

        client = APIClient()
        response = client.post('/api/accounts/login/',
                               {'username': 'test_basic', 'password': 'Basic_12345'},
                               format='json')
        print('Test valid credential login ...')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = client.post('/api/accounts/login/',
                               {'username': 'test_basic', 'password': 'Basic_54321'},
                               format='json')
        print('Test wrong password login ...')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = client.post('/api/accounts/login/',
                               {'username': 'test_basic', 'password': ''},
                               format='json')
        print('Test empty password login ...')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
