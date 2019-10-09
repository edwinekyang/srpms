"""
Print contract to PDF.
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from io import BytesIO

from django.template.loader import render_to_string
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration

from research_mgt.models import (Contract, IndividualProject, Supervise, Assessment,
                                 Examine, AssessmentExamine)


def print_individual_project_contract(contract: Contract, file_object: BytesIO) -> None:
    """
    Print contract and all its content (supervise, assessment, examine, etc.). The function
    assume that the input contract has already been approved by convener, and complies with
    all model constraints.

    :param contract: The contract you're going to print, make sure its individual project
    :param file_object: An buffer this function would output pdf to
    """
    owner = contract.owner
    contract: IndividualProject = contract.individual_project
    supervise: Supervise = contract.supervise.all()
    assessment: Assessment = contract.assessment.all()
    assessment_examine: AssessmentExamine = contract.assessment_examine.all()

    html = render_to_string(template_name='research_mgt/individual_project.html',
                            context={'contract': contract,
                                     'supervise': supervise,
                                     'assessment': assessment,
                                     'assessment_examine': assessment_examine})
    HTML(string=html).write_pdf(target=file_object, font_config=FontConfiguration())
