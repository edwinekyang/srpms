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
        requester: SrpmsUser = request.user

        # Approve GET, HEAD, and OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True

        # Approve normal login user to create contract etc.
        if type(view) in [views.ContractViewSet,
                          views.SuperviseViewSet,
                          views.AssessmentMethodViewSet]:
            return True

        # Approve superuser
        if requester.has_perm('research_mgt.is_mgt_superuser'):
            return True

        # Approve convener to create course and assessment template
        if requester.has_perm('research_mgt.can_convene') \
                and type(view) in [views.CourseViewSet,
                                   views.AssessmentTemplateViewSet]:
            return True

        return False

    def has_object_permission(self, request: Request, view, obj) -> bool:
        """
        Object level permission, covering PUT, PATCH, DELETE method of a given object.
        """

        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Enable type hint
        requester: SrpmsUser = request.user

        # Quickly approve superusers
        if requester.has_perm('research_mgt.is_mgt_superuser'):
            return True

        # Course object
        if isinstance(obj, models.Course):
            if requester.has_perm('research_mgt.can_convene'):
                # Convener can PUT, PATCH, DELETE
                return True
            else:
                return False

        # Contract object
        if isinstance(obj, models.Contract):
            if obj.is_convener_approved():
                # No PUT, PATCH, DELETE allow after final approval
                return False
            elif requester.has_perm('research_mgt.can_convene'):
                # Convener can PUT, PATCH, DELETE
                return True
            elif requester == obj.owner:
                # Allow PUT, PATCH, DELETE for owner
                return True
            elif requester.supervise.all() & obj.supervisor.all() \
                    and request.method in ['PUT', 'PATCH']:
                # Allow PUT, PATCH for formal supervisors of this contract
                return True
            else:
                return False

        # Supervise relation
        if isinstance(obj, models.Supervise):
            if obj.is_convener_approved():
                # No PUT, PATCH, DELETE allow after final approval
                return False
            elif requester.has_perm('research_mgt.can_convene'):
                # Allow PUT, PATCH, DELETE for convener
                return True
            elif requester == obj.supervisor:
                # Allow PUT, PATCH, DELETE for the supervisor him/herself
                return True
            elif requester.has_perm('research_mgt.approved_supervisors') \
                    and obj.contract in requester.supervise.all():
                # Allow PUT, PATCH, DELETE for approved supervisors
                # that are involved in this contract
                return True
            else:
                # Other user, including the contract owner don't have permission
                return False

        # AssessmentTemplate object
        if isinstance(obj, models.AssessmentTemplate):
            if requester.has_perm('research_mgt.can_convene'):
                # Allow PUT, PATCH, DELETE for convener
                return True
            else:
                return False

        # AssessmentMethod relation
        if isinstance(obj, models.AssessmentMethod):
            if obj.is_convener_approved():
                # No PUT, PATCH, DELETE allow after final approval
                return False
            elif requester.has_perm('research_mgt.can_convene'):
                # Allow PUT, PATCH, DELETE for convener
                return True
            elif request.method in ['PUT', 'PATCH'] and requester == obj.examiner:
                # Allow PUT, PATCH for examiner of this assessment
                return True
            elif requester == obj.contract.owner:
                # Allow PUT, PATCH, DELETE for contract owner
                return True
            elif requester.has_perm('research_mgt.approved_supervisors') \
                    and obj.contract in requester.supervise.all():
                # Allow PUT, PATCH, DELETE for approved supervisors
                # that are involved in this contract
                return True
            else:
                return False

        return False
