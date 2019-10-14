"""
Defines permissions for views for the backend. Permission might or might not be request
issuer related, and is being checked before view enter any business logic.

Note that while has_permission() is not object related, HTTP method being banned there
would not pass the has_object_permission() check.

Also, while all permission class support logical operators (i.e. OR, AND, and NOT), it is
not recommend to use NOT operator on permissions that are model relevant, since the negation
might not be completely complementary.
"""

__author__ = "Dajie (Cooper) Yang"
__credits__ = ["Dajie Yang"]

__maintainer__ = "Dajie (Cooper) Yang"
__email__ = "dajie.yang@anu.edu.au"

from rest_framework import viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request

from . import views
from .models import (Contract, Supervise, Assessment, AssessmentExamine)
from accounts.models import SrpmsUser


class AllowSafeMethods(BasePermission):
    """Allow HTTP methods that are considered safe, i.e. GET, HEAD, OPTIONS"""

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return False


class AllowPOST(BasePermission):
    """
    Allow POST method, this is being used in the cased that most user have the permission
    to create resource, but don't necessarily have permission to edit.
    """

    def has_permission(self, request, view) -> bool:
        if request.method == 'POST':
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        return False


class IsConvener(BasePermission):
    """Check if the requester is course convener, model irrelevant"""

    @staticmethod
    def check(user: SrpmsUser):
        return user.has_perm('research_mgt.can_convene')

    def has_permission(self, request: Request, view: viewsets.ModelViewSet) -> bool:
        return self.check(request.user)

    def has_object_permission(self, request: Request, view, obj) -> bool:
        return self.check(request.user)


class IsSuperuser(BasePermission):
    """Check if the requester is superuser, model irrelevant"""

    @staticmethod
    def check(user: SrpmsUser):
        return user.has_perm('research_mgt.is_mgt_superuser')

    def has_permission(self, request: Request, view: viewsets.ModelViewSet) -> bool:
        return self.check(request.user)

    def has_object_permission(self, request: Request, view, obj) -> bool:
        return self.check(request.user)


class IsContractOwner(BasePermission):
    """Check if the requester is the owner of the requested contract"""

    @staticmethod
    def check(contract: Contract, user: SrpmsUser):
        return contract.owner == user

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.ContractViewSet):
            return True
        elif isinstance(view, views.SuperviseViewSet):
            return self.check(view.resolved_parents['contract'], request.user)
        elif isinstance(view, views.AssessmentViewSet):
            contract: Contract = view.resolved_parents['contract']
            if hasattr(contract, 'individual_project') and request.method in ['POST', 'DELETE']:
                return False
            else:
                return self.check(view.resolved_parents['contract'], request.user)

        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, Contract):
            return self.check(obj, request.user)
        elif isinstance(obj, Assessment):
            return self.check(obj.contract, request.user)
        elif isinstance(obj, Supervise):
            return self.check(obj.contract, request.user)

        return False


class IsContractFormalSupervisor(BasePermission):
    """Check if the requester is one of the contract formal supervisor"""

    @staticmethod
    def check(contract: Contract, user: SrpmsUser) -> bool:
        return user in contract.get_all_formal_supervisors()

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.SuperviseViewSet):
            return self.check(view.resolved_parents['contract'], request.user)
        elif isinstance(view, views.AssessmentExamineViewSet):
            return self.check(view.resolved_parents['contract'], request.user)
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, Supervise):
            return self.check(obj.contract, request.user)
        elif isinstance(obj, AssessmentExamine):
            return self.check(obj.contract, request.user)
        return False


class IsContractSuperviseOwner(BasePermission):
    """
    Check if the requester is the supervisor specified in the requested supervise relationship.
    """

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.SuperviseViewSet):
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, Supervise):
            return obj.supervisor == request.user
        return False


class IsContractAssessmentExaminer(BasePermission):
    """
    Check if the requester is the examiner of requested assessment, note that one assessment might
    have multiple examiner.
    """

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.AssessmentExamineViewSet):
            return request.user in view.resolved_parents['contract'].get_all_examiners()
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, AssessmentExamine):
            return obj.examine.examiner == request.user
        return False


