from django.core.exceptions import ValidationError

from research_mgt.models import (Contract, IndividualProject, SpecialTopic, Assessment, \
                                 Examine, AssessmentExamine)
from . import utils
from . import data


class TestModel(utils.SrpmsTest):
    def test_contract_str(self):
        individual_project_data = {**data.contract_01_request, 'course': data.comp8755}
        individual_project_data = {**individual_project_data.pop('individual_project'),
                                   **individual_project_data}
        c = IndividualProject.objects.create(owner=self.user_01.obj, **individual_project_data)
        self.assertEqual(str(c), c.title)

        special_topic_data = {**data.contract_02_request, 'course': data.comp6470}
        special_topic_data = {**special_topic_data.pop('special_topic'),
                              **special_topic_data}
        c = SpecialTopic.objects.create(owner=self.user_01.obj, **special_topic_data)
        self.assertEqual(str(c), c.title)

    def test_assessment_examine(self):
        contract_01 = Contract.objects.create(year=2019, semester=2, duration=1,
                                              course=data.comp8755,
                                              convener=self.convener.obj,
                                              owner=self.user_01.obj)

        contract_02 = Contract.objects.create(year=2019, semester=2, duration=1,
                                              course=data.comp8755,
                                              convener=self.convener.obj,
                                              owner=self.user_01.obj)

        assessment_01 = Assessment.objects.create(template=data.temp_report,
                                                  contract=contract_01,
                                                  weight=50)

        assessment_02 = Assessment.objects.create(template=data.temp_report,
                                                  contract=contract_02,
                                                  weight=50)

        examine_01 = Examine.objects.create(contract=contract_01,
                                            examiner=self.user_02.obj)

        examine_02 = Examine.objects.create(contract=contract_02,
                                            examiner=self.user_02.obj)

        # AssessmentExamine should be locked to the same contract
        with self.assertRaises(ValidationError):
            AssessmentExamine.objects.create(assessment=assessment_02, examine=examine_01)
        with self.assertRaises(ValidationError):
            AssessmentExamine.objects.create(assessment=assessment_01, examine=examine_02)

        # Valid relation
        AssessmentExamine.objects.create(assessment=assessment_01, examine=examine_01)
        AssessmentExamine.objects.create(assessment=assessment_02, examine=examine_02)

        # Violate unique constraint
        with self.assertRaises(ValidationError):
            AssessmentExamine.objects.create(assessment=assessment_01, examine=examine_01)
            AssessmentExamine.objects.create(assessment=assessment_02, examine=examine_02)
