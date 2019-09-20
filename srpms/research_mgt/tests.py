from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import SrpmsUser
from research_mgt import models


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

        self.mgt_user_url = '/api/research_mgt/users/'
        self.assess_temp_url = '/api/research_mgt/assessment-templates/'
        self.assess_meth_url = '/api/research_mgt/assessment-methods/'
        self.course_url = '/api/research_mgt/course/'
        self.contract_url = '/api/research_mgt/contracts/'
        self.supervise_url = '/api/research_mgt/supervise/'

        self.api_urls = [self.mgt_user_url,
                         self.assess_temp_url,
                         self.assess_meth_url,
                         self.course_url,
                         self.contract_url,
                         self.supervise_url]

        self.assess_template = models.AssessmentTemplate.objects.create(
                name='test_template',
                description='test',
                min_mark=30,
                max_mark=70,
                default_mark=50
        )

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

    def test_exception_handling(self):
        client = APIClient()
        client.login(username=self.user_01_name, password=self.user_01_passwd)

        print('test exception handling ...')
        response = client.patch(self.assess_temp_url + '{}/'.format(self.assess_template.id),
                                {'min_mark': 80},
                                format='json', secure=True, follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
