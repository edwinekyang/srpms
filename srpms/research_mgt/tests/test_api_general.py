from rest_framework import status

from . import utils


class APITests(utils.SrpmsTest):
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
        response = self.user_01.get(
                '{}?is_approved_supervisor=true'.format(utils.ApiUrls.mgt_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.user_01.get(
                '{}?is_approved_supervisor=false'.format(utils.ApiUrls.mgt_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
