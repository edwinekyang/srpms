from django.test import TestCase
from rest_framework import status

from . import utils
from . import data


def assert_examine_response(test_case: TestCase, response, true_data) -> None:
    if response.data.get('id', False):
        raise AttributeError("Please remove id before passing data into this function")

    test_case.assertTrue(response.data.pop('examiner_approval_date') is None)

    test_case.assertEqual(response.data, true_data)


class IndividualProject(utils.SrpmsTest):
    def setUp(self):
        super(IndividualProject, self).setUp()

        # Create individual contract
        response = self.user_01.post(utils.ApiUrls.contract, data.contract_01_request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.contract = response.data

        # Get assessment item to prepare for testing
        assessment_report_id = None
        assessment_artifact_id = None
        for ass in response.data['assessment']:
            if ass['template_info']['name'] == 'report':
                assessment_report_id = ass['id']
            if ass['template_info']['name'] == 'artifact':
                assessment_artifact_id = ass['id']
        self.assertTrue(assessment_report_id)
        self.assertTrue(assessment_artifact_id)

        # Assign supervisor for the contract, note that here we deliberately assign a user
        # with no 'can_supervise' permission.
        req, resp = data.gen_supervise_req_resp(self.contract['id'],
                                                self.supervisor_non_formal.id, True)
        response = self.superuser.post(utils.get_supervise_url(self.contract['id']), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.supervise_id = response.data['id']

        # Let the user submit the contract, otherwise editing examiner is not allowed
        response = self.user_01.put(utils.get_contract_url(self.contract['id'], submit=True),
                                    data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        self.examine_list_url = utils.get_examine_url(self.contract['id'], assessment_report_id)

        # Pick assessment for test edit and delete
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_04.id)
        response = self.superuser.post(utils.get_examine_url(self.contract['id'],
                                                             assessment_artifact_id), req)
        examine_id = response.data['id']
        self.examine_detail_url = utils.get_examine_url(self.contract['id'], assessment_artifact_id,
                                                        examine_id)

    def test_supervisor_create_examiner(self):
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_04.id)

        # Supervisor should be able to assign examiner
        response = self.supervisor_non_formal.post(self.examine_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response.data.pop('id')
        assert_examine_response(self, response, resp)

        # Individual project should not allow more than one examiner
        req, _ = data.gen_examine_req_resp(examiner_id=self.user_03.id)
        response = self.supervisor_non_formal.post(self.examine_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_users_create_examiner(self):
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_04.id)

        # Contract owner should not be allowed
        response = self.user_01.post(self.examine_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Other people should not be allowed as well
        response = self.supervisor_formal.post(self.examine_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_convener_create_examiner(self):
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_04.id)

        # Convener is allowed to create
        response = self.convener.post(self.examine_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response.data.pop('id')
        assert_examine_response(self, response, resp)

        # Individual project should not allow more than one examiner
        req, _ = data.gen_examine_req_resp(examiner_id=self.user_03.id)
        response = self.convener.post(self.examine_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_create_examiner(self):
        # Superuser is allowed to create
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_04.id)
        response = self.superuser.post(self.examine_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response.data.pop('id')
        assert_examine_response(self, response, resp)

        # Superuser can assign more than one examiner to this contract
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_03.id)
        response = self.superuser.post(self.examine_list_url, req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response.data.pop('id')
        assert_examine_response(self, response, resp)

    def test_supervisor_PUT_examiner(self):
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_03.id)

        # Supervisor should be able to edit examiner
        response = self.supervisor_non_formal.put(self.examine_detail_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.data.pop('id')
        assert_examine_response(self, response, resp)

    def test_other_users_PUT_examiner(self):
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_03.id)

        # Contract owner not allow
        response = self.user_01.put(self.examine_detail_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 'can_supervise' but not supervisor not allowed
        response = self.supervisor_formal.put(self.examine_detail_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_convener_PUT_examiner(self):
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_03.id)

        # Convener should be able to edit
        response = self.convener.put(self.examine_detail_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.data.pop('id')
        assert_examine_response(self, response, resp)

    def test_superuser_PUT_examiner(self):
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_03.id)

        # Convener should be able to edit
        response = self.superuser.put(self.examine_detail_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.data.pop('id')
        assert_examine_response(self, response, resp)

    def test_supervisor_PATCH_examiner(self):
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_03.id)

        # Supervisor should be able to edit examiner
        response = self.supervisor_non_formal.patch(self.examine_detail_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.data.pop('id')
        assert_examine_response(self, response, resp)

    def test_other_users_PATCH_examiner(self):
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_03.id)

        # Contract owner not allow
        response = self.user_01.patch(self.examine_detail_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 'can_supervise' but not supervisor not allowed
        response = self.supervisor_formal.patch(self.examine_detail_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_convener_PATCH_examiner(self):
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_03.id)

        # Convener should be able to edit
        response = self.convener.patch(self.examine_detail_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.data.pop('id')
        assert_examine_response(self, response, resp)

    def test_superuser_PATCH_examiner(self):
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_03.id)

        # Convener should be able to edit
        response = self.superuser.patch(self.examine_detail_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.data.pop('id')
        assert_examine_response(self, response, resp)

    def test_supervisor_delete_examiner(self):
        # Supervisor should be able to delete examiner
        response = self.supervisor_non_formal.delete(self.examine_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.supervisor_non_formal.get(self.examine_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_users_delete_examiner(self):
        # Contract owner not allow
        response = self.user_01.delete(self.examine_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Examiner owner not allow
        response = self.user_04.delete(self.examine_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 'can_supervise' but not supervisor not allowed
        response = self.supervisor_formal.delete(self.examine_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_convener_delete_examiner(self):
        # Convener should be able to delete
        response = self.convener.delete(self.examine_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_superuser_delete_examiner(self):
        # Superuser should be able to delete
        response = self.superuser.delete(self.examine_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_assign_examiner_for_non_submitted_contract(self):
        # Disapprove to reset the submit status
        response = self.supervisor_non_formal.put(utils.get_supervise_url(self.contract['id'],
                                                                          self.supervise_id,
                                                                          approve=True),
                                                  data.get_approve_data(False))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        # Try to modify examiner, should failed
        req, _ = data.gen_examine_req_resp(examiner_id=self.user_03.id)
        response = self.convener.put(self.examine_detail_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assign_examiner_after_supervisor_approve(self):
        # Disapprove to reset the submit status
        response = self.supervisor_non_formal.put(utils.get_supervise_url(self.contract['id'],
                                                                          self.supervise_id,
                                                                          approve=True),
                                                  data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        req, _ = data.gen_examine_req_resp(examiner_id=self.user_03.id)
        response = self.supervisor_non_formal.put(self.examine_detail_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SpecialTopic(IndividualProject):
    """
    Inherit from individual project, since both of them can only have one examiner per assessment
    """

    def setUp(self):
        super(SpecialTopic, self).setUp()

        # Create special topic
        response = self.user_01.post(utils.ApiUrls.contract, data.contract_02_request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.contract = response.data

        assessment_list_url = utils.get_assessment_url(self.contract['id'])

        # Create assessment item to prepare for testing
        req = {'template': data.temp_custom.id, 'weight': 5}
        response = self.user_01.post(assessment_list_url, req)
        assessment_01_id = response.data['id']
        req = {'template': data.temp_custom.id, 'weight': 95}
        response = self.user_01.post(assessment_list_url, req)
        assessment_02_id = response.data['id']

        # Assign supervisor for the contract, note that here we deliberately assign a user
        # with no 'can_supervise' permission.
        req, resp = data.gen_supervise_req_resp(self.contract['id'],
                                                self.supervisor_non_formal.id, True)
        response = self.superuser.post(utils.get_supervise_url(self.contract['id']), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.supervise_id = response.data['id']

        # Let the user submit the contract, otherwise editing examiner is not allowed
        response = self.user_01.put(utils.get_contract_url(self.contract['id'], submit=True),
                                    data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        self.examine_list_url = utils.get_examine_url(self.contract['id'], assessment_01_id)

        # Pick assessment for test edit and delete
        req, resp = data.gen_examine_req_resp(examiner_id=self.user_04.id)
        response = self.superuser.post(utils.get_examine_url(self.contract['id'],
                                                             assessment_02_id), req)
        examine_id = response.data['id']
        self.examine_detail_url = utils.get_examine_url(self.contract['id'], assessment_02_id,
                                                        examine_id)
