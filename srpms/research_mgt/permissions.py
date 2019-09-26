from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.request import Request

from . import models
from . import views


class ReadOnly(permissions.BasePermission):
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
    def has_permission(self, request: Request, view: viewsets.ModelViewSet) -> bool:
        return request.user.has_perm('research_mgt.can_convene')

    def has_object_permission(self, request: Request, view, obj) -> bool:
        return request.user.has_perm('research_mgt.can_convene')


class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request: Request, view: viewsets.ModelViewSet) -> bool:
        return request.user.has_perm('research_mgt.is_mgt_superuser')

    def has_object_permission(self, request: Request, view, obj) -> bool:
        return request.user.has_perm('research_mgt.is_mgt_superuser')


class IsContractOwner(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if type(view) in [views.ContractViewSet]:
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, models.Contract):
            if obj.owner == request.user:
                return True
        else:
            return False

        return False


class IsContractFormalSupervisor(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if type(view) in [views.ContractViewSet]:
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, models.Contract):
            if request.method == 'DELETE':
                return False
            elif request.user in obj.get_all_formal_supervisors():
                return True
        else:
            return False

        return False


class IsContractSupervisor(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if type(view) in [views.ContractViewSet]:
            return True
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        if isinstance(obj, models.Contract):
            if request.method == 'DELETE':
                return False
            elif request.user in obj.get_all_supervisors():
                return True
        else:
            return False

        return False


class IsContractSuperviseOwner(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        return False


class IsContractAssessmentExamineOwner(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        return False
