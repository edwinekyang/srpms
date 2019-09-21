from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.request import Request

from . import models
from . import views
from accounts.models import SrpmsUser


class DefaultObjectPermission(permissions.BasePermission):

    def has_permission(self, request: Request, view: viewsets.ModelViewSet) -> bool:
        """
        Determine permission against views, for GET, HEAD, OPTIONS, and POST methods,
        PUT, PATCH, DELETE are object level.
        """

        # Enable type hint
        request_user: SrpmsUser = request.user

        # Approve GET, HEAD, and OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True

        # Approve superuser
        if request_user.has_perm('research_mgt.is_mgt_superuser'):
            return True

        # Approve convener
        if request_user.has_perm('research_mgt.can_convene') \
                and type(view) in [views.CourseViewSet,
                                   views.AssessmentTemplateViewSet]:
            return True

        # Approve normal login user
        if type(view) in [views.ContractViewSet,
                          views.SuperviseViewSet,
                          views.AssessmentMethodViewSet]:
            return True

        return False

    def has_object_permission(self, request: Request, view, obj) -> bool:
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Enable type hint
        request_user: SrpmsUser = request.user

        # Quickly approve superusers
        if request_user.has_perm('research_mgt.is_mgt_superuser'):
            return True

        # Course object
        if isinstance(obj, models.Course):
            if request_user.has_perm('research_mgt.can_convene'):
                # Convener can POST, PUT, PATCH, DELETE
                return True
            else:
                return False

        # Contract object
        if isinstance(obj, models.Contract):
            if obj.is_convener_approved():
                # No POST, PUT, PATCH, DELETE allow after final approval
                return False
            elif obj.is_submitted():
                # No POST, PUT, PATCH, DELETE allow after owner submit
                return False
            elif request_user == obj.owner:
                # Allow POST, PUT, PATCH, DELETE for owner
                return True
            else:
                return False

        if isinstance(obj, models.Supervise):
            pass

        if isinstance(obj, models.AssessmentTemplate):
            pass

        if isinstance(obj, models.AssessmentMethod):
            pass

        # Write permissions are only allowed to the owner of the snippet.
        return False
