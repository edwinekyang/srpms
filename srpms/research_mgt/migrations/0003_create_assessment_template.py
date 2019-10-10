"""
Create assessment templates according to existing contract templates available on
https://cs.anu.edu.au/courses/CSPROJECTS/
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from research_mgt.models import AssessmentTemplate
from django.apps.registry import Apps


# noinspection PyPep8Naming
def create_assessment_templates(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    """Create some sample assessment template"""
    TheAssessmentTemplate: AssessmentTemplate = apps.get_model('research_mgt', 'AssessmentTemplate')

    TheAssessmentTemplate.objects.create(
            name='report',
            description='e.g. research report, software description, ...',
            max_weight=90,
            min_weight=45,
            default_weight=60
    )
    TheAssessmentTemplate.objects.create(
            name='artifact',
            description='e.g. software, user interface, robot, ...',
            max_weight=45,
            min_weight=0,
            default_weight=30
    )
    TheAssessmentTemplate.objects.create(
            name='presentation',
            description='',
            max_weight=10,
            min_weight=10,
            default_weight=10
    )
    TheAssessmentTemplate.objects.create(
            name='custom',
            description='',
            max_weight=100,
            min_weight=0,
            default_weight=50
    )


# noinspection PyPep8Naming
def revert_create_assessment_templates(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    TheAssessmentTemplate: AssessmentTemplate = apps.get_model('research_mgt', 'AssessmentTemplate')

    TheAssessmentTemplate.objects.filter(name__in=[
        'report',
        'artifact',
        'presentation',
        'custom'
    ]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('research_mgt', '0002_create_group_permission'),
    ]

    operations = [
        migrations.RunPython(create_assessment_templates, revert_create_assessment_templates),
    ]
