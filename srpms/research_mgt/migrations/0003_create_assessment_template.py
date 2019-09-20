"""
Create sample assessment templates.
"""

__author__ = 'Dajie Yang'
__email__ = 'dajie.yang@anu.edu.au'

from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from research_mgt.models import AssessmentTemplate
from django.apps.registry import Apps


def create_assessment_templates(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    """Create some sample assessment template"""
    TheAssessmentTemplate: AssessmentTemplate = apps.get_model('research_mgt', 'AssessmentTemplate')

    TheAssessmentTemplate.objects.create(
            name='report',
            description='e.g. research report, software description, ...',
            max_mark=90,
            min_mark=45,
            default_mark=60
    )
    TheAssessmentTemplate.objects.create(
            name='artifact',
            description='e.g. software, user interface, robot, ...',
            max_mark=45,
            min_mark=0,
            default_mark=30
    )
    TheAssessmentTemplate.objects.create(
            name='presentation',
            description='',
            max_mark=10,
            min_mark=10,
            default_mark=10
    )
    TheAssessmentTemplate.objects.create(
            name='custom',
            description='',
            max_mark=100,
            min_mark=0,
            default_mark=50
    )


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
