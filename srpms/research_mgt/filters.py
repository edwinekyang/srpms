"""
Filters that enable query string for views. For example, 'api/user/?search=my_name'.
"""

__author__ = "Dajie (Cooper) Yang"
__credits__ = ["Dajie Yang", "Shang Wang", "Glader"]

__maintainer__ = "Dajie (Cooper) Yang"
__email__ = "dajie.yang@anu.edu.au"

from django_filters import FilterSet, BooleanFilter
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.db.models.query import QuerySet

from accounts.models import SrpmsUser


class UserFilter(FilterSet):
    """Filter that shows all users with/without 'can_supervise' permission"""

    is_approved_supervisor = BooleanFilter(method='filter_approved_supervisor')
    is_course_convener = BooleanFilter(method='filter_course_convener')

    class Meta:
        model = SrpmsUser
        fields = []

    # noinspection PyMethodMayBeStatic
    def filter_approved_supervisor(self, queryset: QuerySet, name, value: bool):
        """
        Filter function.

        Note that user being inside a group (with certain permission assigned to the group)
        would not automatically assign user to a Permission object. Thus we refer the method
        [here](https://stackoverflow.com/questions/378303/how-to-get-a-list-of-all-users-with-a-specific-permission-group-in-django)
        to query user given a permission.

        Args:
            queryset: the queryset of the view
            name: field name to apply the filter
            value: value that would be used to filter the query set
        """

        perm = Permission.objects.get(codename='can_supervise')

        if value:
            q = Q(groups__permissions=perm) | Q(user_permissions=perm) | Q(is_superuser=True)
            return queryset.filter(q).distinct()
        else:
            q = ~Q(groups__permissions=perm) & ~Q(user_permissions=perm) & Q(is_superuser=False)
            return queryset.filter(q).distinct()

    # noinspection PyMethodMayBeStatic
    def filter_course_convener(self, queryset: QuerySet, name, value: bool):
        """
        Filter uses with 'can_convene' permission

        Args:
            queryset: the queryset of the view
            name: field name to apply the filter
            value: value that would be used to filter the query set
        """

        perm = Permission.objects.get(codename='can_convene')

        if value:
            q = Q(groups__permissions=perm) | Q(user_permissions=perm) | Q(is_superuser=True)
            return queryset.filter(q).distinct()
        else:
            q = ~Q(groups__permissions=perm) & ~Q(user_permissions=perm) & Q(is_superuser=False)
            return queryset.filter(q).distinct()
