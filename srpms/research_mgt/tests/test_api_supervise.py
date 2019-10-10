"""
Test supervise API, CRUD methods only, does not involve view set actions.
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from django.test import TestCase
from rest_framework import status

from . import utils
from . import data


def assert_supervise_response(test_case: TestCase, response, true_data) -> None:
    if response.data.get('id', False):
        raise AttributeError("Please remove id before passing data into this function")

    # Not check-able
    test_case.assertTrue(response.data.pop('supervisor_approval_date') is None)
    test_case.assertTrue(response.data.pop('nominator'))

    # We'll test approval in other tests
    test_case.assertFalse(response.data.pop('is_supervisor_approved'))

    test_case.assertEqual(response.data, true_data)


class TestSupervise(utils.SrpmsTest):
    def setUp(self):
        super(TestSupervise, self).setUp()

        # Create individual contract
        response = self.user_01.post(utils.ApiUrls.contract, data.contract_01_request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.contract_individual = response.data

        # Create special topic contract
        response = self.user_02.post(utils.ApiUrls.contract, data.contract_02_request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.contract_special = response.data

    def test_POST_individual_owner(self):
        """Test POST method for individual project from contract owner"""
        contract_id = self.contract_individual['id']

        # Owner should not be allowed to nominate un-approved supervisor
        req, _ = data.gen_supervise_req_resp(contract_id, self.supervisor_non_formal.id, False)
        response = self.user_01.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Owner should be allowed to nominate approved supervisor
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_formal.id, True)
        response = self.user_01.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

        # Individual contract should not be allow to have more than one supervisor
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_formal.id, True)
        response = self.user_01.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_POST_individual_others(self):
        """Test POST method for individual project from other users"""
        contract_id = self.contract_individual['id']

        # Other user should not be allowed to nominate
        req, _ = data.gen_supervise_req_resp(contract_id, self.supervisor_formal.id, False)
        response = self.user_02.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.supervisor_formal.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.convener.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_POST_individual_superuser(self):
        """Test POST method for individual project from superuser"""
        contract_id = self.contract_individual['id']

        # Superuser should be allowed to nominate anyone
        req, resp = data.gen_supervise_req_resp(contract_id, self.user_03.id, False)
        response = self.superuser.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

        # Individual contract should not be allow to have more than one supervisor
        req, resp = data.gen_supervise_req_resp(contract_id, self.user_04.id, False)
        response = self.user_01.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_POST_special_owner(self):
        """Test POST method for special topic from contract owner"""
        contract_id = self.contract_special['id']

        # Owner should not be allowed to nominate un-approved supervisor
        req, _ = data.gen_supervise_req_resp(contract_id, self.supervisor_non_formal.id, False)
        response = self.user_02.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Owner should be allowed to nominate approved supervisor
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_formal.id, True)
        response = self.user_02.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

    def test_POST_special_others(self):
        """Test POST method for special topic from other users"""
        contract_id = self.contract_special['id']

        # Other user should not be allowed to nominate
        req, _ = data.gen_supervise_req_resp(contract_id, self.supervisor_formal.id, False)
        response = self.user_01.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.supervisor_formal.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.convener.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_POST_special_superuser(self):
        """Test POST method for special topic from super user"""
        contract_id = self.contract_special['id']

        # Superuser should be allowed to nominate anyone
        req, resp = data.gen_supervise_req_resp(contract_id, self.user_03.id, False)
        response = self.superuser.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

    def test_PUT_individual(self):
        """Test PUT method on individual project"""
        contract_id = self.contract_individual['id']

        # Create a supervise relation first
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_formal.id, True)
        response = self.user_01.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        supervise_id = response.data.pop('id')
        self.assertTrue(supervise_id)

        supervise_url = utils.get_supervise_url(contract_id, supervise_id)

        # Contract owner is allowed to edit supervisor
        response = self.user_01.put(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

        # Others are not allowed to edit
        response = self.user_02.put(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.convener.put(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Contract formal supervisor is allowed to edit
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_non_formal.id, False)
        response = self.supervisor_formal.put(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

        # Contract non-formal supervisor is allowed to edit
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_formal.id, True)
        response = self.supervisor_formal.put(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Superuser is allowed to edit supervisor
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_non_formal.id, False)
        response = self.superuser.put(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

    def test_PUT_special(self):
        """Test PUT method on special topic"""
        contract_id = self.contract_special['id']

        # Create a supervise relation first
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_formal.id, True)
        response = self.user_02.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        supervise_id = response.data.pop('id')
        self.assertTrue(supervise_id)

        supervise_url = utils.get_supervise_url(contract_id, supervise_id)

        # Contract owner is allowed to edit supervisor
        response = self.user_02.put(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

        # Others are not allowed to edit
        response = self.user_01.put(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.convener.put(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Contract formal supervisor is allowed to edit
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_non_formal.id, False)
        response = self.supervisor_formal.put(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

        # Contract non-formal supervisor is allowed to edit
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_formal.id, True)
        response = self.supervisor_formal.put(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Superuser is allowed to edit supervisor
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_non_formal.id, False)
        response = self.superuser.put(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

    def test_PATCH_individual(self):
        """Test PATCH method on individual project"""
        contract_id = self.contract_individual['id']

        # Create a supervise relation first
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_formal.id, True)
        response = self.user_01.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        supervise_id = response.data.pop('id')
        self.assertTrue(supervise_id)

        supervise_url = utils.get_supervise_url(contract_id, supervise_id)

        # Contract owner is allowed to edit supervisor
        response = self.user_01.patch(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

        # Others are not allowed to edit
        response = self.user_02.patch(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.convener.patch(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Contract formal supervisor is allowed to edit
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_non_formal.id, False)
        response = self.supervisor_formal.patch(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

        # Contract non-formal supervisor is allowed to edit
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_formal.id, True)
        response = self.supervisor_formal.patch(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Superuser is allowed to edit supervisor
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_non_formal.id, False)
        response = self.superuser.patch(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

    def test_PATCH_special(self):
        """Test PATCH method on special topic"""
        contract_id = self.contract_special['id']

        # Create a supervise relation first
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_formal.id, True)
        response = self.user_02.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        supervise_id = response.data.pop('id')
        self.assertTrue(supervise_id)

        supervise_url = utils.get_supervise_url(contract_id, supervise_id)

        # Contract owner is allowed to edit supervisor
        response = self.user_02.patch(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

        # Others are not allowed to edit
        response = self.user_01.patch(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.convener.patch(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Contract formal supervisor is allowed to edit
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_non_formal.id, False)
        response = self.supervisor_formal.patch(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

        # Contract non-formal supervisor is allowed to edit
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_formal.id, True)
        response = self.supervisor_formal.patch(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Superuser is allowed to edit supervisor
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_non_formal.id, False)
        response = self.superuser.patch(supervise_url, req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        assert_supervise_response(self, response, resp)

    def test_DELETE_individual(self):
        """Test DELETE method on individual project"""
        contract_id = self.contract_individual['id']

        # Create a supervise relation
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_non_formal.id, True)
        response = self.superuser.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        supervise_url = utils.get_supervise_url(contract_id, response.data['id'])

        # Contract owner is allowed to deleted
        response = self.user_01.delete(supervise_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.user_01.delete(supervise_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Create a supervise relation
        response = self.superuser.post(utils.get_supervise_url(contract_id), req)
        supervise_url = utils.get_supervise_url(contract_id, response.data['id'])

        # Other users are not allowed to deleted
        response = self.user_02.delete(supervise_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.convener.delete(supervise_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.supervisor_formal.delete(supervise_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Superuser is allowed to delete
        response = self.superuser.delete(supervise_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.superuser.delete(supervise_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_DELETE_special(self):
        """Test DELETE method on special topic"""
        contract_id = self.contract_special['id']

        # Create a supervise relation
        req, resp = data.gen_supervise_req_resp(contract_id, self.supervisor_non_formal.id, True)
        response = self.superuser.post(utils.get_supervise_url(contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        supervise_url = utils.get_supervise_url(contract_id, response.data['id'])

        # Contract owner is allowed to deleted
        response = self.user_02.delete(supervise_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.user_02.delete(supervise_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Create a supervise relation
        response = self.superuser.post(utils.get_supervise_url(contract_id), req)
        supervise_url = utils.get_supervise_url(contract_id, response.data['id'])

        # Other users are not allowed to deleted
        response = self.user_01.delete(supervise_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.convener.delete(supervise_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.supervisor_formal.delete(supervise_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Superuser is allowed to delete
        response = self.superuser.delete(supervise_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.superuser.delete(supervise_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
