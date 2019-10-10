"""Create actions that would be used in activity logging"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from research_mgt.models import ActivityAction
from django.apps.registry import Apps


# noinspection PyPep8Naming
def create_actions(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    TheAction: ActivityAction = apps.get_model('research_mgt', 'ActivityAction')

    TheAction.objects.create(name='contract_submit')
    TheAction.objects.create(name='contract_un_submit')
    TheAction.objects.create(name='contract_approve')
    TheAction.objects.create(name='contract_disapprove')
    TheAction.objects.create(name='supervise_approve')
    TheAction.objects.create(name='supervise_disapprove')
    TheAction.objects.create(name='examiner_approve')
    TheAction.objects.create(name='examiner_disapprove')


# noinspection PyPep8Naming
def revert_create_actions(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    TheAction: ActivityAction = apps.get_model('research_mgt', 'ActivityAction')

    TheAction.objects.filter(name__in=[
        'contract_submit',
        'contract_un_submit',
        'contract_approve',
        'contract_disapprove',
        'supervise_approve',
        'supervise_disapprove',
        'examiner_approve',
        'examiner_disapprove'
    ]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('research_mgt', '0004_create_courses'),
    ]

    operations = [
        migrations.RunPython(create_actions, revert_create_actions),
    ]
