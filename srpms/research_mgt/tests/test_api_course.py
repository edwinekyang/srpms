"""
Test course API, CRUD methods only.
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from rest_framework import status

from . import utils
from . import data


class TestCourse(utils.SrpmsTest):
    def test_POST(self):
        for cour in data.get_courses():
            response = self.convener.post(utils.ApiUrls.course, cour)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(response.data.pop('id'))
            self.assertTrue(response.data.pop('contract') is not None)
            self.assertEqual(response.data, cour)

        for cour in data.course_list_invalid:
            response = self.convener.post(utils.ApiUrls.course, cour)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_POST_permission(self):
        course = data.course_list_valid[0]
        course_another = data.course_list_valid[1]

        ########################################
        # Normal user requests
        response = self.user_01.post(utils.ApiUrls.course, course)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Supervisor (approved) requests
        response = self.supervisor_formal.post(utils.ApiUrls.course, course)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Convener requests
        response = self.convener.post(utils.ApiUrls.course, course)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.pop('id'))
        self.assertTrue(response.data.pop('contract') is not None)
        self.assertEqual(response.data, course)

        ########################################
        # Superuser requests
        response = self.superuser.post(utils.ApiUrls.course, course_another)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(response.data.pop('id'))
        self.assertTrue(response.data.pop('contract') is not None)
        self.assertEqual(response.data, course_another)

    def test_PUT(self):
        course = data.get_course()

        # Create first
        response = self.convener.post(utils.ApiUrls.course, course)
        course_id = response.data.pop('id')

        # Legal
        response = self.convener.put(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data.pop('id'))
        self.assertTrue(response.data.pop('contract') is not None)
        self.assertEqual(response.data, course)

        # Illegal
        for course in data.course_list_invalid:
            response = self.convener.put(utils.ApiUrls.course + str(course_id) + '/', course)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_PUT_permission(self):
        course = data.get_course()

        # Create first
        response = self.convener.post(utils.ApiUrls.course, course)
        course_id = response.data.pop('id')

        ########################################
        # Normal user requests
        response = self.user_01.put(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Supervisor (approved) requests
        response = self.supervisor_formal.put(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Convener requests
        response = self.convener.put(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        self.assertTrue(response.data.pop('contract') is not None)
        self.assertEqual(response.data, course)

        ########################################
        # Superuser requests
        response = self.superuser.put(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        self.assertTrue(response.data.pop('contract') is not None)
        self.assertEqual(response.data, course)

    def test_PATCH(self):
        course = data.get_course()

        # Create first
        response = self.convener.post(utils.ApiUrls.course, course)
        course_id = response.data.pop('id')

        # Legal
        response = self.convener.patch(utils.ApiUrls.course + str(course_id) + '/',
                                       {'course_number': course['course_number']})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data.pop('id'))
        self.assertTrue(response.data.pop('contract') is not None)
        self.assertEqual(response.data, course)

        # Legal
        response = self.convener.patch(utils.ApiUrls.course + str(course_id) + '/',
                                       {'name': course['name']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        self.assertTrue(response.data.pop('contract') is not None)
        self.assertEqual(response.data, course)

        # Illegal
        for course in data.course_list_invalid:
            response = self.convener.put(utils.ApiUrls.course + str(course_id) + '/', course)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_PATCH_permission(self):
        course = data.get_course()

        # Create first
        response = self.convener.post(utils.ApiUrls.course, course)
        course_id = response.data.pop('id')

        ########################################
        # Normal user requests
        response = self.user_01.patch(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Supervisor (approved) requests
        response = self.supervisor_formal.patch(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Convener requests
        response = self.convener.patch(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        self.assertTrue(response.data.pop('contract') is not None)
        self.assertEqual(response.data, course)

        ########################################
        # Superuser requests
        response = self.superuser.patch(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        self.assertTrue(response.data.pop('contract') is not None)
        self.assertEqual(response.data, course)

    def test_DELETE(self):
        course = data.get_course()

        # Create first
        response = self.convener.post(utils.ApiUrls.course, course)
        course_id = response.data.pop('id')

        response = self.convener.delete(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.convener.delete(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_DELETE_permission(self):
        course = data.get_course()

        # Create first
        response = self.convener.post(utils.ApiUrls.course, course)
        course_id = response.data.pop('id')

        ########################################
        # Normal user requests
        response = self.user_01.delete(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Supervisor (approved) requests
        response = self.supervisor_formal.delete(utils.ApiUrls.course + str(course_id) + '/',
                                                 course)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Convener requests
        response = self.convener.delete(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.convener.delete(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        ########################################
        # Superuser requests

        # Create again
        response = self.convener.post(utils.ApiUrls.course, course)
        course_id = response.data.pop('id')

        response = self.convener.delete(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.convener.delete(utils.ApiUrls.course + str(course_id) + '/', course)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
