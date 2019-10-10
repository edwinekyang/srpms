"""
Integration test for special topic type of contract.
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'
from rest_framework import status

from . import utils
from . import data


class SpecialTopic(utils.SrpmsTest):
    def setUp(self):
        super(SpecialTopic, self).setUp()

        contract_request = {
            'year': 2019,
            'semester': 1,
            'duration': 1,
            'resources': 'asdf9o8239jasdf',
            'course': data.comp6470.id,
            'special_topic': {
                'title': 'Test',
                'objectives': 'd09130jodsaf',
                'description': 'd89aqefd9hf'
            }
        }

        # Create a special topic contract
        response = self.user_01.post(utils.ApiUrls.contract, contract_request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.contract_id: int = response.data['id']

    def set_supervise(self) -> None:
        """
        Assign supervisors for the contract.
        """

        # Contract owner set formal supervisor
        req, _ = data.gen_supervise_req_resp(self.contract_id,
                                             self.supervisor_formal.id, True)
        response = self.user_01.post(utils.get_supervise_url(self.contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.supervise_formal_id: int = response.data['id']

        # Formal supervisor set non-formal supervisor
        req, _ = data.gen_supervise_req_resp(self.contract_id,
                                             self.supervisor_non_formal.id, False)
        response = self.supervisor_formal.post(utils.get_supervise_url(self.contract_id), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.supervise_non_formal_id: int = response.data['id']

        # URLs for later use
        self.supervise_formal_approve_url: str = utils.get_supervise_url(
                self.contract_id, self.supervise_formal_id, approve=True)
        self.supervise_non_formal_approve_url: str = utils.get_supervise_url(
                self.contract_id, self.supervise_non_formal_id, approve=True)

    def set_assessment(self) -> None:
        """Set two assessments for the contract created in setUp()"""
        response = self.user_01.post(utils.get_assessment_url(self.contract_id),
                                     {'template': data.temp_custom.id, 'weight': 70})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assess_01_id: int = response.data['id']

        response = self.user_01.post(utils.get_assessment_url(self.contract_id),
                                     {'template': data.temp_custom.id, 'weight': 30})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assess_02_id: int = response.data['id']

    def set_submit(self) -> None:
        """Set submit status for the contract"""
        response = self.user_01.put(utils.get_contract_url(self.contract_id, submit=True),
                                    data.get_submit_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    def set_examine(self) -> None:
        """Assign examiner to every assessment of the contract"""

        req, _ = data.gen_examine_req_resp(self.user_03.id)
        response = self.supervisor_formal.post(
                utils.get_examine_url(self.contract_id, self.assess_01_id), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.examine_01_id: int = response.data['id']

        req, _ = data.gen_examine_req_resp(self.user_04.id)
        response = self.supervisor_non_formal.post(
                utils.get_examine_url(self.contract_id, self.assess_02_id), req)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.examine_02_id: int = response.data['id']

    def set_supervise_approve(self) -> None:
        """Set supervisor approval for the contract"""
        response = self.supervisor_formal.put(self.supervise_formal_approve_url,
                                              data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.supervisor_non_formal.put(self.supervise_non_formal_approve_url,
                                                  data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def set_examiner_approve(self):
        """Set examiner approval for all assessments for the contract"""
        response = self.user_03.put(utils.get_examine_url(self.contract_id, self.assess_01_id,
                                                          self.examine_01_id, approve=True),
                                    data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        response = self.user_04.put(utils.get_examine_url(self.contract_id, self.assess_02_id,
                                                          self.examine_02_id, approve=True),
                                    data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    def set_convener_approve(self):
        """Set final approval for the contract"""
        response = self.convener.put(utils.get_contract_url(self.contract_id, approve=True),
                                     data.get_approve_data(True))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

    def test_work_flow_valid(self):
        self.set_supervise()
        self.set_assessment()
        self.set_submit()
        self.set_examine()
        self.set_supervise_approve()
        self.set_examiner_approve()
        self.set_convener_approve()
