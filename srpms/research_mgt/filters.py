from django_filters import FilterSet, BooleanFilter
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.db.models.query import QuerySet

from accounts.models import SrpmsUser


class UserFilter(FilterSet):
    is_approved_supervisor = BooleanFilter(method='filter_approved_supervisor')

    class Meta:
        model = SrpmsUser
        fields = []

    def filter_approved_supervisor(self, queryset: QuerySet, name, value: bool):
        perm = Permission.objects.get(codename='can_supervise')

        if value:
            q = Q(groups__permissions=perm) | Q(user_permissions=perm) | Q(is_superuser=True)
            return queryset.filter(q).distinct()
        else:
            q = ~Q(groups__permissions=perm) & ~Q(user_permissions=perm) & Q(is_superuser=False)
            return queryset.filter(q).distinct()
