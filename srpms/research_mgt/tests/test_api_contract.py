from rest_framework import status

from . import utils
from . import data


class TestContract(utils.SrpmsTest):
    def test_POST(self):
        # User should allowed to create valid contract
        for con_req, con_resp in data.get_contracts(data.contract_list_valid,
                                                    owner=self.user_01):
            response = self.user_01.post(utils.ApiUrls.contract, con_req)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            con_id = response.data.pop('id')
            self.assertTrue(con_id)
            self.assertTrue(response.data.pop('create_date'))
            self.assertEqual(response.data, con_resp)

    def test_PUT(self):
        con_req, con_resp = data.get_contract(data.contract_list_valid, owner=self.user_01)

        # Create first
        response = self.user_01.post(utils.ApiUrls.contract, con_req)
        con_id = response.data.pop('id')

        # Legal modification
        con_req['year'] = 2050
        con_resp['year'] = 2050
        response = self.user_01.put(utils.ApiUrls.contract + str(con_id) + '/',
                                    con_req)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.pop('id'))
        self.assertTrue(response.data.pop('create_date'))
        self.assertEqual(response.data, con_resp)

        # Illegal modification
        if con_req['special_topics']:
            con_req['individual_project'] = {'title': 'fioe23', 'objectives': '',
                                             'description': ''}
            response = self.user_01.put(utils.ApiUrls.contract + str(con_id) + '/',
                                        con_req)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                             'Contract of multiple types should not be allowed')
            con_req['individual_project'] = None

        # Illegal modification
        if con_req['individual_project']:
            con_req['special_topics'] = {'title': 'fioe23', 'objectives': '', 'description': ''}
            response = self.user_01.put(utils.ApiUrls.contract + str(con_id) + '/',
                                        con_req)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                             'Contract of multiple types should not be allowed')
            con_req['special_topics'] = None

        # Illegal modification
        con_req['special_topics'] = {'title': 'fioe23', 'objectives': '', 'description': ''}
        con_req['individual_project'] = {'title': 'fioe23', 'objectives': '', 'description': ''}
        response = self.user_01.put(utils.ApiUrls.contract + str(con_id) + '/',
                                    con_req)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Contract of multiple types should not be allowed')

        # Illegal modification
        con_req['special_topics'] = None
        con_req['individual_project'] = None
        response = self.user_01.put(utils.ApiUrls.contract + str(con_id) + '/',
                                    con_req)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Contract of no type should not be allowed')

    def test_PATCH(self):
        con_req, con_resp = data.get_contract(data.contract_list_valid, owner=self.user_01)

        # Create first
        response = self.user_01.post(utils.ApiUrls.contract, con_req)
        con_id = response.data.pop('id')

        # Legal modification
        con_req['year'] = 2050
        con_resp['year'] = 2050
        response = self.user_01.patch(utils.ApiUrls.contract + str(con_id) + '/',
                                      {'year': con_req['year']})
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         'Partial update with only a subset of fields should be allowed')
        self.assertTrue(response.data.pop('id'))
        self.assertTrue(response.data.pop('create_date'))
        self.assertEqual(response.data, con_resp)

        if con_req['special_topics']:
            # Illegal modification
            response = self.user_01.put(utils.ApiUrls.contract + str(con_id) + '/',
                                        {'individual_project': {'title': 'fioe23'}})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                             'Contract of multiple types should not be allowed')

            # Legal modification
            con_req['special_topics'] = {'title': 'cacier2', 'objectives': '', 'description': ''}
            con_resp['special_topics'] = {'title': 'cacier2', 'objectives': '', 'description': ''}
            response = self.user_01.patch(utils.ApiUrls.contract + str(con_id) + '/',
                                          {'special_topics': {'title': 'cacier2',
                                                              'objectives': '',
                                                              'description': ''}})
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                             'Partial update of nested field should be allowed')
            self.assertTrue(response.data.pop('id'))
            self.assertTrue(response.data.pop('create_date'))
            self.assertEqual(response.data, con_resp)

        if con_req['individual_project']:
            # Illegal modification
            response = self.user_01.put(utils.ApiUrls.contract + str(con_id) + '/',
                                        {'special_topics': {'title': 'fioe23'}})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                             'Contract of multiple types should not be allowed')

            # Legal modification
            con_req['individual_project'] = {'title': 'fio123e23', 'objectives': '',
                                             'description': ''}
            con_resp['individual_project'] = {'title': 'fio123e23', 'objectives': '',
                                              'description': ''}
            response = self.user_01.patch(utils.ApiUrls.contract + str(con_id) + '/',
                                          {'individual_project': {'title': 'fio123e23',
                                                                  'objectives': '',
                                                                  'description': ''}})
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                             'Partial update of nested field should be allowed')
            self.assertTrue(response.data.pop('id'))
            self.assertTrue(response.data.pop('create_date'))
            self.assertEqual(response.data, con_resp)

        # Illegal modification
        response = self.user_01.put(utils.ApiUrls.contract + str(con_id) + '/',
                                    {'individual_project': {'objectives': ''},
                                     'special_topics': {'objectives': ''}})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Contract of multiple types should not be allowed')

        # Illegal modification
        response = self.user_01.put(utils.ApiUrls.contract + str(con_id) + '/',
                                    {'individual_project': None, 'special_topics': None})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Contract of no type should not be allowed')

        # Illegal modification
        con_req['special_topics'] = None
        con_req['individual_project'] = None
        response = self.user_01.put(utils.ApiUrls.contract + str(con_id) + '/',
                                    con_req)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Contract of no type should not be allowed')

    def test_DELETE(self):
        con_req, con_resp = data.get_contract(data.contract_list_valid, owner=self.user_01)

        # Create first
        response = self.user_01.post(utils.ApiUrls.contract, con_req)
        con_id = response.data.pop('id')

        # Legal delete
        response = self.user_01.delete(utils.ApiUrls.contract + str(con_id) + '/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.user_01.get(utils.ApiUrls.contract + str(con_id) + '/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_supervise_api(self):
        pass

    def test_assessment_method_api(self):
        pass
