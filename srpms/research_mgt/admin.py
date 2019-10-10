"""
Controls the list of objects that can be manipulated through django admin site
"""

__author__ = 'Dajie (Cooper) Yang, and Euikyum (Edwin) Yang'
__credits__ = ['Dajie Yang', 'Euikyum Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from django.contrib import admin

from .models import (Course, AssessmentTemplate, IndividualProject, SpecialTopic, Supervise,
                     Assessment, Examine, AssessmentExamine)

admin.site.register(Course)
admin.site.register(AssessmentTemplate)
admin.site.register(IndividualProject)
admin.site.register(SpecialTopic)
admin.site.register(Supervise)
admin.site.register(Assessment)
admin.site.register(Examine)
admin.site.register(AssessmentExamine)
