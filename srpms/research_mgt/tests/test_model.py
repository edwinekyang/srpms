from django.core.exceptions import ValidationError

from research_mgt.models import Contract, AssessmentMethod, Examine, AssessmentExamine
from . import utils
from . import data


class TestModel(utils.SrpmsTest):
    def test_assessment_examine(self):
        contract_01 = Contract.objects.create(year=2019, semester=2, duration=1,
                                              course=data.comp8755,
                                              convener=self.convener.obj,
                                              owner=self.user_01.obj)

        contract_02 = Contract.objects.create(year=2019, semester=2, duration=1,
                                              course=data.comp8755,
                                              convener=self.convener.obj,
                                              owner=self.user_01.obj)

        assessment_01 = AssessmentMethod.objects.create(template=data.temp_report,
                                                        contract=contract_01,
                                                        weight=50)

        assessment_02 = AssessmentMethod.objects.create(template=data.temp_report,
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
