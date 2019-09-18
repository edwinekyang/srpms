from django.db import models
from accounts.models import SrpmsUser


class Course(models.Model):
    course_number = models.CharField(max_length=8, null=False, blank=False)
    name = models.CharField(max_length=50, null=False, blank=False)


class Contract(models.Model):
    year = models.IntegerField(null=False, blank=False)
    semester = models.IntegerField(null=False, blank=False)
    duration = models.IntegerField(null=False, blank=False)
    resources = models.CharField(max_length=200, blank=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, blank=False, null=False)

    convener = models.ForeignKey(SrpmsUser, related_name='convene', on_delete=models.PROTECT,
                                 blank=True, null=True)
    convener_approval_date = models.DateTimeField(null=True, blank=True)

    owner = models.ForeignKey(SrpmsUser, related_name='own', on_delete=models.PROTECT,
                              blank=False, null=False)
    create_date = models.DateTimeField(auto_now_add=True)


class Supervise(models.Model):
    supervisor = models.ForeignKey(SrpmsUser, on_delete=models.PROTECT, blank=False, null=False)
    is_formal = models.BooleanField(blank=False, null=False)
    supervisor_approval_date = models.DateTimeField(null=True, blank=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, blank=False, null=False)


class IndividualProject(Contract):
    title = models.CharField(max_length=100, null=False, blank=False)
    objectives = models.CharField(max_length=200, null=False, blank=False)
    description = models.CharField(max_length=500, null=False, blank=False)


class SpecialTopics(Contract):
    title = models.CharField(max_length=100, null=False, blank=False)
    objectives = models.CharField(max_length=200, null=False, blank=False)
    description = models.CharField(max_length=500, null=False, blank=False)


class AssessmentTemplate(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.CharField(max_length=200, blank=True)


class AssessmentMethod(models.Model):
    template = models.ForeignKey(AssessmentTemplate, on_delete=models.PROTECT,
                                 null=True, blank=True)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=False, blank=False)
    additional_description = models.CharField(max_length=200, blank=True)
    due = models.DateTimeField(null=True, blank=True)
    max = models.IntegerField(null=False, blank=False)
    examiner = models.ForeignKey(SrpmsUser, on_delete=models.PROTECT, null=False, blank=False)
    examiner_approval_date = models.DateTimeField(null=True, blank=True)
