"""
Test serializer utilities, mainly for testing the customize serializer field is behaving correctly.
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from rest_framework.serializers import ModelSerializer

from research_mgt.serializer_utils import DateTimeBooleanField
from research_mgt.models import Contract
from . import data
from . import utils


# noinspection PyAbstractClass
class FakeSerializer(ModelSerializer):
    is_created = DateTimeBooleanField(source='create_date')

    class Meta:
        model = Contract
        fields = ['is_created']


class DateTimeBooleanFieldTest(utils.SrpmsTest):
    def setUp(self):
        super(DateTimeBooleanFieldTest, self).setUp()

        self.contract = Contract.objects.create(year=2019, semester=1, duration=2,
                                                course=data.comp8755, owner=self.user_01.obj)

    def test_initial(self):
        serializer = FakeSerializer(self.contract)
        self.assertTrue(serializer.data['is_created'] is True)

    def test_to_internal_value(self):
        serializer = FakeSerializer(self.contract, data={'is_created': True})
        serializer.is_valid()
        serializer.save()
