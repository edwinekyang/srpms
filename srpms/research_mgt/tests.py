from django.test import TestCase
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import SrpmsUser
from research_mgt import models


# Create your tests here.

class ResearchMgtTest(TestCase):
    def setUp(self):
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

        self.user_01_name = 'test_01'
        self.user_01_passwd = 'Basic_12345'
        self.user_01 = SrpmsUser.objects.create_user(username=self.user_01_name,
                                                     password=self.user_01_passwd,
                                                     email='test.01@example.com',
                                                     first_name='01',
                                                     last_name='Test', uni_id="")

        self.user_02_name = 'test_02'
        self.user_02_passwd = 'Basic_23456'
        self.user_02 = SrpmsUser.objects.create_user(username=self.user_02_name,
                                                     password=self.user_02_passwd,
                                                     email='test.02@example.com',
                                                     first_name='02',
                                                     last_name='Test', uni_id="")

        self.user_supervisor_name = 'test_supervisor'
        self.user_supervisor_passwd = 'Basic_23456'
        self.user_supervisor = SrpmsUser.objects.create_user(username=self.user_supervisor_name,
                                                             password=self.user_supervisor_passwd,
                                                             email='test.supervisor@example.com',
                                                             first_name='Supervisor',
                                                             last_name='Test', uni_id="")
        self.user_supervisor.groups.add(Group.objects.get(name='approved_supervisors'))
        self.user_supervisor = SrpmsUser.objects.get(username=self.user_supervisor_name)
        # Because of permission caching, we need to get the user again

        self.user_convener_name = 'test_convener'
        self.user_convener_passwd = 'Basic_09876'
        self.user_convener = SrpmsUser.objects.create_user(username=self.user_convener_name,
                                                           password=self.user_convener_passwd,
                                                           email='test.convener@example.com',
                                                           first_name='Convener',
                                                           last_name='Test', uni_id="")
        self.user_convener.groups.add(Group.objects.get(name='course_convener'))
        self.user_convener = SrpmsUser.objects.get(username=self.user_convener_name)

        self.user_super_name = 'test_super'
        self.user_super_passwd = 'Super_09876'
        self.user_super = SrpmsUser.objects.create_user(username=self.user_super_name,
                                                        password=self.user_super_passwd,
                                                        email='test.super@example.com',
                                                        first_name='Super',
                                                        last_name='Test', uni_id="")
        self.user_super.groups.add(Group.objects.get(name='mgt_superusers'))
        self.user_super = SrpmsUser.objects.get(username=self.user_super_name)

        self.comp8755 = models.Course.objects.get(course_number='COMP8755')
        self.comp6470 = models.Course.objects.get(course_number='COMP6470')

        self.indiv_proj = models.IndividualProject.objects.create(title='TestIndiv',
                                                                  course=self.comp8755,
                                                                  owner=self.user_01)
        self.speci_topc = models.SpecialTopics.objects.create(title='TestSpeci',
                                                              course=self.comp6470,
                                                              owner=self.user_02)

        self.assess_template = models.AssessmentTemplate.objects.create(
                name='test_template',
                description='test',
                min_mark=30,
                max_mark=70,
                default_mark=50
        )

    def test_course_api(self):
        pass

    def test_contract_api(self):
        pass

    def test_supervise_api(self):
        pass

    def test_assessment_template_api(self):
        pass

    def test_assessment_method_api(self):
        pass

    def test_api_access(self):
        client = APIClient()

        print('Test no login user access ...')
        for api_url in self.api_urls:
            response = client.get(api_url, format='json', secure=True, follow=True)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        client.login(username=self.user_super_name, password=self.user_super_passwd)
        print('Test GET on api lists ...')
        for api_url in self.api_urls:
            response = client.get(api_url, format='json', secure=True, follow=True)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_exception_handling(self):
        client = APIClient()
        client.login(username=self.user_super_name, password=self.user_super_passwd)

        print('test exception handling ...')
        response = client.post(self.assess_temp_url,
                               {
                                   "name": "test",
                                   "description": "",
                                   "max_mark": 30,
                                   "min_mark": 60,
                                   "default_mark": 90
                               },
                               format='json', secure=True, follow=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
