"""
Print contract to PDF.
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from io import BytesIO
from datetime import datetime
from typing import List, Union, Set, Tuple
from collections import OrderedDict

from django.template.loader import render_to_string
from django.db.models.query import Q, QuerySet
from django.contrib.auth.models import Permission
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

from research_mgt.models import (Course, Contract, IndividualProject, Supervise, Assessment,
                                 AssessmentExamine)
from accounts.models import SrpmsUser


def get_examiners_name(assessment_examine: Union[QuerySet, List[AssessmentExamine]]) -> Set[str]:
    """
    Retrieve examiner information for printing, so that we don't need to do query
    inside HTML template. This function would not check if all the AssessmentExamine
    items belong to the same assessment, check it if necessary before pass to this
    function.

    Args:
        assessment_examine: queryset of AssessmentExamine that you would want to extract
                            examiner.
    Returns:
        A set of examiner's display name and their approval date
    """
    names = set()
    for ae in assessment_examine:
        names.add(ae.examine.examiner.get_display_name())
    return names


def get_supervise_name(supervise: Union[QuerySet, List[Supervise]]) -> Set[str]:
    """
    Retrieve supervisor information for printing.

    Args:
        supervise: queryset of Supervise
    """
    names = set()
    for s in supervise:
        names.add(s.supervisor.get_display_name())
    return names


def print_individual_project_contract(contract: Contract, file_object: BytesIO, base_url: str) \
        -> None:
    """
    Print contract and all its content (supervise, assessment, examine, etc.). The function
    assume that the input contract has already been approved by convener, and complies with
    all model constraints.

    Args:
        contract: The contract you're going to print, make sure its individual project
        file_object: An buffer this function would output pdf to
        base_url: return of request.build_absolute_uri()
    """
    contract: IndividualProject = contract.individual_project
    supervises: Union[QuerySet, List[Supervise]] = contract.supervise.all()
    assessments: Union[QuerySet, List[Assessment]] = contract.assessment.all()
    assess_examines: Union[QuerySet, List[AssessmentExamine]] = contract.assessment_examine.all()

    perm = Permission.objects.get(codename='can_supervise')

    owner: SrpmsUser = contract.owner

    course: Course = contract.course
    course_info: str = '{code} - {name} ({unit} units)'.format(code=course.course_number,
                                                               name=course.name,
                                                               unit=course.units)

    # Supervisor information
    formal_supervisors = supervises.filter(Q(supervisor__groups__permissions=perm) |
                                           Q(supervisor__user_permissions=perm) |
                                           Q(supervisor__is_superuser=True))
    other_supervisors = supervises.filter(~Q(supervisor__groups__permissions=perm) &
                                          ~Q(supervisor__user_permissions=perm) &
                                          Q(supervisor__is_superuser=False))

    # Supervisor approval information
    supervise_approval: List[Tuple[SrpmsUser, datetime]] = list()
    for supervise in (formal_supervisors | other_supervisors).distinct():
        supervise_approval.append((supervise.supervisor.get_display_name(),
                                   supervise.supervisor_approval_date))

    # If no other supervisor, project supervisor is the same as formal supervisor.
    # Note that formal supervisor is limited to one for individual project.
    if not other_supervisors:
        other_supervisors = formal_supervisors

    # Assessment information
    repr_assessments: List[OrderedDict] = list()
    for i in range(len(assessments)):
        # Get a readable representation
        if assessments[i].additional_description:
            assessment_name = ': '.join([assessments[i].template.name,
                                         assessments[i].additional_description])
        else:
            assessment_name = assessments[i].template.name

        # Initialize assessment information
        repr_assessment = OrderedDict([
            ('component', assessment_name),
            ('weight', assessments[i].weight),
            ('due date', '' if not assessments[i].due else assessments[i].due),
            ('examiners', ', '.join(get_examiners_name(
                    assess_examines.filter(assessment=assessments[i]))))
        ])
        repr_assessments.append(repr_assessment)

    # Assessment approval information
    assess_examine_approve: OrderedDict[str, List[Tuple[str, datetime]]] = OrderedDict()
    for assessment in assessments:
        # Get a readable representation
        if assessment.additional_description:
            assessment_name = ': '.join([assessment.template.name,
                                         assessment.additional_description])
        else:
            assessment_name = assessment.template.name

        # Initialize list of examiners
        assess_examine_approve[assessment_name]: List[Tuple[str, datetime]] = list()

        # Get all the examiner name and their approval date for this assessment
        for assess_examine in assessment.assessment_examine.all():
            assess_examine: AssessmentExamine = assess_examine
            assess_examine_approve[assessment_name].append(
                    (assess_examine.examine.examiner.get_display_name(),
                     assess_examine.examiner_approval_date))

    html_string: str = render_to_string(template_name='research_mgt/individual_project.html',
                                        context={'contract': contract,
                                                 'owner': owner,
                                                 'course_info': course_info,
                                                 'supervise_formal': get_supervise_name(
                                                         formal_supervisors),
                                                 'supervise_other': get_supervise_name(
                                                         other_supervisors),
                                                 'supervise_approval': supervise_approval,
                                                 'assessments': repr_assessments,
                                                 'assess_examine_approve': assess_examine_approve})
    html = HTML(string=html_string, base_url=base_url)
    font_config = FontConfiguration()
    html.write_pdf(target=file_object, font_config=font_config)
