from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.request import Request

from . import models
from . import views
from accounts.models import SrpmsUser


class AllowSafeMethods(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return False


class AllowPOST(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method == 'POST':
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        return False


class IsConvener(permissions.BasePermission):
    @staticmethod
    def check(user: SrpmsUser):
        return user.has_perm('research_mgt.can_convene')

    def has_permission(self, request: Request, view: viewsets.ModelViewSet) -> bool:
        return self.check(request.user)

    def has_object_permission(self, request: Request, view, obj) -> bool:
        return self.check(request.user)


class IsSuperuser(permissions.BasePermission):
    @staticmethod
    def check(user: SrpmsUser):
        return user.has_perm('research_mgt.is_mgt_superuser')

    def has_permission(self, request: Request, view: viewsets.ModelViewSet) -> bool:
        return self.check(request.user)

    def has_object_permission(self, request: Request, view, obj) -> bool:
        return self.check(request.user)


class IsContractOwner(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if isinstance(view, views.ContractViewSet):
            return True
        elif isinstance(view, views.AssessmentViewSet):
            if request.method in ['POST', 'DELETE'] and \
                    hasattr(view.resolved_parents['contract'], 'individual_project'):
                return False
            else:
                return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, models.Contract):
            if obj.owner == request.user:
                return True
        elif isinstance(obj, models.Assessment):
            if obj.contract.owner == request.user:
                return True
        else:
            return False

        return False


class IsContractFormalSupervisor(permissions.BasePermission):
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


class IsContractSupervisor(permissions.BasePermission):
    @staticmethod
    def check(contract: models.Contract, user: SrpmsUser) -> bool:
        if user in contract.get_all_supervisors():
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


class IsContractSuperviseOwner(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        return False


class IsContractAssessmentExaminer(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        return False
