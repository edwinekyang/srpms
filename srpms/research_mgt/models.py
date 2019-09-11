from django.db import models


class Contract(models.Model):
    contract_id = models.AutoField(primary_key=True)
    year = models.IntegerField(default=None, null=False, blank=False)
    semester = models.CharField(max_length=20, null=False, blank=False)
    duration = models.IntegerField(default=None, null=False, blank=False)
    res = models.CharField(max_length=200, null=False, blank=False)
    ca_date = models.DateTimeField(default=None, null=True, blank=True)
    c_id = models.ForeignKey('accounts.SrpmsUser', related_name='convener_id', on_delete=models.SET_NULL, default=None, blank=True, null=True)
    i_date = models.DateTimeField(auto_now_add=True)
    u_id = models.ForeignKey('accounts.SrpmsUser', related_name='user_id', on_delete=models.SET_NULL, default=None, blank=True, null=True)
    s_id = models.ForeignKey('accounts.SrpmsUser', related_name='supervisor_id', on_delete=models.SET_NULL, default=None, blank=True, null=True)
    is_formal = models.BooleanField(default=False)
    sa_date = models.DateTimeField(default=None, null=True, blank=True)
    course_id = models.ForeignKey('Course', on_delete=models.CASCADE, default=None, blank=False, null=False)


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_number = models.CharField(max_length=8, default=None, null=True, blank=True)
    name = models.CharField(max_length=50, default=None, null=False, blank=False)


class IndividualProject(Contract):
    title = models.CharField(max_length=100, default=None, null=False, blank=False)
    obj = models.CharField(max_length=200, default=None, null=False, blank=False)
    desc = models.CharField(max_length=500, default=None, null=False, blank=False)


class SpecialTopics(Contract):
    title = models.CharField(max_length=100, default=None, null=False, blank=False)
    obj = models.CharField(max_length=200, default=None, null=False, blank=False)
    desc = models.CharField(max_length=500, default=None, null=False, blank=False)