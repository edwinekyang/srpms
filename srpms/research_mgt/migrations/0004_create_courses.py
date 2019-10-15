"""
Create courses according to courses specified on https://cs.anu.edu.au/courses/CSPROJECTS/
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from research_mgt.models import Course
from django.apps.registry import Apps


# noinspection PyPep8Naming
def create_courses(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    TheCourse: Course = apps.get_model('research_mgt', 'Course')

    TheCourse.objects.create(course_number='COMP2710',
                             name='Special Topics in Computer Science', units=6)
    TheCourse.objects.create(course_number='COMP3710',
                             name='Topics in Computer Science', units=6)
    TheCourse.objects.create(course_number='COMP3740',
                             name='Project Work in Computing', units=6)
    TheCourse.objects.create(course_number='COMP3770',
                             name='Individual Research Project', units=6)
    TheCourse.objects.create(course_number='COMP4560',
                             name='Advanced Computing Project', units=12)
    TheCourse.objects.create(course_number='COMP6470',
                             name='Special Topics in Computing', units=6)
    TheCourse.objects.create(course_number='COMP8755',
                             name='Individual Computing Project', units=12)


# noinspection PyPep8Naming
def revert_create_courses(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    TheCourse: Course = apps.get_model('research_mgt', 'Course')

    TheCourse.objects.filter(course_number__in=[
        'COMP2710',
        'COMP3710',
        'COMP3740',
        'COMP3770',
        'COMP4560',
        'COMP6470',
        'COMP8755'
    ]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('research_mgt', '0003_create_assessment_template'),
    ]

    operations = [
        migrations.RunPython(create_courses, revert_create_courses),
    ]
