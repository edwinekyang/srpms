import random
from typing import List, Dict, Tuple

from accounts.models import SrpmsUser
from . import utils
from research_mgt import models

############################################################################################
# Courses

comp2710 = models.Course.objects.get(course_number='COMP2710')
comp3710 = models.Course.objects.get(course_number='COMP3710')
comp3740 = models.Course.objects.get(course_number='COMP3740')
comp3770 = models.Course.objects.get(course_number='COMP3770')
comp4560 = models.Course.objects.get(course_number='COMP4560')
comp6470 = models.Course.objects.get(course_number='COMP6470')
comp8755 = models.Course.objects.get(course_number='COMP8755')

############################################################################################
# Assessment Templates

temp_report = models.AssessmentTemplate.objects.get(name='report')
temp_artifact = models.AssessmentTemplate.objects.get(name='artifact')
temp_presentation = models.AssessmentTemplate.objects.get(name='presentation')
temp_custom = models.AssessmentTemplate.objects.get(name='custom')

############################################################################################
# Contracts

contract_01_valid_request = {
    'year': 2019,
    'semester': 1,
    'duration': 1,
    'resources': '',
    'course': comp8755.id,
    'is_convener_approved': False,
    'is_submitted': False,
    'individual_project': {
        'title': 'Test',
        'objectives': '',
        'description': ''
    },
    'special_topics': None
}

contract_01_valid_response = {
    'year': 2019,
    'semester': 1,
    'duration': 1,
    'resources': '',
    'course': comp8755.id,
    'convener': None,
    'is_convener_approved': False,
    'convener_approval_date': None,
    'owner': None,  # Supply data here
    'submit_date': None,
    'is_submitted': False,
    'individual_project': {
        'title': 'Test',
        'objectives': '',
        'description': ''
    },
    'special_topics': None
}

contract_list_valid = [
    (contract_01_valid_request, contract_01_valid_response),
]


def get_contract(contract_list: list, owner: SrpmsUser) \
        -> Tuple[Dict, Dict]:
    c_req, c_resp = random.choice(contract_list)
    return {**c_req}, {**c_resp, 'owner': owner.id}


def get_contracts(contract_list: list, owner: SrpmsUser) \
        -> List[Tuple[Dict, Dict]]:
    results = []
    for c_req, c_resp in contract_list:
        results.append((
            {**c_req},
            {**c_resp, 'owner': owner.id, }
        ))
    return results

############################################################################################
# Supervise

############################################################################################
# Assessment Methods
