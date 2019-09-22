from rest_framework import status

from . import utils
from . import data


class TestCourse(utils.SrpmsTest):
    def test_course_api_user_normal(self):
        valid_data = {
            'course_number': 'Test0001',
            'name': 'Whatever'
        }

        comp8755 = {
            'course_number': data.comp8755.course_number,
            'name': 'Whatever'
        }

        # Normal user shouldn't allow to create
        response = self.user_01.post(utils.ApiUrls.course, valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Normal user shouldn't allow to edit
        response = self.user_01.put(utils.ApiUrls.course + '{}/'.format(data.comp8755.pk),
                                    comp8755)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Normal user shouldn't allow to edit
        response = self.user_01.patch(utils.ApiUrls.course + '{}/'.format(data.comp8755.pk),
                                      valid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Normal user shouldn't allow to delete
        response = self.user_01.delete(utils.ApiUrls.course + '{}/'.format(data.comp8755.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_api_user_convener(self):
        valid_data_01 = {
            'course_number': 'Test0001',
            'name': 'Whatever'
        }

        valid_data_02 = {
            'course_number': 'Test0001',
            'name': 'Whatasdfqr9283ever'
        }

        # Convener should allow to create
        response = self.convener.post(utils.ApiUrls.course, valid_data_01)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['course_number'], valid_data_01['course_number'])
        self.assertEqual(response.data['name'], valid_data_01['name'])

        data_id = response.data['id']

        # Convener should allow to edit
        response = self.convener.put(utils.ApiUrls.course + str(data_id) + '/', valid_data_02)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['course_number'], valid_data_02['course_number'])
        self.assertEqual(response.data['name'], valid_data_02['name'])

        # Convener should allow to edit
        response = self.convener.patch(utils.ApiUrls.course + str(data_id) + '/', valid_data_01)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['course_number'], valid_data_01['course_number'])
        self.assertEqual(response.data['name'], valid_data_01['name'])

        # Convener should allow to delete
        response = self.convener.delete(utils.ApiUrls.course + str(data_id) + '/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.convener.get(utils.ApiUrls.course + str(data_id) + '/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
