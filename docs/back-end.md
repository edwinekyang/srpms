# File Structure

```
srpms/
├── accounts                 # Account app
│   ├── migrations/              # Database migration for this app
│   ├── __init__.py
│   ├── admin.py                 # Django admin page configuration
│   ├── apps.py                  # App config and initialization
│   ├── authentication.py        # ANU LDAP Authentication backend
│   ├── models.py                # Database schema for this app
│   ├── serializers.py           # Data serializers for encode/decode JSON for API
│   ├── tests.py                 # Tests for this app
│   ├── urls.py                  # How this app locate itself in url
│   └── views.py                 # Views handle requests and generate response
├── research_mgt             # Research management system app
│   ├── migrations/              # Database migration for this app
│   ├── static/                  # Static resources for generate contract PDF
│   │   └── research_mgt/
│   ├── templates/               # HTML templates for generate contract PDF
│   │   └── research_mgt/
│   ├── tests/                   # Tests for this app
│   ├── __init__.py
│   ├── admin.py                 # Django admin page configuration
│   ├── apps.py                  # App config and initialization
│   ├── filters.py               # Filters that enable url query, e.g. '?key=value'
│   ├── mixins.py                # Custom mixins to support nested url
│   ├── models.py                # Database schema for this app
│   ├── permissions.py           # Permission control for request sender
│   ├── print.py                 # Print contract to PDF
│   ├── serializers.py           # Data serializers for encode/decode JSON for API
│   ├── serializer_utils.py      # Custom serializer field
│   ├── signals.py               # Define signals, and send notifications on signal
│   ├── urls.py                  # How this app locate itself in url
│   └── views.py                 # Views handle requests and generate response
├── srpms                    # System configuration
│   ├── __init__.py
│   ├── settings.py          # System settings
│   ├── urls.py              # Root url
│   ├── utils.py             # Custom exception handler for server error
│   └── wsgi.py
├── Dockerfile               # Dockerfile for building the django image
├── manage.py
└── start.sh                 # Start up script (only for docker use)
```

# Apps in Django Project

A Django project consists of one or more app, each app represents a distinct set of functionalities you want to deliver to user.

In this project, our main goal is to provide the research contract management system, and all functionalities regarding this goal would provided through the `research_mgt` app.

We also have a separate app `accounts` providing user management and authentication functionalities. This set of functionalities is separated from `research_mgt` for the consideration that user management and authentication is not app specific, and might be used for other apps (in the case that we have other apps in the future).

## General Structure of a Django App

The typical structure of a Django app is as follow:

```
app-name/
├── migrations/
├── __init__.py
├── admin.py
├── apps.py
├── authentication.py
├── models.py
├── serializers.py
├── tests.py
├── urls.py
└── views.py
```

## Django REST framework

# Authentication

## ANU LDAP Authentication



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
- Users are allowed to create, edit, delete for their own contract

### User

- Read-only for everyone

## Implications

- Convener does not have permission to edit, delete contract, and its assessments.
- Supervisor can only nominate examiner and approve supervise relation, but not edit assessment or contract
- Convener can bypass the `is_all_assessment_approved` integrity check

# Limitations

- Cannot enforce contract to must have some assessment method in the back-end
  - For example, the current individual project contract must have "report", "artifact", and "presentation", however we current does not enforce that
- When convener approve examiner on examiner's behalf, the database model would not reflect that it is approved by some one else (i.e. the convener)