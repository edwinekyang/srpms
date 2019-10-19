"""
Some general tests for API. These are tests that not worth putting into a separate file, however
be sure to separate if the number of tests in this file grows.
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from rest_framework import status

from . import utils


class APITests(utils.SrpmsTest):
    """Some general test cases"""

    def test_internal_exception_handling(self):
        """Test exception handling"""
        response = self.superuser.post(utils.ApiUrls.assess_temp,
                                       {
                                           'name': 'test',
                                           'description': '',
                                           'weight': 30,
                                           'min_weight': 60,
                                           'default_weight': 90
                                       })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_nologin(self):
        """Test no login user access"""
        for api_url in utils.ApiUrls.all:
            response = self.client_nologin.get(api_url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.superuser.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_login(self):
        """Test GET on api lists"""
        for api_url in utils.ApiUrls.all:
            response = self.superuser.get(api_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.superuser.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_approved_supervisors(self):
        """Test the is_approved_supervisor filter is working correctly"""
        response = self.user_01.get(
                '{}?is_approved_supervisor=true'.format(utils.ApiUrls.mgt_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.user_01.get(
                '{}?is_approved_supervisor=false'.format(utils.ApiUrls.mgt_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_convener(self):
        """Test the is_approved_supervisor filter is working correctly"""
        response = self.user_01.get(
                '{}?is_course_convener=true'.format(utils.ApiUrls.mgt_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.user_01.get(
                '{}?is_course_convener=false'.format(utils.ApiUrls.mgt_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_set_permission(self):
        """Test permission setting"""
        user_id = self.user_04.id

        response = self.convener.put(utils.get_user_url(user_id, supervisor=True),
                                     {'submit': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        response = self.convener.put(utils.get_user_url(user_id, convener=True),
                                     {'submit': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        response = self.convener.put(utils.get_user_url(user_id, supervisor=True),
                                     {'submit': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        response = self.convener.put(utils.get_user_url(user_id, convener=True),
                                     {'submit': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
