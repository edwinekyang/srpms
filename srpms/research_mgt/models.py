from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import SrpmsUser


class Course(models.Model):
    course_number = models.CharField(max_length=8, null=False, blank=False)
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name


class Contract(models.Model):
    year = models.IntegerField(null=False, blank=False)
    semester = models.IntegerField(null=False, blank=False)
    duration = models.IntegerField(null=False, blank=False)
    resources = models.CharField(max_length=200, blank=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, blank=False, null=False)

    convener = models.ForeignKey(SrpmsUser, related_name='convene', on_delete=models.PROTECT,
                                 blank=False, null=False)
    convener_approval_date = models.DateTimeField(null=True, blank=True)

    owner = models.ForeignKey(SrpmsUser, related_name='own', on_delete=models.PROTECT,
                              blank=False, null=False)
    create_date = models.DateTimeField(auto_now_add=True)


class Supervise(models.Model):
    supervisor = models.ForeignKey(SrpmsUser, related_name='supervise',
                                   on_delete=models.PROTECT, blank=False, null=False)
    is_formal = models.BooleanField(blank=False, null=False)
    supervisor_approval_date = models.DateTimeField(null=True, blank=True)
    contract = models.ForeignKey(Contract, related_name='supervisor',
                                 on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        unique_together = ('id', 'supervisor', 'contract')


class IndividualProject(Contract):
    title = models.CharField(max_length=100, null=False, blank=False)
    objectives = models.CharField(max_length=200, null=False, blank=False)
    description = models.CharField(max_length=500, null=False, blank=False)

    def __str__(self):
        return self.title


class SpecialTopics(Contract):
    title = models.CharField(max_length=100, null=False, blank=False)
    objectives = models.CharField(max_length=200, null=False, blank=False)
    description = models.CharField(max_length=500, null=False, blank=False)

    def __str__(self):
        return self.title


class AssessmentTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    description = models.CharField(max_length=200, blank=True)
    max_mark = models.IntegerField(null=False, blank=False)
    min_mark = models.IntegerField(null=False, blank=False)
    default_mark = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class AssessmentMethod(models.Model):
    template = models.ForeignKey(AssessmentTemplate, related_name='assessment_method',
                                 on_delete=models.PROTECT, null=False, blank=False)
    contract = models.ForeignKey(Contract, related_name='assessment_method',
                                 on_delete=models.CASCADE, null=False, blank=False)
    additional_description = models.CharField(max_length=200, blank=True)
    due = models.DateTimeField(null=True, blank=True)
    max_mark = models.IntegerField(null=False, blank=False)
    examiner = models.ForeignKey(SrpmsUser, related_name='examine',
                                 on_delete=models.PROTECT, null=False, blank=False)
    examiner_approval_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('id', 'contract', 'examiner')

    def clean(self):
        """
        Apply constraint to the model
        """
        if self.max_mark > self.template.max_mark or self.max_mark < self.template.min_mark:
            raise ValidationError("Please keep the mark within the valid range")

    def save(self, *args, **kwargs):
        self.full_clean()
        super(AssessmentMethod, self).save(*args, **kwargs)


class AppPermission(models.Model):
    """A dummy model for holding permissions for this app"""
    class Meta:
        managed = False  # Do not create database table
