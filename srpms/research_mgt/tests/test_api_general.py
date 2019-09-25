from rest_framework import status

from . import utils


class APITests(utils.SrpmsTest):
    def test_internal_exception_handling(self):
        print('test exception handling ...')
        response = self.superuser.post(utils.ApiUrls.assess_temp,
                                       {
                                           'name': 'test',
                                           'description': '',
                                           'max_mark': 30,
                                           'min_mark': 60,
                                           'default_mark': 90
                                       })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_nologin(self):
        print('Test no login user access ...')
        for api_url in utils.ApiUrls.all:
            response = self.client_nologin.get(api_url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_login(self):
        print('Test GET on api lists ...')
        for api_url in utils.ApiUrls.all:
            response = self.superuser.get(api_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
