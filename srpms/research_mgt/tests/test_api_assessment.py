from django.test import TestCase
from rest_framework import status

from . import utils
from . import data


def assert_assessment_response(test_case: TestCase, response, true_data) -> None:
    if response.data.get('id', False):
        raise AttributeError("Please remove id before passing data into this function")

    # Not check-able
    test_case.assertTrue(response.data.pop('template_info') is not None)
    test_case.assertTrue(response.data.pop('assessment_examine') is not None)

    test_case.assertEqual(response.data, true_data)


class IndividualProject(utils.SrpmsTest):
    def setUp(self):
        super(IndividualProject, self).setUp()

        response = self.user_01.post(utils.ApiUrls.contract, data.contract_01_request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.contract = response.data

        self.assessment_list_url = utils.get_assessment_url(self.contract['id'])

        # Get assessment item to prepare for testing
        self.assessment_report_url = None
        for ass in response.data['assessment']:
            if ass['template_info']['name'] == 'report':
                self.assessment_report_url = utils.get_assessment_url(
                        self.contract['id'], ass['id'])
        self.assertTrue(self.assessment_report_url)

        # Assign supervisor for the contract
        req, resp = data.gen_supervise_req_resp(self.contract['id'],
                                                self.supervisor_formal.id, True)
        response = self.user_01.post(utils.get_supervise_url(self.contract['id']), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_owner_create_assessment(self):
        """Owner is not allowed to create new assessments"""
        req, resp = data.get_assessment(self.contract['id'])
        response = self.user_01.post(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_edit_assessment_valid(self):
        """Owner is allowed to update assessment, but not its template"""
        req = {'weight': 60, 'additional_description': 'asdfqwer'}
        response = self.user_01.put(self.assessment_report_url, req)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.user_01.patch(self.assessment_report_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['weight'], req['weight'])
        self.assertEqual(response.data['additional_description'], req['additional_description'])

    def test_owner_edit_assessment_invalid(self):
        """Owner is allowed to update assessment, but not its template"""
        req, resp = data.get_assessment(self.contract['id'])
        response = self.user_01.put(self.assessment_report_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_users_create_assessment(self):
        """Other users are not allowed to create new assessments"""
        req, resp = data.get_assessment(self.contract['id'])

        response = self.user_02.post(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.convener.post(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.supervisor_formal.post(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_users_edit_assessment(self):
        """Other users are not allowed to edit assessments"""
        req, resp = data.get_assessment(self.contract['id'])

        response = self.user_02.put(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.convener.put(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.supervisor_formal.put(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.user_02.patch(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.convener.patch(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.supervisor_formal.patch(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_assessment(self):
        """Almost no one is not allowed to delete assessment"""
        response = self.user_01.delete(self.assessment_report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.user_02.delete(self.assessment_report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.supervisor_formal.delete(self.assessment_report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.convener.delete(self.assessment_report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_create_assessment(self):
        """Superuser is allowed to create new assessments"""
        req, resp = data.get_assessment(self.contract['id'])

        response = self.superuser.post(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_superuser_edit_assessment(self):
        """Superuser is allowed to create new assessments"""
        req, resp = data.get_assessment(self.contract['id'])

        response = self.superuser.put(self.assessment_report_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.superuser.patch(self.assessment_report_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_superuser_delete_assessment(self):
        """Superuser is allowed to delete assessments"""
        response = self.superuser.delete(self.assessment_report_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.superuser.get(self.assessment_report_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SpecialTopic(utils.SrpmsTest):
    def setUp(self):
        super(SpecialTopic, self).setUp()

        response = self.user_01.post(utils.ApiUrls.contract, data.contract_02_request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.contract = response.data

        self.assessment_list_url = utils.get_assessment_url(self.contract['id'])

        # Assign supervisor for the contract
        req, resp = data.gen_supervise_req_resp(self.contract['id'],
                                                self.supervisor_formal.id, True)
        response = self.user_01.post(utils.get_supervise_url(self.contract['id']), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create an assessment item for the contract
        req, resp = data.get_assessment(self.contract['id'])
        response = self.user_01.post(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assessment_custom_url = utils.get_assessment_url(self.contract['id'],
                                                              response.data['id'])

    def test_owner_create_assessment(self):
        """Owner is allowed to create new assessments"""
        req, resp = data.get_assessment(self.contract['id'])
        response = self.user_01.post(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response.data.pop('id')
        assert_assessment_response(self, response, resp)

    def test_owner_edit_assessment(self):
        """Owner is allowed to update assessment"""
        req, resp = data.assessment_02_request, data.assessment_02_response
        resp['contract'] = self.contract['id']

        response = self.user_01.put(self.assessment_custom_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.data.pop('id')
        assert_assessment_response(self, response, resp)

        response = self.user_01.patch(self.assessment_custom_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.data.pop('id')
        assert_assessment_response(self, response, resp)

    def test_owner_delete_assessment(self):
        """Owner is allowed to delete assessment"""
        response = self.user_01.delete(self.assessment_custom_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.user_01.get(self.assessment_custom_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_users_create_assessment(self):
        """Other users are not allowed to create new assessments"""
        req, resp = data.get_assessment(self.contract['id'])

        response = self.user_02.post(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.convener.post(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.supervisor_formal.post(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_users_edit_assessment(self):
        """Other users are not allowed to edit assessments"""
        req, resp = data.get_assessment(self.contract['id'])

        response = self.user_02.put(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.convener.put(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.supervisor_formal.put(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.user_02.patch(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.convener.patch(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.supervisor_formal.patch(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_assessment(self):
        """Almost no one is not allowed to delete assessment"""
        response = self.user_02.delete(self.assessment_custom_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.supervisor_formal.delete(self.assessment_custom_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.convener.delete(self.assessment_custom_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_create_assessment(self):
        """Superuser is allowed to create new assessments"""
        req, resp = data.get_assessment(self.contract['id'])

        response = self.superuser.post(self.assessment_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_superuser_edit_assessment(self):
        """Superuser is allowed to create new assessments"""
        req, resp = data.assessment_02_request, data.assessment_02_response
        resp['contract'] = self.contract['id']

        response = self.superuser.put(self.assessment_custom_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.superuser.patch(self.assessment_custom_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_superuser_delete_assessment(self):
        """Superuser is allowed to delete assessments"""
        response = self.superuser.delete(self.assessment_custom_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.superuser.get(self.assessment_custom_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
