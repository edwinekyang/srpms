# Models, serializers and their validation

- Validation for business logic and database model should be separated clearly, business logic should be validated by serializers, and database model should not touch these
  - [Differences between ModelSerializer validation and ModelForm.](https://www.django-rest-framework.org/community/3.0-announcement/#differences-between-modelserializer-validation-and-modelform)
  - [Django models, encapsulation and data integrity](https://www.dabapps.com/blog/django-models-and-encapsulation/)

# Permissions

## Groups & Permissions

- Permissions
  - `can_convene`
  - `can_supervise`
  - `is_mgt_superuser`
- Groups:
  - `approved_supervisors`, has permission `can_supervise`
  - `course_convener`, has permission `can_convene`
  - `mgt_superusers`, has permission `is_mgt_superuser`

## APP: Research_mgt

**NOTE: "Users" implies any login users, rules in lower order would not be reached if higher order rule passed **

### Course

- Users with `is_mgt_superuser` permission are allowed to create, edit, delete
- Users with `can_convene` permission is allowed to create, edit, delete

### Contract

- Users with `is_mgt_superuser` permission are allowed to create, edit, delete
- Users aren't allowed to edit, delete if the contract has approved by convener
- Users are allowed to create contract with them being the owner of the contract
- Users are allowed to edit, delete if they own the contract
- Users are allowed to edit for their supervise contract

### Supervise

- Users with `is_mgt_superuser` permission are allowed to create, edit, delete
- Users aren't allowed to create, edit, delete after the related contract has approved by convener
- Users with `can_convene` permission are allowed to create, edit, delete
- Users are allowed to create, edit, delete for their own contract
- Users are allowed to edit, delete for their supervise contract
- Users with `can_supervise` permission are allowed to create, edit, delete for their supervise contract

### AssessmentTemplate

- Users with `is_mgt_superuser` permission are allowed to create, edit, delete
- Users with `can_convene` permission is allowed to create, edit, delete

### AssessmentMethod

- Users with `is_mgt_superuser` permission are allowed to create, edit, delete
- Users aren't allowed to create, edit, delete after the related contract has approved by convener
- Users with `can_convene` permission are allowed to create, edit, delete
- Users are allowed to edit if they are the examiner of this assessment
- Users are allowed to create, edit, delete for their own contract
- Users are allowed to create, edit, delete for their supervise contract

### User

- Read-only for everyone

# Limitations

- Cannot enforce contract to must have some assessment method in the back-end
  - For example, the current individual project contract must have "report", "artifact", and "presentation", however we current does not enforce that
- When convener approve examiner on examiner's behalf, the database model would not reflect that it is approved by some one else (i.e. the convener)