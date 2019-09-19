"""
Create group and assign related permissions for this app.
"""

__author__ = 'Dajie Yang'
__email__ = 'dajie.yang@anu.edu.au'

from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps.registry import Apps

from research_mgt.models import ResearchManagementPermission


def create_group_permission(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    """
    Create group for approved supervisor and course convener

    Note that we can't import models directly as it may be a newer version than
    this migration expects. We use the historical version through apps.get_model
    """

    TheGroup: Group = apps.get_model('auth', 'Group')
    ThePermission: Permission = apps.get_model('auth', 'Permission')
    TheContentType: ContentType = apps.get_model('contenttypes', 'ContentType')
    TheMGTPermission: ResearchManagementPermission = apps.get_model('research_mgt',
                                                                    'ResearchManagementPermission')

    ThePermission.objects.create(codename='can_convene',
                                 name='can be course convener of contracts',
                                 content_type=TheContentType.objects.get_for_model(
                                         TheMGTPermission))
    ThePermission.objects.create(codename='can_supervise',
                                 name='can supervise contracts as a formal supervisor',
                                 content_type=TheContentType.objects.get_for_model(
                                         TheMGTPermission))
    ThePermission.objects.create(codename='is_mgt_superuser',
                                 name='can read, create, update, delete anything',
                                 content_type=TheContentType.objects.get_for_model(
                                         TheMGTPermission))

    supervise = TheGroup.objects.create(name='approved_supervisors')
    supervise.permissions.set([ThePermission.objects.get(codename='can_supervise')])

    convene = TheGroup.objects.create(name='course_convener')
    convene.permissions.set([ThePermission.objects.get(codename='can_convene')])

    superuser = TheGroup.objects.create(name='mgt_superusers')
    superuser.permissions.set([ThePermission.objects.get(codename='is_mgt_superuser')])


def revert_create_group_permission(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    """
    Revert what's done in create_group_permission
    """
    TheGroup: Group = apps.get_model('auth', 'Group')
    ThePermission: Permission = apps.get_model('auth', 'Permission')

    TheGroup.objects.filter(name__in=[
        'approved_supervisors',
        'course_convener',
        'mgt_superusers'
    ]).delete()

    ThePermission.objects.get(codename__in=[
        'can_convene',
        'can_supervise',
        'is_mgt_superuser'
    ]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('research_mgt', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_group_permission, revert_create_group_permission),
    ]
