from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import SrpmsUser


# Create your tests here.

class SerializerTest(TestCase):
    def setUp(self):
        self.user_01_name = 'test_basic'
        self.user_01_passwd = 'Basic_12345'
        self.user_01_email = 'test.basic@example.com'
        self.user_01_first_name = 'Test'
        self.user_01_last_name = 'Basic'
        SrpmsUser.objects.create_user(username=self.user_01_name, password=self.user_01_passwd,
                                      email='test.basic@example.com', first_name='Test',
                                      last_name='Basic', uni_id="")
        self.user_01 = SrpmsUser.objects.get(username=self.user_01_name)

        self.api_urls = ['/api/research_mgt/users/',
                         '/api/research_mgt/assessment-templates/',
                         '/api/research_mgt/assessment-methods/',
                         '/api/research_mgt/course/',
                         '/api/research_mgt/contracts/',
                         '/api/research_mgt/supervise/']

    def test_api_acccess(self):
        client = APIClient()

        # Test no login user access
        for api_url in self.api_urls:
            response = client.get(api_url, format='json', secure=True, follow=True)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test login user access
        client.login(username=self.user_01_name, password=self.user_01_passwd)
        for api_url in self.api_urls:
            response = client.get(api_url, format='json', secure=True, follow=True)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
