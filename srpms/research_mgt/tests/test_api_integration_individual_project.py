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
        """Assign examiner to every assessment of the contract, examiner is user_04"""

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
                self.examine_artifact_id = response.data['id']
            elif assessment['template_info']['name'] == 'presentation':
                self.assess_present_id = assessment['id']
                req, _ = data.gen_examine_req_resp(self.user_04.id)
                response = self.supervisor_non_formal.post(
                        utils.get_examine_url(self.contract_id, self.assess_present_id), req)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
                self.examine_present_id = response.data['id']
        self.assertTrue(self.assess_report_id)
        self.assertTrue(self.assess_artifact_id)
        self.assertTrue(self.assess_present_id)
        self.assertTrue(self.examine_report_id)
        self.assertTrue(self.examine_artifact_id)
        self.assertTrue(self.examine_present_id)

    def set_supervise_approve(self):
        # Supervisor approval
        response = self.supervisor_non_formal.put(self.supervise_approve_url,
                                                  data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def set_examiner_approve(self):
        # Before we can let examiner approve, we need to set examiners
        response = self.user_04.put(utils.get_examine_url(self.contract_id, self.assess_artifact_id,
                                                          self.examine_artifact_id, approve=True),
                                    data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user_04.put(utils.get_examine_url(self.contract_id, self.assess_report_id,
                                               self.examine_report_id, approve=True),
                         data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user_04.put(utils.get_examine_url(self.contract_id, self.assess_present_id,
                                               self.examine_present_id, approve=True),
                         data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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

        # Submit first
        self.user_01.put(utils.get_contract_url(self.contract_id, submit=True),
                         data.get_submit_data(True))

        # Try undo submit
        response = self.user_01.put(utils.get_contract_url(self.contract_id, submit=True),
                                    data.get_submit_data(False))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

    def test_other_users_submit(self):  # Forbidden
        self.set_supervise()

        # Forbid other users
        response = self.user_02.put(utils.get_contract_url(self.contract_id, submit=True),
                                    data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.content)

        # Forbid supervisor
        response = self.supervisor_non_formal.put(
                utils.get_contract_url(self.contract_id, submit=True),
                data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

        # Forbid supervisor
        response = self.supervisor_formal.put(utils.get_contract_url(self.contract_id, submit=True),
                                              data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.content)

        # Forbid convener
        response = self.convener.put(utils.get_contract_url(self.contract_id, submit=True),
                                     data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.content)

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
        self.set_examine()

        # No POST
        response = self.superuser.post(self.supervise_approve_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.content)

        # No DELETE
        response = self.superuser.delete(self.supervise_approve_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED, response.content)

    def test_supervise_approve_legal_01(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()

        # Allow PUT
        response = self.superuser.put(self.supervise_approve_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    def test_supervise_approve_legal_02(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()

        # Allow PATCH
        response = self.superuser.patch(self.supervise_approve_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    def test_supervise_reapprove(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()

        response = self.supervisor_non_formal.put(self.supervise_approve_url,
                                                  data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        # Forbid re-approval
        response = self.supervisor_non_formal.put(self.supervise_approve_url,
                                                  data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

    def test_supervise_approve_without_examiner(self):
        self.set_supervise()
        self.set_submit()

        response = self.supervisor_non_formal.put(self.supervise_approve_url,
                                                  data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_supervise_approve_non_submitted_contract(self):
        self.set_supervise()

        # Un-submitted contract is not allowed to be approved
        response = self.supervisor_non_formal.put(self.supervise_approve_url,
                                                  data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

    def test_supervise_approve_submitted_contract(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()

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

    def test_supervise_disapprove_non_submitted_contract(self):
        self.set_supervise()

        # Un-submitted contract is not allowed to be disapproved
        response = self.supervisor_non_formal.put(self.supervise_approve_url,
                                                  data.get_approve_data(False))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

        # Owner should be able to submit again
        self.set_submit()

    def test_other_users_approve_supervisor(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()

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

    def test_other_users_disapprove_supervisor(self):
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

    def test_examiner_approve_illegal_method(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()

        response = self.superuser.post(utils.get_examine_url(self.contract_id,
                                                             self.assess_report_id,
                                                             self.examine_report_id, approve=True),
                                       data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.superuser.delete(utils.get_examine_url(self.contract_id,
                                                               self.assess_report_id,
                                                               self.examine_report_id,
                                                               approve=True))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_examiner_approve_legal_01(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()

        response = self.user_04.put(utils.get_examine_url(self.contract_id,
                                                          self.assess_report_id,
                                                          self.examine_report_id, approve=True),
                                    data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_examiner_approve_legal_02(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()

        response = self.user_04.patch(utils.get_examine_url(self.contract_id,
                                                            self.assess_artifact_id,
                                                            self.examine_artifact_id, approve=True),
                                      data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_examiner_reapprove(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()

        response = self.user_04.put(utils.get_examine_url(self.contract_id,
                                                          self.assess_report_id,
                                                          self.examine_report_id, approve=True),
                                    data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.user_04.put(utils.get_examine_url(self.contract_id,
                                                          self.assess_report_id,
                                                          self.examine_report_id, approve=True),
                                    data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_examiner_disapprove(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()

        response = self.user_04.put(utils.get_examine_url(self.contract_id,
                                                          self.assess_report_id,
                                                          self.examine_report_id, approve=True),
                                    data.get_approve_data(False))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    def test_other_users_approve_examiner(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()

        examine_url = utils.get_examine_url(self.contract_id, self.assess_report_id,
                                            self.examine_report_id, approve=True)

        # Forbid normal user
        response = self.user_01.put(examine_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Forbid un-related can_supervise
        response = self.supervisor_formal.put(examine_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Allow convener
        response = self.convener.put(examine_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Allow superuser
        self.superuser.put(examine_url, data.get_approve_data(False))
        response = self.superuser.put(examine_url, data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)
        # Nominator disapprove would clear the supervisor (who nominate this examiner)'s approval,
        # and examiner cannot approve before supervisor approve, thus bad request

    def test_other_users_disapprove_examiner(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()

        examine_url = utils.get_examine_url(self.contract_id, self.assess_report_id,
                                            self.examine_report_id, approve=True)

        # Forbid normal user
        response = self.user_01.put(examine_url, data.get_approve_data(False))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Forbid un-related can_supervise
        response = self.supervisor_formal.put(examine_url, data.get_approve_data(False))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Allow convener
        response = self.convener.put(examine_url, data.get_approve_data(False))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Allow superuser
        response = self.superuser.put(examine_url, data.get_approve_data(False))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    ########################################
    # Contract convener approval

    def test_convener_approve_illegal_method(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()
        self.set_examiner_approve()

        response = self.superuser.post(utils.get_contract_url(self.contract_id, approve=True),
                                       data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.superuser.delete(utils.get_contract_url(self.contract_id, approve=True),
                                         data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_convener_approve_legal_01(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()
        self.set_examiner_approve()

        response = self.superuser.put(utils.get_contract_url(self.contract_id, approve=True),
                                      data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_convener_approve_legal_02(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()
        self.set_examiner_approve()

        response = self.superuser.patch(utils.get_contract_url(self.contract_id, approve=True),
                                        data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_convener_reapprove(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()
        self.set_examiner_approve()

        response = self.convener.put(utils.get_contract_url(self.contract_id, approve=True),
                                     data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.convener.put(utils.get_contract_url(self.contract_id, approve=True),
                                     data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_convener_approve_non_submitted_contract(self):
        """Contract supervisor is set, but contract hasn't been submitted"""
        self.set_supervise()

        response = self.convener.put(utils.get_contract_url(self.contract_id, approve=True),
                                     data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_convener_approve_non_supervisor_approve_contract(self):
        """
        Contract supervisor is set, and contract is submitted, but contract supervisor hasn't
        approve the contract.
        """
        self.set_supervise()
        self.set_submit()

        response = self.convener.put(utils.get_contract_url(self.contract_id, approve=True),
                                     data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_convener_approve_non_examiner_approve_contract(self):
        """
        Contract supervisor is set, contract is submitted, and contract supervisor approved
        the contract. However not all of the assessments have been approved by examiners.
        """
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()

        response = self.convener.put(utils.get_contract_url(self.contract_id, approve=True),
                                     data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_convener_approve_contract(self):
        """All criteria for approving a contract has passed"""
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()
        self.set_examiner_approve()

        response = self.convener.put(utils.get_contract_url(self.contract_id, approve=True),
                                     data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_convener_disapprove_contract(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()
        self.set_examiner_approve()

        response = self.convener.put(utils.get_contract_url(self.contract_id, approve=True),
                                     data.get_approve_data(False))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_convener_disapprove_approved_contract(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()
        self.set_examiner_approve()

        response = self.convener.put(utils.get_contract_url(self.contract_id, approve=True),
                                     data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Un-submitted contract is not allowed to be approved
        response = self.convener.put(utils.get_contract_url(self.contract_id, approve=True),
                                     data.get_approve_data(False))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.content)

    def test_other_users_approve_convener(self):
        self.set_supervise()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()
        self.set_examiner_approve()

        # Contract owner
        response = self.user_01.put(utils.get_contract_url(self.contract_id, approve=True),
                                    data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Contract examiner
        response = self.user_04.put(utils.get_contract_url(self.contract_id, approve=True),
                                    data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Users with 'can_supervise' permission
        response = self.supervisor_formal.put(utils.get_contract_url(self.contract_id,
                                                                     approve=True),
                                              data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Contract supervisor
        response = self.supervisor_non_formal.put(utils.get_contract_url(self.contract_id,
                                                                         approve=True),
                                                  data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
