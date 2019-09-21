from datetime import datetime, MINYEAR, MAXYEAR
from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError
from accounts.models import SrpmsUser


def get_semester() -> int:
    """Return the next semester with regards to the current time"""
    current = datetime.now()
    if current.month > 9 or current.month < 3:
        return 1
    else:
        return 2


class Course(models.Model):
    course_number = models.CharField(max_length=20, null=False, blank=False, unique=True)
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name


class Contract(models.Model):
    year = models.IntegerField(null=False, blank=False, default=datetime.now().year, validators=[
        validators.MinValueValidator(MINYEAR, 'Year number should > {}'.format(MINYEAR)),
        validators.MaxValueValidator(MAXYEAR, 'Year number should < {}'.format(MAXYEAR)),
    ])
    semester = models.IntegerField(null=False, blank=False, default=get_semester(), validators=[
        validators.MinValueValidator(1, 'Semester number should >= 1'),
        validators.MaxValueValidator(2, 'Semester number should <= 2')
    ])
    duration = models.IntegerField(null=False, blank=False, default=2, validators=[
        validators.MinValueValidator(1, 'Duration semesters should >= 1'),
        validators.MaxValueValidator(8, 'Max duration supported is 8')
    ])
    resources = models.CharField(max_length=500, blank=True)
    course = models.ForeignKey(Course, related_name='contract',
                               on_delete=models.PROTECT, blank=False, null=False)

    # Convener related fields
    convener = models.ForeignKey(SrpmsUser, related_name='convene', on_delete=models.PROTECT,
                                 blank=True, null=True)
    convener_approval_date = models.DateTimeField(null=True, blank=True)

    # Owner related fields
    owner = models.ForeignKey(SrpmsUser, related_name='own', on_delete=models.PROTECT,
                              blank=False, null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    submit_date = models.DateTimeField(null=True, blank=True)

    def is_submitted(self) -> bool:
        """Check if the contract is submitted"""
        return bool(self.convener_approval_date)

    def is_examiners_approved(self) -> bool:
        """Check if all examiners approved"""
        return all([a.examiner_approval_date for a in AssessmentMethod.objects.get(contract=self)])

    def is_supervisors_approved(self) -> bool:
        """Check if all supervisors approved"""
        return all([s.supervisor_approval_date for s in Supervise.objects.get(contract=self)])

    def is_convener_approved(self) -> bool:
        """No one should be allowed to change after convener approved"""
        return bool(self.convener_approval_date)

    def clean(self):
        """
        Apply model level constraints.

        Please note that this method would also be called when it's inheritance's `save`
        method is being called.
        """

        errors = {}

        # Update only check, self.pk would not present during create
        if self.pk:
            # Check if only one type of contract assigned
            iterator = iter([hasattr(self, 'individualproject'),
                             hasattr(self, 'specialtopics')])
            if any(iterator) and not any(iterator):
                pass
            else:
                errors['individualproject'] = 'A contract should have one and only one type'
                errors['specialtopics'] = 'A contract should have one and only one type'

        if not self.pk and self.submit_date:
            errors['is_submitted'] = 'You can\'t submit a contract on creation'
            errors['submit_date'] = 'You can\'t submit a contract on creation'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Contract, self).save(*args, **kwargs)

    def __str__(self):
        if hasattr(self, 'individualproject'):
            return str(self.individualproject)
        elif hasattr(self, 'specialtopics'):
            return str(self.specialtopics.title)
        else:
            super(Contract, self).__str__()


class Supervise(models.Model):
    supervisor = models.ForeignKey(SrpmsUser, related_name='supervise',
                                   on_delete=models.PROTECT, blank=False, null=False)
    is_formal = models.BooleanField(blank=False, null=False)
    supervisor_approval_date = models.DateTimeField(null=True, blank=True)
    contract = models.ForeignKey(Contract, related_name='supervisor',
                                 on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        unique_together = ('supervisor', 'contract')

    def is_convener_approved(self) -> bool:
        """No one should be allowed to change after convener approved"""
        return self.contract.is_convener_approved()

    def is_supervisor_approved(self) -> bool:
        """Whether this supervisor have approved this contract"""
        return bool(self.supervisor_approval_date)


class IndividualProject(Contract):
    title = models.CharField(max_length=100, default='Project title', null=False, blank=False)
    objectives = models.CharField(max_length=500, blank=True)
    description = models.CharField(max_length=1000, blank=True)

    def save(self, *args, **kwargs):
        # TODO: on submit, apply all constraints
        # TODO: on create, create associated assessments
        super(IndividualProject, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class SpecialTopics(Contract):
    title = models.CharField(max_length=100, default='Topic title', null=False, blank=False)
    objectives = models.CharField(max_length=500, blank=True)
    description = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return self.title


class AssessmentTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    description = models.CharField(max_length=200, blank=True)
    max_mark = models.IntegerField(null=False, blank=False)
    min_mark = models.IntegerField(null=False, blank=False)
    default_mark = models.IntegerField(null=True, blank=True)

    def clean(self):
        errors = {}

        if not self.min_mark <= self.max_mark <= 100:
            errors['max_mark'] = 'mark must within the range of min_mark to 100'
        if not 0 <= self.min_mark <= self.max_mark:
            errors['min_mark'] = 'mark must within the range of 0 to max_mark'
        if not self.min_mark <= self.default_mark <= self.max_mark:
            errors['default_mark'] = 'mark must within the range of min_mark to max_mark'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(AssessmentTemplate, self).save()

    def __str__(self):
        return self.name


class AssessmentMethod(models.Model):
    template = models.ForeignKey(AssessmentTemplate, related_name='assessment_method',
                                 on_delete=models.PROTECT, null=False, blank=False)
    contract = models.ForeignKey(Contract, related_name='assessment_method',
                                 on_delete=models.CASCADE, null=False, blank=False)
    additional_description = models.CharField(max_length=200, blank=True)
    due = models.DateField(null=True, blank=True)
    max_mark = models.IntegerField(null=False, blank=False)
    examiner = models.ForeignKey(SrpmsUser, related_name='examine',
                                 on_delete=models.PROTECT, null=True, blank=True)
    examiner_approval_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('contract', 'examiner')

    def is_supervisors_approved(self) -> bool:
        """No one should be allowed to change after supervisor approved"""
        return self.contract.is_supervisors_approved()

    def clean(self):
        """
        Apply constraint to the model

        TODO: remove the ambiguity of max_mark
        """

        errors = {}
        # Ensure each assessment item is within the valid rage specified by the template
        if self.max_mark > self.template.max_mark or self.max_mark < self.template.min_mark:
            errors['max_mark'] = 'Please keep the mark within the valid range'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        # Assign default marking weight based on template if not given
        if not self.max_mark:
            self.max_mark = self.template.default_mark

        super(AssessmentMethod, self).save(*args, **kwargs)


class AppPermission(models.Model):
    """A dummy model for holding permissions for this app"""

    class Meta:
        managed = False  # Do not create database table
