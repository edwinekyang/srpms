"""
Test assessment template API, CRUD methods only.
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from rest_framework import status

from . import utils
from . import data


class TestAssessmentTemplate(utils.SrpmsTest):
    def test_POST(self):
        for temp in data.get_temps():
            response = self.convener.post(utils.ApiUrls.assess_temp, temp)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(response.data.pop('id'))
            self.assertEqual(response.data, temp)

        for temp in data.temp_list_invalid:
            response = self.convener.post(utils.ApiUrls.assess_temp, temp)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_POST_permission(self):
        temp = data.temp_list_valid[0]
        temp_another = data.temp_list_valid[1]

        ########################################
        # Normal user requests
        response = self.user_01.post(utils.ApiUrls.assess_temp, temp)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Supervisor (approved) requests
        response = self.supervisor_formal.post(utils.ApiUrls.assess_temp, temp)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Convener requests
        response = self.convener.post(utils.ApiUrls.assess_temp, temp)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.pop('id'))
        self.assertEqual(response.data, temp)

        ########################################
        # Superuser requests
        response = self.superuser.post(utils.ApiUrls.assess_temp, temp_another)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(response.data.pop('id'))
        self.assertEqual(response.data, temp_another)

    def test_PUT(self):
        temp = data.get_temp()

        # Create first
        response = self.convener.post(utils.ApiUrls.assess_temp, temp)
        temp_id = response.data.pop('id')

        # Legal
        response = self.convener.put(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data.pop('id'))
        self.assertEqual(response.data, temp)

        # Illegal
        for temp in data.temp_list_invalid:
            response = self.convener.put(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_PUT_permission(self):
        temp = data.get_temp()

        # Create first
        response = self.convener.post(utils.ApiUrls.assess_temp, temp)
        temp_id = response.data.pop('id')

        ########################################
        # Normal user requests
        response = self.user_01.put(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Supervisor (approved) requests
        response = self.supervisor_formal.put(utils.ApiUrls.assess_temp + str(temp_id) + '/',
                                              temp)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Convener requests
        response = self.convener.put(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        self.assertEqual(response.data, temp)

        ########################################
        # Superuser requests
        response = self.superuser.put(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        self.assertEqual(response.data, temp)

    def test_PATCH(self):
        temp = data.get_temp()

        # Create first
        response = self.convener.post(utils.ApiUrls.assess_temp, temp)
        temp_id = response.data.pop('id')

        # Legal
        response = self.convener.patch(utils.ApiUrls.assess_temp + str(temp_id) + '/',
                                       {'name': temp['name']})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data.pop('id'))
        self.assertEqual(response.data, temp)

        # Legal
        response = self.convener.patch(utils.ApiUrls.assess_temp + str(temp_id) + '/',
                                       {'default_weight': temp['default_weight']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        self.assertEqual(response.data, temp)

        # Illegal
        for temp in data.temp_list_invalid:
            response = self.convener.put(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_PATCH_permission(self):
        temp = data.get_temp()

        # Create first
        response = self.convener.post(utils.ApiUrls.assess_temp, temp)
        temp_id = response.data.pop('id')

        ########################################
        # Normal user requests
        response = self.user_01.patch(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Supervisor (approved) requests
        response = self.supervisor_formal.patch(utils.ApiUrls.assess_temp + str(temp_id) + '/',
                                                temp)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Convener requests
        response = self.convener.patch(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        self.assertEqual(response.data, temp)

        ########################################
        # Superuser requests
        response = self.superuser.patch(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        self.assertEqual(response.data, temp)

    def test_DELETE(self):
        temp = data.get_temp()

        # Create first
        response = self.convener.post(utils.ApiUrls.assess_temp, temp)
        temp_id = response.data.pop('id')

        response = self.convener.delete(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.convener.delete(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_DELETE_permission(self):
        temp = data.get_temp()

        # Create first
        response = self.convener.post(utils.ApiUrls.assess_temp, temp)
        temp_id = response.data.pop('id')

        ########################################
        # Normal user requests
        response = self.user_01.delete(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Supervisor (approved) requests
        response = self.supervisor_formal.delete(utils.ApiUrls.assess_temp + str(temp_id) + '/',
                                                 temp)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Convener requests
        response = self.convener.delete(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.convener.delete(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        ########################################
        # Superuser requests

        # Create again
        response = self.convener.post(utils.ApiUrls.assess_temp, temp)
        temp_id = response.data.pop('id')

        response = self.convener.delete(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.convener.delete(utils.ApiUrls.assess_temp + str(temp_id) + '/', temp)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
