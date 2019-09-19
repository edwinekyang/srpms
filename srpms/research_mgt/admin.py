from django.contrib import admin

from .models import IndividualProject, SpecialTopics, Course
# Register your models here.

admin.site.register(IndividualProject)
admin.site.register(SpecialTopics)
admin.site.register(Course)
