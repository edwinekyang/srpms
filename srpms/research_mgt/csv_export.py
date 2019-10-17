"""
Export related functions, for example, export list of contracts to csv
"""

__author__ = "Dajie (Cooper) Yang"
__credits__ = ["Dajie Yang"]

__maintainer__ = "Dajie (Cooper) Yang"
__email__ = "dajie.yang@anu.edu.au"

from io import StringIO
from typing import List, Union
from django.db.models import QuerySet

from .models import Contract, Supervise, AssessmentExamine
from accounts.models import SrpmsUser


def get_name_email(user: SrpmsUser) -> str:
    """
    Output user's information in the form of 'FirstName LastName <email>'

    Args:
        user: the user that you what to print
    """
    return '{} {} <{}>'.format(user.first_name, user.last_name, user.email)


def contract_csv_export(contract_list: Union[QuerySet, List[Contract]],
                        file_object: StringIO) -> None:
    """
    Generate csv file according to given queryset of Contract. Only contracts that has
    been approved by course convener would be included.

    TODO: Support special topic contract

    CSV Template:
    COMP8755; 18S2; u9999999; stuSurname, stuFirstname; project title; 45; 45;
    supr1Firstname supr1Surname <supr1Email>, supr2Firstname supr2Surname <supr2Email>;
    repExFirstname repExSurname <repExEmail>; artExFirstname artExSurname <artExEmail>;

    Args:
        contract_list: a queryset of contract
        file_object: a file_object to store the output
    """
    for contract in contract_list:
        # Only support individual project at the moment
        if hasattr(contract, 'individual_project') and contract.convener_approval_date:
            course: str = contract.course.course_number

            # Generate conducting time information
            current_year = contract.year
            current_semester = contract.semester
            semesters: List[str] = []
            for _ in range(contract.duration):
                semesters.append('{}S{}'.format(str(current_year)[-2:],
                                                current_semester))
                if current_semester >= 2:  # carry
                    current_semester = 1
                    current_year += 1
                else:
                    current_semester += 1
            time_info = ', '.join(semesters)

            # Owner information
            student_id: str = contract.owner.uni_id

            student_name: str = ', '.join([contract.owner.last_name,
                                      contract.owner.first_name])

            title: str = str(contract)

            # Supervisor information
            supervisors: List[str] = []
            for s in contract.supervise.all():
                s: Supervise = s
                supervisors.append(get_name_email(s.supervisor))
            supervisor_info: str = ', '.join(supervisors)

            # Report weight and examiner
            report = contract.assessment.get(template__name='report')
            report_weight: str = str(report.weight)
            report_assess: Union[
                QuerySet, List[AssessmentExamine]] = report.assessment_examine.all()
            if report_assess:
                report_examiner = get_name_email(report_assess[0].examine.examiner)
            else:
                report_examiner = None

            # Artifact weight and examiner
            artifact = contract.assessment.get(template__name='artifact')
            artifact_weight: str = str(artifact.weight)
            artifact_assess: Union[
                QuerySet, List[AssessmentExamine]] = artifact.assessment_examine.all()
            if artifact_assess:
                artifact_examiner = get_name_email(artifact_assess[0].examine.examiner)
            else:
                artifact_examiner = None

            # Write to csv, the last '' is for the purpose of adding ; for the last item
            contract_export = '; '.join([course, time_info, student_id, student_name, title,
                                         report_weight, artifact_weight,
                                         supervisor_info,
                                         report_examiner, artifact_examiner, ''])
            contract_export += '\n\n'
            file_object.write(contract_export)