class ContractNotFinalApproved(BasePermission):
    """Check if the requested contract is approved by supervisor"""

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.ContractViewSet):
            return True
        elif isinstance(view, views.SuperviseViewSet):
            return not view.resolved_parents['contract'].is_convener_approved()
        elif isinstance(view, views.AssessmentViewSet):
            return not view.resolved_parents['contract'].is_convener_approved()
        elif isinstance(view, views.AssessmentExamineViewSet):
            return not view.resolved_parents['contract'].is_convener_approved()
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, Contract):
            return not obj.is_convener_approved()
        elif isinstance(obj, Supervise):
            return not obj.contract.is_convener_approved()
        elif isinstance(obj, Assessment):
            return not obj.contract.is_convener_approved()
        elif isinstance(obj, AssessmentExamine):
            return not obj.contract.is_convener_approved()
        return False


class ContractSubmitted(BasePermission):
    """Check if the requested contract has been submitted"""

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.SuperviseViewSet):
            return view.resolved_parents['contract'].is_submitted()
        elif isinstance(view, views.AssessmentExamineViewSet):
            return view.resolved_parents['contract'].is_submitted()
        elif isinstance(view, views.AssessmentViewSet):
            return view.resolved_parents['contract'].is_submitted()
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, Supervise):
            return obj.contract.is_submitted()
        elif isinstance(obj, AssessmentExamine):
            return obj.contract.is_submitted()
        elif isinstance(obj, Assessment):
            return not obj.contract.is_submitted()
        return False


class ContractNotSubmitted(BasePermission):
    """Check if the requested contract hasn't been submitted"""

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.SuperviseViewSet):
            return not view.resolved_parents['contract'].is_submitted()
        elif isinstance(view, views.ContractViewSet):
            return True
        elif isinstance(view, views.AssessmentViewSet):
            return not view.resolved_parents['contract'].is_submitted()
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, Supervise):
            return not obj.contract.is_submitted()
        elif isinstance(obj, Contract):
            return not obj.is_submitted()
        elif isinstance(obj, Assessment):
            return not obj.contract.is_submitted()
        return False


class ContractApprovedBySupervisor(BasePermission):
    """Check if the requested contract has been approved by all of its supervisors"""

    @staticmethod
    def check(contract: Contract) -> bool:
        return contract.is_all_supervisors_approved()

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.AssessmentExamineViewSet):
            return self.check(view.resolved_parents['contract'])
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, AssessmentExamine):
            return self.check(obj.contract)
        return False


class IsThisSupervisorNotApprove(BasePermission):
    """Check if the supervise relation has been approve by the requester"""

    @staticmethod
    def check(supervise: Supervise, user: SrpmsUser) -> bool:
        return supervise.supervisor == user and not supervise.supervisor_approval_date

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.AssessmentExamineViewSet):
            contract: Contract = view.resolved_parents['contract']
            try:
                supervise = contract.supervise.get(supervisor=request.user)
                return self.check(supervise, request.user)
            except Supervise.DoesNotExist:
                return False
        elif isinstance(view, views.SuperviseViewSet):
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, AssessmentExamine):
            contract: Contract = view.resolved_parents['contract']
            try:
                supervise = contract.supervise.get(supervisor=request.user)
                return self.check(supervise, request.user)
            except Supervise.DoesNotExist:
                return False
        if isinstance(obj, Supervise):
            return self.check(obj, request.user)
        return False


class IsExaminerNominator(BasePermission):
    """Check if the requester is the nominator of this examiner"""

    @staticmethod
    def check(assessment_examine: AssessmentExamine, user):
        return assessment_examine.examine.nominator == user

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.AssessmentExamineViewSet):
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, AssessmentExamine):
            return self.check(obj, request.user)
        return False


class ContractFinalApproved(BasePermission):
    """Check if the requested contract has been approved by convener"""

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.ContractViewSet):
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, Contract):
            return bool(obj.convener_approval_date)
        return False


class IsSuperviseNominator(BasePermission):
    """Check if the requester is the nominator of this supervise relationship"""

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.SuperviseViewSet):
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, Supervise):
            return obj.nominator == request.user
        return False
