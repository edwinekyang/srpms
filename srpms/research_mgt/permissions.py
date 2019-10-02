from rest_framework import viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request

from . import models
from . import views
from accounts.models import SrpmsUser


class AllowSafeMethods(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return False


class AllowPOST(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method == 'POST':
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        return False


class IsConvener(BasePermission):
    @staticmethod
    def check(user: SrpmsUser):
        return user.has_perm('research_mgt.can_convene')

    def has_permission(self, request: Request, view: viewsets.ModelViewSet) -> bool:
        return self.check(request.user)

    def has_object_permission(self, request: Request, view, obj) -> bool:
        return self.check(request.user)


class IsSuperuser(BasePermission):
    @staticmethod
    def check(user: SrpmsUser):
        return user.has_perm('research_mgt.is_mgt_superuser')

    def has_permission(self, request: Request, view: viewsets.ModelViewSet) -> bool:
        return self.check(request.user)

    def has_object_permission(self, request: Request, view, obj) -> bool:
        return self.check(request.user)


class IsContractOwner(BasePermission):
    @staticmethod
    def check(contract: models.Contract, user: SrpmsUser):
        return contract.owner == user

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.ContractViewSet):
            return True
        elif isinstance(view, views.SuperviseViewSet):
            return self.check(view.resolved_parents['contract'], request.user)
        elif isinstance(view, views.AssessmentViewSet):
            contract: models.Contract = view.resolved_parents['contract']
            if hasattr(contract, 'individual_project') and request.method in ['POST', 'DELETE']:
                return False
            else:
                return self.check(view.resolved_parents['contract'], request.user)

        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, models.Contract):
            return self.check(obj, request.user)
        elif isinstance(obj, models.Assessment):
            return self.check(obj.contract, request.user)
        elif isinstance(obj, models.Supervise):
            return self.check(obj.contract, request.user)

        return False


class IsContractFormalSupervisor(BasePermission):
    @staticmethod
    def check(contract: models.Contract, user: SrpmsUser) -> bool:
        if user in contract.get_all_formal_supervisors():
            return True
        return False

    def has_permission(self, request, view) -> bool:
        if type(view) in [views.ContractViewSet]:
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, models.Contract):
            if request.method == 'DELETE':
                return False
            elif self.check(obj, request.user):
                return True
        else:
            return False

        return False


class IsContractSupervisor(BasePermission):
    @staticmethod
    def check(contract: models.Contract, user: SrpmsUser) -> bool:
        if user in contract.get_all_supervisors():
            return True
        return False

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.SuperviseViewSet):
            return self.check(view.resolved_parents['contract'], request.user)
        elif isinstance(view, views.AssessmentExamineViewSet):
            return self.check(view.resolved_parents['contract'], request.user)
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, models.AssessmentExamine):
            return self.check(obj.contract, request.user)
        elif isinstance(obj, models.Supervise):
            return self.check(obj.contract, request.user)

        return False


class IsContractSuperviseOwner(BasePermission):
    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.SuperviseViewSet):
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, models.Supervise):
            return obj.supervisor == request.user
        return False


class IsContractAssessmentExaminer(BasePermission):
    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.AssessmentExamineViewSet):
            return request.user in view.resolved_parents['contract'].get_all_examiners()
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, models.AssessmentExamine):
            return obj.examine.examiner == request.user
        return False


class ContractNotFinalApproved(BasePermission):
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
        if isinstance(obj, models.Contract):
            return not obj.is_convener_approved()
        elif isinstance(obj, models.Supervise):
            return not obj.contract.is_convener_approved()
        elif isinstance(obj, models.Assessment):
            return not obj.contract.is_convener_approved()
        elif isinstance(obj, models.AssessmentExamine):
            return not obj.contract.is_convener_approved()
        return False


class ContractSubmitted(BasePermission):
    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.SuperviseViewSet):
            return view.resolved_parents['contract'].is_submitted()
        elif isinstance(view, views.AssessmentExamineViewSet):
            return view.resolved_parents['contract'].is_submitted()
        elif isinstance(view, views.AssessmentViewSet):
            return view.resolved_parents['contract'].is_submitted()
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, models.Supervise):
            return obj.contract.is_submitted()
        elif isinstance(obj, models.AssessmentExamine):
            return obj.contract.is_submitted()
        elif isinstance(obj, models.Assessment):
            return not obj.contract.is_submitted()
        return True


class ContractNotSubmitted(BasePermission):
    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.SuperviseViewSet):
            return not view.resolved_parents['contract'].is_submitted()
        elif isinstance(view, views.ContractViewSet):
            return True
        elif isinstance(view, views.AssessmentViewSet):
            return not view.resolved_parents['contract'].is_submitted()
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, models.Supervise):
            return not obj.contract.is_submitted()
        elif isinstance(obj, models.Contract):
            return not obj.is_submitted()
        elif isinstance(obj, models.Assessment):
            return not obj.contract.is_submitted()
        return False


class ContractApprovedBySupervisor(BasePermission):
    @staticmethod
    def check(contract: models.Contract):
        return contract.is_all_supervisors_approved()

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.AssessmentExamineViewSet):
            return self.check(view.resolved_parents['contract'])
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, models.AssessmentExamine):
            return self.check(obj.contract)
        return True


class ContractNotApprovedBySupervisor(BasePermission):
    @staticmethod
    def check(contract: models.Contract):
        return not contract.is_all_supervisors_approved()

    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.AssessmentExamineViewSet):
            return self.check(view.resolved_parents['contract'])
        elif isinstance(view, views.SuperviseViewSet):
            return self.check(view.resolved_parents['contract'])
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, models.AssessmentExamine):
            return self.check(obj.contract)
        if isinstance(obj, models.Supervise):
            return self.check(obj.contract)
        return True
