import random
from typing import List, Dict, Tuple

from accounts.models import SrpmsUser
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

# For course, response and requests are basically the same, 'id' and 'contract' field are read-only
course_list_valid = [
    {'course_number': 'test',
     'name': 'dafklj92498234iusdfqiwoer', },
    {'course_number': 'test0123',
     'name': 'dafklj92498234iusdfqiwoer', }
]


def get_course() -> Dict:
    c_req = random.choice(course_list_valid)
    return {**c_req}


def get_courses() -> List[Dict]:
    results = []
    for c_req in course_list_valid:
        results.append({**c_req})
    return results


course_list_invalid = [
    {'course_number': 'COMP2710',  # course number not unique
     'name': 'dafklj92498234iusdfqiwoer', },
    {'course_number': '',  # course number empty
     'name': 'dafklj92498234iusdfqiwoer', },
    {'course_number': 'sdifuoqer2',
     'name': '', },  # course name empty
]

############################################################################################
# Assessment Templates

temp_report = models.AssessmentTemplate.objects.get(name='report')
temp_artifact = models.AssessmentTemplate.objects.get(name='artifact')
temp_presentation = models.AssessmentTemplate.objects.get(name='presentation')
temp_custom = models.AssessmentTemplate.objects.get(name='custom')

temp_list_valid = [
    {'name': 'test01',
     'description': '',
     'max_weight': 100,
     'min_weight': 0,
     'default_weight': 50},
    {'name': 'test02',
     'description': '',
     'max_weight': 50,
     'min_weight': 50,
     'default_weight': 50},
    {'name': 'test03',
     'description': '',
     'max_weight': 60,
     'min_weight': 50,
     'default_weight': 60},
    {'name': 'test04',
     'description': '',
     'max_weight': 50,
     'min_weight': 30,
     'default_weight': 30}
]


def get_temp() -> Dict:
    c_req = random.choice(temp_list_valid)
    return {**c_req}


def get_temps() -> List[Dict]:
    results = []
    for c_req in temp_list_valid:
        results.append({**c_req})
    return results


temp_list_invalid = [
    {'name': '',  # Empty name
     'description': 'asd',
     'max_weight': 100,
     'min_weight': 0,
     'default_weight': 50},
    {'name': 'test02',
     'description': '',
     'max_weight': 101,  # > 100
     'min_weight': -1,  # < 0
     'default_weight': 50},
    {'name': 'test03',
     'description': '',
     'max_weight': 60,
     'min_weight': 50,
     'default_weight': 70},  # Out of range
    {'name': 'test04',
     'description': '',
     'max_weight': 50,
     'min_weight': 30,
     'default_weight': 10}  # Out of range
]

############################################################################################
# Contracts

contract_01_request = {
    'year': 2019,
    'semester': 1,
    'duration': 1,
    'resources': '',
    'course': comp8755.id,
    'individual_project': {
        'title': 'Test',
        'objectives': '',
        'description': ''
    }
}

contract_01_response = {
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
    'special_topic': None
}

contract_02_request = {
    'year': 2019,
    'semester': 1,
    'duration': 1,
    'resources': '',
    'course': comp8755.id,
    'special_topic': {
        'title': 'Test',
        'objectives': '',
        'description': ''
    }
}

contract_02_response = {
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
    'individual_project': None,
    'special_topic': {
        'title': 'Test',
        'objectives': '',
        'description': ''
    }
}

contract_list_valid = [
    (contract_01_request, contract_01_response),
    (contract_02_request, contract_02_response),
]


def get_contract(owner: SrpmsUser) -> Tuple[Dict, Dict]:
    c_req, c_resp = random.choice(contract_list_valid)
    return {**c_req}, {**c_resp, 'owner': owner.id}


def get_contracts(owner: SrpmsUser) -> List[Tuple[Dict, Dict]]:
    results = []
    for c_req, c_resp in contract_list_valid:
        results.append((
            {**c_req},
            {**c_resp, 'owner': owner.id, }
        ))
    return results


contract_list_invalid = [
    {'year': -1,  # Illegal value
     'semester': -1,  # Illegal value
     'duration': 10000000,  # Illegal value
     'resources': '',
     'course': comp8755.id,
     'is_convener_approved': False,
     'is_submitted': False,
     'individual_project': {
         'title': 'Test',
         'objectives': '',
         'description': ''
     },
     'special_topic': None},
    {'year': 2019,
     'semester': 1,
     'duration': 1,
     'resources': '',
     'course': comp8755.id,
     'is_convener_approved': False,
     'is_submitted': True,  # Cannot be submitted
     'individual_project': {
         'title': 'Test',
         'objectives': '',
         'description': ''
     },
     'special_topic': None},
    {'year': 2019,
     'semester': 1,
     'duration': 1,
     'resources': '',
     'course': comp8755.id,
     'is_convener_approved': False,
     'is_submitted': False,
     'individual_project': None,  # Contract type should at least one
     'special_topic': None},
    {'year': 2019,
     'semester': 1,
     'duration': 1,
     'resources': '',
     'course': comp8755.id,
     'is_convener_approved': False,
     'is_submitted': False,
     'individual_project': {  # Contract cannot have more than one type
         'title': 'Test',
         'objectives': '',
         'description': ''
     },
     'special_topic': {
         'title': 'Test',
         'objectives': '',
         'description': ''
     }}
]


############################################################################################
# Supervise

def gen_supervise_req_resp(contract_id: int, supervisor_id: int, is_formal: bool) \
        -> Tuple[dict, dict]:
    request = {'supervisor': supervisor_id}
    response = {'contract': contract_id, 'supervisor': supervisor_id, 'is_formal': is_formal}
    return request, response


############################################################################################
# Assessments

assessment_01_request = {
    'template': temp_report.id,
}

assessment_01_response = {
    "template": temp_report.id,
    "contract": None,  # Supply data here
    "additional_description": "",
    "due": None,
    "weight": temp_report.default_weight,
    "is_all_examiners_approved": False
}

assessment_02_request = {
    'template': temp_artifact.id,
    "additional_description": "aisduioeodyhery82",
    'weight': 40,
}

assessment_02_response = {
    "template": temp_artifact.id,
    "contract": None,  # Supply data here
    "additional_description": "aisduioeodyhery82",
    "due": None,
    "weight": 40,
    "is_all_examiners_approved": False
}

assessment_custom_request = {
    'template': temp_custom.id,
    "additional_description": "",
    'weight': 40,
}

assessment_custom_response = {
    "template": temp_custom.id,
    "contract": None,  # Supply data here
    "additional_description": "",
    "due": None,
    "weight": 40,
    "is_all_examiners_approved": False
}

assessment_list_valid = [
    (assessment_01_request, assessment_01_response),
    (assessment_02_request, assessment_02_response),
]


def get_assessment(contract_id: int) \
        -> Tuple[dict, dict]:
    request, response = random.choice(assessment_list_valid)
    return {**request}, {**response, 'contract': contract_id}


def get_assessments(contract_id: int) \
        -> List[Tuple[dict, dict]]:
    results = []
    for request, response in contract_list_valid:
        results.append((
            {**request},
            {**response, 'contract': contract_id}
        ))
    return results


############################################################################################
# Assessment Examine

def gen_examine_req_resp(examiner_id: int) \
        -> Tuple[dict, dict]:
    request = {'examiner': examiner_id}
    response = {'examiner': examiner_id}
    return request, response
