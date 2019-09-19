from django.db import models
from accounts.models import SrpmsUser


class Course(models.Model):
    course_number = models.CharField(max_length=8, default=None, null=False, blank=False)
    name = models.CharField(max_length=50, default=None, null=False, blank=False)


class Contract(models.Model):
    year = models.IntegerField(default=None, null=False, blank=False)
    semester = models.IntegerField(default=None, null=False, blank=False)
    duration = models.IntegerField(default=None, null=False, blank=False)
    resources = models.CharField(max_length=200, default=None, null=True, blank=True)
    convener_approval_date = models.DateTimeField(default=None, null=True, blank=True)
    convener = models.ForeignKey(SrpmsUser, related_name='convene', on_delete=models.CASCADE, default=None, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(SrpmsUser, related_name='own', on_delete=models.CASCADE, default=None, blank=False, null=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=None, blank=False, null=False)


class Supervise(models.Model):
    supervisor = models.ForeignKey(SrpmsUser, on_delete=models.CASCADE, default=None, blank=False, null=False)
    is_formal = models.BooleanField(default=False)
    supervisor_approval_date = models.DateTimeField(default=None, null=True, blank=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, default=None, blank=False, null=False)


class IndividualProject(Contract):
    title = models.CharField(max_length=100, default=None, null=False, blank=False)
    object = models.CharField(max_length=200, default=None, null=False, blank=False)
    description = models.CharField(max_length=500, default=None, null=False, blank=False)


class SpecialTopics(Contract):
    title = models.CharField(max_length=100, default=None, null=False, blank=False)
    object = models.CharField(max_length=200, default=None, null=False, blank=False)
    description = models.CharField(max_length=500, default=None, null=False, blank=False)


class AssessmentTemplate(models.Model):
    name = models.CharField(max_length=100, default=None, null=False, blank=False)
    description = models.CharField(max_length=200, default=None, null=True, blank=True)


class AssessmentMethod(models.Model):
    template = models.ForeignKey(AssessmentTemplate, on_delete=models.CASCADE, null=False, blank=False)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=False, blank=False)
    additional_description = models.CharField(max_length=200, default=None, null=True, blank=True)
    due = models.DateField(default=None, null=True, blank=True)
    max = models.IntegerField(default=None, null=False, blank=False)
    examiner = models.ForeignKey(SrpmsUser, on_delete=models.CASCADE, default=None, null=True, blank=True)
    examiner_approval_date = models.DateTimeField(default=None, null=True, blank=True)
