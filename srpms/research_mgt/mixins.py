from collections import OrderedDict

from django.utils import six
from django.db.models import Model
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from rest_framework.exceptions import NotFound
from rest_framework.viewsets import GenericViewSet
from rest_framework_extensions.settings import extensions_api_settings


class NestedGenericViewSet(GenericViewSet):
    """
    This ViewSet is a re-write of the original NestedViewSetMixin from rest_framework_extensions

    The original ViewSet is quite buggy regarding the following points:
    - It would return 200 even if the parent lookup does not exist
    - It would allow creation of objects for another parent object
    - It does not check whether requester has the permission to access parent object

    The rewrite is based on https://github.com/chibisov/drf-extensions/issues/142,
    credit to @Place1 for the ideas and sample implementation.
    """
    resolved_parents = OrderedDict()

    def initial(self, request, *args, **kwargs) -> None:
        """
        Resolve parent objects.

        Before every request to this nested viewset we want to resolve all the parent
        lookup kwargs into the actual model instances.

        We do this so that if they don't exist a 404 will be raised.

        We also cache the result on `self` so that if the request is a POST, PUT or
        PATCH the parent models can be reused in our perform_create and perform_update
        handlers to avoid accessing the DB twice.
        """
        try:
            # Parents resolve need to be done before initial(), as these parent
            # objects may be used for permission checking during initial().
            self.resolve_parent_lookup_fields()
            super(NestedGenericViewSet, self).initial(request, *args, **kwargs)
        except NotFound as exc:
            # If any parent notfound, render the response context and throw the exception.
            super(NestedGenericViewSet, self).initial(request, *args, **kwargs)
            raise exc

    def get_queryset(self):
        return self.filter_queryset_by_parents_lookups(
                super(NestedGenericViewSet, self).get_queryset()
        )

    def filter_queryset_by_parents_lookups(self, queryset):
        parents_query_dict = self.get_parents_query_dict()
        if parents_query_dict:
            try:
                return queryset.filter(**parents_query_dict)
            except ValueError:
                raise NotFound()
        else:
            return queryset

    def get_parents_query_dict(self) -> OrderedDict:
        result = OrderedDict()
        for kwarg_name, kwarg_value in six.iteritems(self.kwargs):
            if kwarg_name.startswith(
                    extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX):
                query_lookup = kwarg_name.replace(
                        extensions_api_settings.DEFAULT_PARENT_LOOKUP_KWARG_NAME_PREFIX,
                        '',
                        1
                )
                query_value = kwarg_value
                result[query_lookup] = query_value
        return result

    def resolve_parent_lookup_fields(self) -> None:
        """Update resolved parents to the instance variable"""

        parents_query_dict = self.get_parents_query_dict()

        keys = list(parents_query_dict.keys())

        for i in range(len(keys)):
            # the lookup key can be a django ORM query string like 'project__slug'
            # so we want to split on the first '__' to get the related field's name,
            # followed by the lookup string for the related model. Using the given
            # example the related field will be 'project' and the 'slug' property
            # will be the lookup on that related model

            # TODO: support django ORM query string, like 'project__slug'
            field = keys[i]
            value = parents_query_dict[keys[i]]

            related_descriptor: ForwardManyToOneDescriptor = getattr(self.queryset.model, field)
            related_model: Model = related_descriptor.field.related_model

            # The request must have all previous parents matched, for example
            # /contracts/2/assessment-methods/1/examine/ must satisfy assessment-method=1
            # can be query by contract=2
            previous_parents = {k: self.resolved_parents[k] for k in keys[:i]}

            try:
                self.resolved_parents[field] = related_model.objects.get(
                        **{'pk': value, **previous_parents})
            except related_model.DoesNotExist:
                raise NotFound()
