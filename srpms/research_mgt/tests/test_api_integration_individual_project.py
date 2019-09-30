from rest_framework import status

from . import utils
from . import data


class IndividualProject(utils.SrpmsTest):
    def set_submit(self):
        response = self.user_01.put(utils.get_contract_url(self.contract_id, submit=True),
                                    data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    def set_supervise(self):
        # Assign supervisor for the contract, note that here we deliberately assign a user
        # with no 'can_supervise' permission.
        req, resp = data.gen_supervise_req_resp(self.contract['id'],
                                                self.supervisor_non_formal.id, True)
        response = self.superuser.post(utils.get_supervise_url(self.contract['id']), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.supervise_id = response.data['id']

        self.supervise_approve_url = utils.get_supervise_url(self.contract_id, self.supervise_id,
                                                             approve=True)

    def set_examine(self):
        # Before nominate examiner, the contract must be submitted and is approved by supervisor
        self.set_submit()
        self.set_supervise()

        # Retrieving assessment examine id in prepare for testing examiner approval
        self.assess_report_id = None
        self.assess_artifact_id = None
        self.assess_present_id = None
        self.examine_report_id = None
        self.examine_artifact_id = None
        self.examine_present_id = None
        for assessment in self.contract['assessment']:
            if assessment['template_info']['name'] == 'report':
                self.assess_report_id = assessment['id']
                req, _ = data.gen_examine_req_resp(self.user_04.id)
                response = self.supervisor_non_formal.post(
                        utils.get_examine_url(self.contract_id, self.assess_report_id), req)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
                self.examine_report_id = response.data['id']
            elif assessment['template_info']['name'] == 'artifact':
                self.assess_artifact_id = assessment['id']
                req, _ = data.gen_examine_req_resp(self.user_04.id)
                response = self.supervisor_non_formal.post(
                        utils.get_examine_url(self.contract_id, self.assess_artifact_id), req)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
                self.examine_artifact_id_id = response.data['id']
            elif assessment['template_info']['name'] == 'presentation':
                self.assess_present_id = assessment['id']
                req, _ = data.gen_examine_req_resp(self.user_04.id)
                response = self.supervisor_non_formal.post(
                        utils.get_examine_url(self.contract_id, self.assess_present_id), req)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
                self.examine_present_id = response.data['id']

    def setUp(self):
        super(IndividualProject, self).setUp()

        # Create a contract
        response = self.user_01.post(utils.ApiUrls.contract, data.contract_01_request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.contract = response.data
        self.contract_id = self.contract['id']

    ########################################
    # Contract submission

    def test_owner_submit_illegal_method(self):
        # No POST
        response = self.user_01.post(utils.get_contract_url(self.contract_id, submit=True),
                                     data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.content)

        # No DELETE
        response = self.user_01.delete(utils.get_contract_url(self.contract_id, submit=True),
                                       data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.content)

    def test_owner_submit_without_supervisor(self):  # Forbidden
        response = self.user_01.put(utils.get_contract_url(self.contract_id, submit=True),
                                    data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

    def test_owner_submit_legal_01(self):
        self.set_supervise()
        # Allow PUT
        response = self.user_01.put(utils.get_contract_url(self.contract_id, submit=True),
                                    data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    def test_owner_submit_legal_02(self):
        self.set_supervise()
        # Allow PATCH
        response = self.user_01.patch(utils.get_contract_url(self.contract_id, submit=True),
                                      data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    def test_owner_resubmit(self):  # Forbidden
        self.set_supervise()

        response = self.user_01.put(utils.get_contract_url(self.contract_id, submit=True),
                                    data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        response = self.user_01.put(utils.get_contract_url(self.contract_id, submit=True),
                                    data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

    def test_owner_un_submit(self):  # Forbidden
        self.set_supervise()

        response = self.user_01.put(utils.get_contract_url(self.contract_id, submit=True),
                                    data.get_submit_data(False))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

    def test_other_users_submit(self):  # Forbidden
        self.set_supervise()

        # Forbid other users
        response = self.user_02.put(utils.get_contract_url(self.contract_id, submit=True),
                                    data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

        # Forbid supervisor
        response = self.supervisor_non_formal.put(
                utils.get_contract_url(self.contract_id, submit=True),
                data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

        # Forbid supervisor
        response = self.supervisor_formal.put(utils.get_contract_url(self.contract_id, submit=True),
                                              data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

        # Forbid convener
        response = self.convener.put(utils.get_contract_url(self.contract_id, submit=True),
                                     data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

        # Allow superuser
        response = self.superuser.put(utils.get_contract_url(self.contract_id, submit=True),
                                      data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        response = self.superuser.put(utils.get_contract_url(self.contract_id, submit=True),
                                      data.get_submit_data(False))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    ########################################
    # Contract supervisor approval

    def test_supervise_approve_illegal_method(self):
        self.set_supervise()
        self.set_submit()

        # No POST
        response = self.superuser.post(self.supervise_approve_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.content)

        # No DELETE
        response = self.superuser.delete(self.supervise_approve_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.content)

    def test_supervise_approve_legal_01(self):
        self.set_supervise()
        self.set_submit()

        # Allow PUT
        response = self.superuser.put(self.supervise_approve_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    def test_supervise_approve_legal_02(self):
        self.set_supervise()
        self.set_submit()

        # Allow DELETE
        response = self.superuser.patch(self.supervise_approve_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    def test_supervise_reapprove(self):
        self.set_supervise()
        self.set_submit()

        response = self.supervisor_non_formal.put(self.supervise_approve_url,
                                                  data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        # Forbid re-approval
        response = self.supervisor_non_formal.put(self.supervise_approve_url,
                                                  data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

    def test_supervise_approve_non_submitted_contract(self):
        self.set_supervise()

        # Un-submitted contract is not allowed to be approved
        response = self.supervisor_non_formal.put(self.supervise_approve_url,
                                                  data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)

    def test_supervise_approve_submitted_contract(self):
        self.set_supervise()
        self.set_submit()

        # Submitted contract is allowed to be approved
        response = self.supervisor_non_formal.put(self.supervise_approve_url,
                                                  data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    def test_supervise_disapprove_submitted_contract(self):
        self.set_supervise()
        self.set_submit()

        # Submitted contract is allowed to be disapproved
        response = self.supervisor_non_formal.put(self.supervise_approve_url,
                                                  data.get_approve_data(False))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        # Owner should be able to submit again
        self.set_submit()

    def test_other_users_approve(self):
        self.set_supervise()
        self.set_submit()

        # Forbid other user
        response = self.user_02.put(self.supervise_approve_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

        # Forbid can_supervise but unrelated supervisor
        response = self.supervisor_formal.put(self.supervise_approve_url,
                                              data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

        # Allow convener
        response = self.convener.put(self.supervise_approve_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        # Allow superuser
        response = self.superuser.put(self.supervise_approve_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    def test_other_users_disapprove(self):
        self.set_supervise()
        self.set_submit()

        # Forbid other user
        response = self.user_02.put(self.supervise_approve_url, data.get_approve_data(False))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

        # Forbid can_supervise but unrelated supervisor
        response = self.supervisor_formal.put(self.supervise_approve_url,
                                              data.get_approve_data(False))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

        # Allow convener
        response = self.convener.put(self.supervise_approve_url, data.get_approve_data(False))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        # Allow superuser
        self.set_submit()
        response = self.superuser.put(self.supervise_approve_url, data.get_approve_data(False))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    ########################################
    # Contract examiner approval

    ########################################
    # Contract convener approval

    def test_convener_approve_non_submitted_contract(self):
        # Un-submitted contract is not allowed to be approved
        response = self.convener.put(utils.get_contract_url(self.contract_id, approve=True),
                                     data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)


# class IndividualProjectAssessmentApprove(IndividualProject):
#     def setUp(self):
#         super(IndividualProjectAssessmentApprove, self).setUp()
#
#         for assessment in self.contract['assessment']:
#             req, _ = data.gen_examine_req_resp(self.user_03.id)
#             response = self.superuser.post(
#                     utils.get_examine_url(self.contract_id, assessment['id']), req)
#
#     def test_approve_put_patch_only(self):
#         # Submit the contract first, otherwise approve is not allowed
#         response = self.superuser.put(utils.get_contract_url(self.contract_id, submit=True),
#                                       data.get_submit_data(True))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         # No POST
#         response = self.superuser.post(utils.get_contract_url(self.contract_id, approve=True),
#                                        data.get_approve_data(True))
#         self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
#
#         # Allow PUT
#         response = self.superuser.put(utils.get_contract_url(self.contract_id, approve=True),
#                                       data.get_approve_data(True))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         # Allow PATCH
#         response = self.superuser.patch(utils.get_contract_url(self.contract_id, approve=True),
#                                         data.get_approve_data(True))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         # No DELETE
#         response = self.superuser.delete(utils.get_contract_url(self.contract_id, approve=True))
#         self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
