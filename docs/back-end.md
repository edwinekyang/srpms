# Models, serializers and their validation

- Validation for business logic and database model should be separated clearly, business logic should be validated by serializers, and database model should not touch these
  - [Differences between ModelSerializer validation and ModelForm.](https://www.django-rest-framework.org/community/3.0-announcement/#differences-between-modelserializer-validation-and-modelform)
  - [Django models, encapsulation and data integrity](https://www.dabapps.com/blog/django-models-and-encapsulation/)

# Limitations

- Cannot enforce contract to must have some assessment method in the back-end
  - For example, the current individual project contract must have "report", "artifact", and "presentation", however we current does not enforce that
- When convener approve examiner on examiner's behalf, the database model would not reflect that it is approved by some one else (i.e. the convener)