from django.db import models
from accounts.models import SrpmsUser


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    course_number = models.CharField(max_length=8, default=None, null=True, blank=True)
    name = models.CharField(max_length=50, default=None, null=False, blank=False)


class Contract(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.IntegerField(default=None, null=False, blank=False)
    semester = models.CharField(max_length=20, default=None, null=False, blank=False)
    duration = models.IntegerField(default=None, null=False, blank=False)
    resources = models.CharField(max_length=200, default=None, null=False, blank=False)
    convener_approval_date = models.DateTimeField(default=None, null=True, blank=True)
    convener = models.ForeignKey(SrpmsUser, related_name='convener', on_delete=models.SET_NULL, default=None, blank=True, null=True)
    initial_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(SrpmsUser, related_name='user', on_delete=models.SET_NULL, default=None, blank=True, null=True)
    supervisor = models.ForeignKey(SrpmsUser, related_name='supervisor', on_delete=models.SET_NULL, default=None, blank=True, null=True)
    is_formal = models.BooleanField(default=False)
    supervisor_approval_date = models.DateTimeField(default=None, null=True, blank=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, default=None, blank=False, null=False)


class IndividualProject(Contract):
    title = models.CharField(max_length=100, default=None, null=False, blank=False)
    obj = models.CharField(max_length=200, default=None, null=False, blank=False)
    desc = models.CharField(max_length=500, default=None, null=False, blank=False)


class SpecialTopics(Contract):
    title = models.CharField(max_length=100, default=None, null=False, blank=False)
    obj = models.CharField(max_length=200, default=None, null=False, blank=False)
    desc = models.CharField(max_length=500, default=None, null=False, blank=False)
