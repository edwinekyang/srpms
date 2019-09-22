from rest_framework import status

from . import utils


class TestAssessmentTemplate(utils.SrpmsTest):
    def test_assessment_template_api_normal_user(self):
        valid_data_01 = {
            'name': 'test',
            'description': '',
            'max_mark': 80,
            'min_mark': 20,
            'default_mark': 50
        }

        # Normal user shouldn't allow to create
        response = self.user_01.post(utils.ApiUrls.assess_temp, valid_data_01)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Normal user shouldn't allow to edit
        response = self.user_01.put(utils.ApiUrls.assess_temp + '1/', valid_data_01)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Normal user shouldn't allow to edit
        response = self.user_01.patch(utils.ApiUrls.assess_temp + '1/', valid_data_01)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Normal user shouldn't allow to delete
        response = self.user_01.delete(utils.ApiUrls.assess_temp + '1/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assessment_template_api_convener(self):
        valid_data_01 = {
            'name': 'test',
            'description': '',
            'max_mark': 80,
            'min_mark': 20,
            'default_mark': 50
        }

        valid_data_02 = {
            'max_mark': 60,
            'min_mark': 40,
        }

        # Convener should allow to create
        response = self.convener.post(utils.ApiUrls.assess_temp, valid_data_01)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data_id = response.data.pop('id')
        self.assertEqual(response.data, valid_data_01)

        # Convener should allow to edit
        response = self.convener.put(utils.ApiUrls.assess_temp + str(data_id) + '/', valid_data_01)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.data.pop('id')
        self.assertEqual(response.data, valid_data_01)

        # Convener should allow to edit
        response = self.convener.patch(utils.ApiUrls.assess_temp + str(data_id) + '/',
                                       valid_data_02)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], valid_data_01['name'])
        self.assertEqual(response.data['description'], valid_data_01['description'])
        self.assertEqual(response.data['max_mark'], valid_data_02['max_mark'])
        self.assertEqual(response.data['min_mark'], valid_data_02['min_mark'])
        self.assertEqual(response.data['default_mark'], valid_data_01['default_mark'])

        # Convener should allow to delete
        response = self.convener.delete(utils.ApiUrls.assess_temp + str(data_id) + '/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.convener.get(utils.ApiUrls.assess_temp + str(data_id) + '/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
