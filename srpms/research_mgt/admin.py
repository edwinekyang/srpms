from django.contrib import admin

from .models import IndividualProject, SpecialTopic, Course
# Register your models here.

admin.site.register(IndividualProject)
admin.site.register(SpecialTopic)
admin.site.register(Course)
