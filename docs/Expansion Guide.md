**NOTE: While this guide would provide most information you need, reading the official tutorial to get a basic idea about [Django](https://docs.djangoproject.com/en/2.2/intro/) and [REST framework](https://www.django-rest-framework.org/tutorial/1-serialization/) is still highly recommended. Completion of these two series of tutorials should only take no more than 1.5 day.**

# Back-end

## Simple code walk through

The `/srpms` directory current holds the Django back-end, of which we have two application `accounts` and `research_mgt`, and `srpms` holding the Django settings

```
/srpms
├── accounts/
├── research_mgt/
├── srpms/
└── ...
```

The `/srpms/srpms/urls.py` defines the root URL

```python
# /srpms/srpms/urls.py

# ...

urlpatterns = [
    ...
    path('api/research_mgt/', include('research_mgt.urls')),
    path('api/accounts/', include('accounts.urls')),
]
```

which imports each application's URL configuration.

The `reserach_mgt` application holds most of the logic, and it is URL is configured as follow:

```python
# /srpms/research_mgt/urls.py

from .views import (UserViewSet, ContractViewSet, SuperviseViewSet, ...)

# ...

router = ExtendedDefaultRouter()

# register UserViewSet
router.register(r'users', UserViewSet)

# register ContractViewSet
contract_routes = router.register(r'contracts', ContractViewSet, basename='contract')

# register SuperviseViewSet
contract_routes.register(r'supervise',
                         SuperviseViewSet,
                         basename='contract-supervise',
                         parents_query_lookups=['contract'])

# ...
```

The router would automatically register all views in a ViewSet:

- A ViewSet typically have a list view and detail view. In the case of `UserViewSet`, it is `/api/research_mgt/users/` and `/api/research_mgt/users/<id>/`, where `<id>` is the primary key of a user.
- Router would also register other views in a ViewSet automatically. For example, the special action `approve` of the `ContractViewSet` would be at `/api/research_mgt/contracts/<id>/approve`. For more detail about ViewSet actions, see [the official docs about extra actions for routing](https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing)
- In the case of nested router, `parents_query_lookups` defines the field that would be used for filtering objects. For example, the `SuperviseViewSet` would filter its queryset by `contract`, details about queryset would be discussed later.

the `XXXViewSet` is the place where response would be handled, and is defined in each application's `views.py`, for example:

```python
# /srpms/research_mgt/views.py

from .serializers import (SuperviseSerializer, ...)
from .models import (Supervise, ...)
from .permissions import (AllowSafeMethods, ...)

# ...

class SuperviseViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin,
                       DestroyModelMixin, ListModelMixin, NestedGenericViewSet):
    
    queryset = Supervise.objects.all()
    serializer_class = SuperviseSerializer
    permission_classes = [AllowSafeMethods, ...]

    def perform_create(...):
        # override default method, add business logic before creation
        return super(...)
    
    def perform_update(...):
        # override default method, add business logic before update
        return super(...)
```

In a `ViewSet`,  there are:

- `queryset` defines objects that would be available when request hit this view. Here we connect to all objects in the `Supervise` model
- `serializer_class` defines the serializer that would be used to convert between Python object and text representation
- `permission_classes` defines permissions that must be met for each request. All permissions in that list must be met, any fail would return HTTP 403. However you can use `[A|B, C, ...]` to apply OR logic

A `ViewSet` also have multiple functions that can be override:

- `perform_create()` would be executed before calling the serializer to perform actual creation
- `perform_update()` would be executed before calling the serializer to perform actual creation
- Consult [docs of generic view](https://www.django-rest-framework.org/api-guide/generic-views/) and [docs of ViewSet](https://www.django-rest-framework.org/api-guide/viewsets/) to know more about mixins, viewset, and available overrides

The above `SuperviseViewSet` is connected to the `Supervise` model, which is defined in `models.py` using Django ORM:

```python
# /srpms/research_mgt/models.py

from django.db import models

class Supervise(models.Model):
    supervisor = models.ForeignKey(...)
    is_formal = models.BooleanField(...)
    supervisor_approval_date = models.DateTimeField(...)
    contract = models.ForeignKey(...)
    nominator = models.ForeignKey(...)
    
    class Meta:
        unique_together = ('supervisor', 'contract')
        
    def clean(...):
        # Model level constraints
    
    def save(...):
        self.full_clean()
        return super(...)
```

This model would:

- Automatically have an auto-increment field `id` as primary key
- Defines the following attributes in the supervise schema: `supervisor`, `is_formal`, `supervisor_approval_date`, `contract`, and `nominator`
- Make sure `supervisor` and `contract` attributes are unique together
- Have model level constraints specified in `clean()`, i.e. relations between attributes
- However the model level constraints would not be applied automatically, thus we need to call `full_clean()` before `save()`
- Consult [official docs about model](https://docs.djangoproject.com/en/2.2/topics/db/models/) to know more about Django ORM.

Recall that the `SuperviseViewSet` is also connected to the `SuperviseSerializer`, which is defined in `serializers.py`:

```python
# /srpms/research_mgt/serializers.py

from rest_framework import serializers

class SuperviseSerializer(serializers.ModelSerializer):
    
    # ...
    contract = serializers.PrimaryKeyRelatedField(read_only=True)
    is_formal = serializers.ReadOnlyField()
    # ...
    
    class Meta:
        model = Supervise
        fields = ['id', 'contract', 'supervisor', 'is_formal', 'nominator']
    
    def create(...):
        # business logic
        return super(...)
    
    def update(...):
        # business logic
        return super(...)
```

The serializer defines:

- The model it'll connect to in its `Meta` class
- The serializer would automatically recognize all fields in a model, however it would not automatically includes them during serialization. Thus we need to specify the list of fields that we want to expose in `fields`.
- The field can be override by defining them as class variables, for example the `is_formal` field is being specified as read-only.
- In the case that a field is a foreign key, it would by default use its related object's primary key.
- `create()` customize the object creation behavior, is called by the `perform_create()` function from views
- `update()` customize the object creation behavior, is called by the `perform_create()` function from views
- Consult [official docs of serializer](https://www.django-rest-framework.org/api-guide/serializers/) for more information

The `SuperviseViewSet` uses permissions define in `permissions.py`, example permission is defined as:

```python
# /srpms/research_mgt/permissions.py

from rest_framework.permissions import BasePermission

class AllowSafeMethods(BasePermission):
    """Allow HTTP methods that are considered safe, i.e. GET, HEAD, OPTIONS"""

    message = 'Only safe method is allowed'

    def has_permission(...) -> bool:
        # ...

    def has_object_permission(...) -> bool:
        # ...
```

where:

- `message` defines the response body if a HTTP 403 will be raised
- `has_permission()` check whether a request has permission for a ViewSet.
- `has_object_permission()` check whether a request has perm to the object it tries to access in that ViewSet, note that this would not be checked if `has_permission()` failed. This check only applies to detail view of a ViewSet.

## Notifications and signals

Theoretically, notifications can be triggered anywhere you prefer. The project currently implements the signals like below:

```python
# /srpms/research_mgt/signals.py

from django.dispatch import receiver, Signal
from django.core.mail import send_mail

CONTRACT_SUBMIT = Signal(providing_args=['contract', 'activity_log'])

# ...

@receiver(CONTRACT_SUBMIT, dispatch_uid='contract_submit')
def contract_submit_notifications(contract, activity_log, ...):
    # ...
    send_mail(...)
    
# ...
```

Where:

- `CONTRACT_SUBMIT` is a signal, and `providing_args` defines the arguments this signal would provide to its receivers.
- `contract_submit_notifications` receive the `CONTRACT_SUBMIT` signal, and use `send_mail()` to send email notification.

Example of sending signal:

```python
# /srpms/reserach_mgt/views.py

from .signals import (CONTRACT_SUBMIT, ...)
from rest_framework.decorators import action

class ContractViewSet(...):
    
    # ...
    
    @action(...)
    def submit(...) -> HttpResponse:
        # perform business logic
        
        CONTRACT_SUBMIT.send(...)
        
        return ...
```

[Official docs about signals](https://docs.djangoproject.com/en/2.2/topics/signals/)

## Supporting review functions

**It should be noted that detail functionalities about review is not being discussed thoroughly. This section should only serve as an unreliable reference, as it does not include any considerations including software patten, architecture, or user experience.**

**Note:**  refer to previous sections about how to place these code, every previous code snippets all gave its file name and path at top.

Since a review is tight to a contract, the review model should link to the contract model:

```python
from research_mgt.models import Contract

class Review(models.Model):
    contract = models.OneToOneField(Contract, ...)
    
    # Other necessary fields ...
```

and then, define corresponding serializer:

```python
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    contract = serializers.PrimaryKeyRelatedField(read_only=True)
    
    # Other fields' override ..

    class Meta:
        model = Review
        fields = ['id', 'contract', ...]
```

and corresponding views:

```python
class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = ...
    
    # And other possible logics
    
    # ...
```

and finally register it to the router:

```python
router.register(r'users', ReviewViewSet)
```

For supporting file uploads, the current SRPMS does not have similar implementation, please refer to the [official docs about file update](https://www.django-rest-framework.org/api-guide/parsers/#fileuploadparser) for more details