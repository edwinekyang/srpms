from django.test import TestCase
from rest_framework import status

from . import utils
from . import data


def assert_contract_response(test_case: TestCase, response, true_data) -> None:
    if response.data.get('id', False):
        raise AttributeError("Please remove id before passing data into this function")

    # Not check-able
    test_case.assertTrue(response.data.pop('create_date'))
    test_case.assertTrue(response.data.pop('supervise') is not None)
    test_case.assertTrue(response.data.pop('assessment') is not None)
    test_case.assertTrue(response.data.pop('was_submitted') is not None)

    # Contract should at least have one supervisor, otherwise is_all_supervisors_approved
    # would be false. Contract test also does not approve any supervise relation, as such
    # is_all_supervisors_approved should always be False.
    test_case.assertFalse(response.data.pop('is_all_supervisors_approved'))

    # Contract should at least have one assessment, otherwise is_all_assessments_approved
    # would be false. Contract test also does not approve any assessment method, as such
    # is_all_assessments_approved should always be False.
    test_case.assertFalse(response.data.pop('is_all_assessments_approved'))

    test_case.assertEqual(response.data, true_data)


class TestContract(utils.SrpmsTest):
    def set_submit(self, operator: utils.User, contract_id: int) -> None:
        """Submit the contract given an contract id"""

        response = operator.get(utils.get_contract_url(contract_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contract = response.data

        # Set supervisor if does not have any
        if not contract['supervise']:
            req, _ = data.gen_supervise_req_resp(contract_id, self.supervisor_non_formal.id,
                                                 is_formal=True)
            response = self.superuser.post(utils.get_supervise_url(contract_id), req)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        # Set assessment if does not have any
        if not contract['assessment']:
            response = operator.post(utils.get_assessment_url(contract_id),
                                     data.assessment_custom_request)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)

        # Set submit
        response = operator.put(utils.get_contract_url(contract_id, submit=True),
                                data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def set_unsubmit(self, contract_id: int) -> None:
        response = self.superuser.put(utils.get_contract_url(contract_id, submit=True),
                                      data.get_submit_data(False))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_POST(self):
        # User should allowed to create valid contract
        for con_req, con_resp in data.get_contracts(owner=self.user_01):
            response = self.user_01.post(utils.ApiUrls.contract, con_req)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            con_id = response.data.pop('id')
            self.assertTrue(con_id)
            assert_contract_response(self, response, con_resp)

        for con_req in data.contract_list_valid:
            response = self.user_01.post(utils.ApiUrls.contract, con_req)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_POST_permission(self):
        con_req, con_resp = data.get_contract(owner=self.user_01)

        ########################################
        # Normal user requests
        response = self.user_01.post(utils.ApiUrls.contract, con_req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ########################################
        # Supervisor (approved) requests
        response = self.supervisor_formal.post(utils.ApiUrls.contract, con_req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ########################################
        # Convener requests
        response = self.convener.post(utils.ApiUrls.contract, con_req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ########################################
        # Superuser requests
        response = self.superuser.post(utils.ApiUrls.contract, con_req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_PUT(self):
        con_req, con_resp = data.get_contract(owner=self.user_01)

        # Create first
        response = self.user_01.post(utils.ApiUrls.contract, con_req)
        con_id = response.data.pop('id')

        # Legal modification
        con_req['year'] = 2050
        con_resp['year'] = 2050
        response = self.user_01.put(utils.get_contract_url(con_id),
                                    con_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        assert_contract_response(self, response, con_resp)

        # Illegal modification
        if con_req.get('special_topic', False):
            con_req['individual_project'] = {'title': 'fioe23', 'objectives': '',
                                             'description': ''}
            response = self.user_01.put(utils.get_contract_url(con_id),
                                        con_req)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                             'Contract of multiple types should not be allowed')
            con_req['individual_project'] = None

        # Illegal modification
        if con_req.get('individual_project', False):
            con_req['special_topic'] = {'title': 'fioe23', 'objectives': '', 'description': ''}
            response = self.user_01.put(utils.get_contract_url(con_id),
                                        con_req)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                             'Contract of multiple types should not be allowed')
            con_req['special_topic'] = None

        # Illegal modification
        con_req['special_topic'] = {'title': 'fioe23', 'objectives': '', 'description': ''}
        con_req['individual_project'] = {'title': 'fioe23', 'objectives': '', 'description': ''}
        response = self.user_01.put(utils.get_contract_url(con_id),
                                    con_req)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Contract of multiple types should not be allowed')

        # Illegal modification
        con_req['special_topic'] = None
        con_req['individual_project'] = None
        response = self.user_01.put(utils.get_contract_url(con_id),
                                    con_req)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Contract of no type should not be allowed')

    def test_PUT_permission(self):
        con_req, con_resp = data.get_contract(owner=self.user_01)

        # Create contract
        response = self.user_01.post(utils.ApiUrls.contract, con_req)
        con_id = response.data.pop('id')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ########################################
        # Non-owner requests
        response = self.user_02.put(utils.get_contract_url(con_id), con_req)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        ########################################
        # Supervisor requests

        # Add supervisor first
        response = self.superuser.post(utils.get_supervise_url(con_id),
                                       {'supervisor': self.supervisor_non_formal.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Illegal request
        response = self.supervisor_non_formal.put(utils.get_contract_url(con_id),
                                                  con_req)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # After submit, supervisor can see it, but still forbidden to edit
        self.set_submit(self.user_01, con_id)
        response = self.supervisor_non_formal.put(utils.get_contract_url(con_id),
                                                  con_req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.set_unsubmit(con_id)

        # Illegal request
        response = self.supervisor_formal.put(utils.get_contract_url(con_id), con_req)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND,
                         'Supervisor not involve in a contract should not be allowed to edit')

        ########################################
        # Convener requests, as there was submit attempt, the convener can see it
        response = self.convener.put(utils.get_contract_url(con_id), con_req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Superuser requests
        response = self.superuser.put(utils.get_contract_url(con_id), con_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         'Course convener should be allowed to edit')
        self.assertTrue(response.data.pop('id'))
        assert_contract_response(self, response, con_resp)

    def test_PATCH(self):
        con_req, con_resp = data.get_contract(owner=self.user_01)

        # Create first
        response = self.user_01.post(utils.ApiUrls.contract, con_req)
        con_id = response.data.pop('id')

        # Legal modification
        con_req['year'] = 2050
        con_resp['year'] = 2050
        response = self.user_01.patch(utils.get_contract_url(con_id),
                                      {'year': con_req['year']})
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         'Partial update with only a subset of fields should be allowed')
        self.assertTrue(response.data.pop('id'))
        assert_contract_response(self, response, con_resp)

        if con_req.get('special_topic', False):
            # Illegal modification
            response = self.user_01.put(utils.get_contract_url(con_id),
                                        {'individual_project': {'title': 'fioe23'}})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                             'Contract of multiple types should not be allowed')

            # Legal modification
            con_req['special_topic'] = {'title': 'cacier2', 'objectives': '', 'description': ''}
            con_resp['special_topic'] = {'title': 'cacier2', 'objectives': '', 'description': ''}
            response = self.user_01.patch(utils.get_contract_url(con_id),
                                          {'special_topic': {'title': 'cacier2',
                                                             'objectives': '',
                                                             'description': ''}})
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                             'Partial update of nested field should be allowed')
            self.assertTrue(response.data.pop('id'))
            assert_contract_response(self, response, con_resp)

        if con_req.get('individual_project', False):
            # Illegal modification
            response = self.user_01.put(utils.get_contract_url(con_id),
                                        {'special_topic': {'title': 'fioe23'}})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                             'Contract of multiple types should not be allowed')

            # Legal modification
            con_req['individual_project'] = {'title': 'fio123e23', 'objectives': '',
                                             'description': ''}
            con_resp['individual_project'] = {'title': 'fio123e23', 'objectives': '',
                                              'description': ''}
            response = self.user_01.patch(utils.get_contract_url(con_id),
                                          {'individual_project': {'title': 'fio123e23',
                                                                  'objectives': '',
                                                                  'description': ''}})
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                             'Partial update of nested field should be allowed')
            self.assertTrue(response.data.pop('id'))
            assert_contract_response(self, response, con_resp)

        # Illegal modification
        response = self.user_01.put(utils.get_contract_url(con_id),
                                    {'individual_project': {'objectives': ''},
                                     'special_topic': {'objectives': ''}})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Contract of multiple types should not be allowed')

        # Illegal modification
        response = self.user_01.put(utils.get_contract_url(con_id),
                                    {'individual_project': None, 'special_topic': None})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Contract of no type should not be allowed')

        # Illegal modification
        con_req['special_topic'] = None
        con_req['individual_project'] = None
        response = self.user_01.put(utils.get_contract_url(con_id),
                                    con_req)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Contract of no type should not be allowed')

    def test_PATCH_permission(self):
        con_req, con_resp = data.get_contract(owner=self.user_01)

        # Create first
        response = self.user_01.post(utils.ApiUrls.contract, con_req)
        con_id = response.data.pop('id')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ########################################
        # Non-owner requests
        response = self.user_02.patch(utils.get_contract_url(con_id), con_req)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        ########################################
        # Supervisor requests

        # Illegal request
        self.set_submit(self.user_01, con_id)
        response = self.supervisor_non_formal.patch(utils.get_contract_url(con_id),
                                                    con_req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.set_unsubmit(con_id)

        # Illegal request
        response = self.supervisor_formal.patch(utils.get_contract_url(con_id), con_req)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND,
                         'Supervisor not involve in a contract should not be allowed to edit')

        ########################################
        # Convener requests
        response = self.convener.patch(utils.get_contract_url(con_id), con_req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Superuser requests
        response = self.superuser.patch(utils.get_contract_url(con_id), con_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertTrue(response.data.pop('id'))
        assert_contract_response(self, response, con_resp)

    def test_DELETE(self):
        con_req, con_resp = data.get_contract(owner=self.user_01)

        # Create first
        response = self.user_01.post(utils.ApiUrls.contract, con_req)
        con_id = response.data.pop('id')

        # Legal delete
        response = self.user_01.delete(utils.get_contract_url(con_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.user_01.get(utils.get_contract_url(con_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_DELETE_permission(self):
        con_req, con_resp = data.get_contract(owner=self.user_01)

        # Create first
        response = self.user_01.post(utils.ApiUrls.contract, con_req)
        con_id = response.data.pop('id')

        ########################################
        # Non-owner requests, they aren't able to see this contract
        response = self.user_02.delete(utils.get_contract_url(con_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        ########################################
        # Supervisor requests

        # Illegal
        self.set_submit(self.user_01, con_id)
        response = self.supervisor_non_formal.delete(utils.get_contract_url(con_id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.set_unsubmit(con_id)

        # Illegal
        response = self.supervisor_formal.delete(utils.get_contract_url(con_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        ########################################
        # Convener requests
        response = self.convener.delete(utils.get_contract_url(con_id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        ########################################
        # Superuser requests

        # Create again
        response = self.user_01.post(utils.ApiUrls.contract, con_req)
        con_id = response.data.pop('id')

        response = self.superuser.delete(utils.get_contract_url(con_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
