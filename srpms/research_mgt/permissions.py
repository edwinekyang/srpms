from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.request import Request

from . import models
from . import views
from accounts.models import SrpmsUser


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True


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
        return False

    def has_object_permission(self, request, view, obj) -> bool:
        pass


class IsContractFormalSupervisor(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        pass

    def has_object_permission(self, request, view, obj) -> bool:
        pass


class IsContractSupervisor(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        pass

    def has_object_permission(self, request, view, obj) -> bool:
        pass


class IsContractSuperviseOwner(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        pass

    def has_object_permission(self, request, view, obj) -> bool:
        pass


class IsContractAssessmentExamineOwner(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        pass

    def has_object_permission(self, request, view, obj) -> bool:
        pass
