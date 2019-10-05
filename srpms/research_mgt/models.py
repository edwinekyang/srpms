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
    resources = models.CharField(max_length=500, default='', blank=True)
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
        return bool(self.submit_date)

    def is_all_assessments_approved(self) -> bool:
        """Check if all assessments approved"""

        # A contract should have at least one assessment, otherwise it won't be approved
        if not self.assessment.all():
            return False

        # An assessment should have at least one examiner, otherwise it won't be approved
        if bool(Assessment.objects.filter(contract=self,
                                          assessment_examine__isnull=True)):
            return False

        return not bool(AssessmentExamine.objects.filter(contract=self,
                                                         examiner_approval_date__isnull=True))

    def is_all_supervisors_approved(self) -> bool:
        """Check if all supervisors approved"""

        # A contract should at least have one supervise relation
        if not self.supervise.all():
            return False

        # Check if any non-approval-date supervise relation exist
        return not bool(SrpmsUser.objects.filter(supervise__contract=self,
                                                 supervise__supervisor_approval_date__isnull=True))

    def is_convener_approved(self) -> bool:
        """No one should be allowed to change after convener approved"""
        return bool(self.convener_approval_date)

    def get_all_examiners(self):
        """
        Get all examiners of the contract. Note that there might be the case that an examiner
        of the contract does not belong to any assessment, in this case only examiners
        part of a assessment would be return.
        """
        return SrpmsUser.objects.filter(examine__assessment_examine__contract=self)

    def get_all_formal_supervisors(self):
        return SrpmsUser.objects.filter(supervise__contract=self, supervise__is_formal=True)

    def get_all_supervisors(self):
        return SrpmsUser.objects.filter(supervise__contract=self)

    def clean(self):
        """
        Apply model level constraints.

        Please note that this method would also be called when it's inheritance's `save`
        method is being called.
        """

        errors = {}

        if self.submit_date:
            # Make sure every contract have assessments sum to 100 on submit
            weights = list(Assessment.objects.filter(contract=self)
                           .values_list('weight', flat=True))
            if not sum(weights) == 100:
                errors['assessments'] = 'The sum of all assessments\' weight should be 100'

            # Make sure at least one supervisor is assign on submission
            if not len(Supervise.objects.filter(contract=self)) >= 1:
                errors['supervisor'] = 'A contract requires at least one supervisor'

        # Update only check, self.pk would not present during create
        if self.pk:
            pass  # Don't have anything to check at the moment

        # Check every condition satisfy on final approval
        if self.convener_approval_date:
            if not self.is_submitted():
                errors['is_submitted'] = 'Un-submitted contract cannot be approved'
            if not self.is_all_assessments_approved():
                errors['is_all_assessments_approved'] = 'All assessments must be approved ' \
                                                        'before final approval'
            if not self.is_all_supervisors_approved():
                errors['is_all_supervisors_approved'] = 'All supervisors must approve this ' \
                                                        'contract before final approval'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        # Final approval passed, clean up examiners that does not examine anything on this contract
        if self.convener_approval_date:
            Examine.objects.filter(contract=self, assessment_examine__isnull=True).delete()

        return super(Contract, self).save(*args, **kwargs)

    def __str__(self):
        if hasattr(self, 'individual_project'):
            return str(self.individual_project)
        elif hasattr(self, 'special_topic'):
            return str(self.special_topic)
        else:
            return super(Contract, self).__str__()


class IndividualProject(Contract):
    # Explicitly define OneToOne inheritance link, the default's on_delete policy is NOT CASCADE
    contract = models.OneToOneField(Contract, on_delete=models.CASCADE, parent_link=True,
                                    related_name='individual_project')

    title = models.CharField(max_length=100, default='Project title', null=False, blank=False)
    objectives = models.CharField(max_length=500, default='', blank=True)
    description = models.CharField(max_length=1000, default='', blank=True)

    def save(self, *args, **kwargs):
        # TODO: on submit, apply all constraints
        return super(IndividualProject, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class SpecialTopic(Contract):
    # Explicitly define OneToOne inheritance link, the default's on_delete policy is NOT CASCADE
    contract = models.OneToOneField(Contract, on_delete=models.CASCADE, parent_link=True,
                                    related_name='special_topic')

    title = models.CharField(max_length=100, default='Topic title', null=False, blank=False)
    objectives = models.CharField(max_length=500, default='', blank=True)
    description = models.CharField(max_length=1000, default='', blank=True)

    def save(self, *args, **kwargs):
        # TODO: on submit, apply all constraints
        return super(SpecialTopic, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Supervise(models.Model):
    supervisor = models.ForeignKey(SrpmsUser, related_name='supervise',
                                   on_delete=models.PROTECT, blank=False, null=False)
    is_formal = models.BooleanField(blank=False, null=False)
    supervisor_approval_date = models.DateTimeField(null=True, blank=True)
    contract = models.ForeignKey(Contract, related_name='supervise',
                                 on_delete=models.CASCADE, blank=False, null=False)

    nominator = models.ForeignKey(SrpmsUser, related_name='supervisor_nominate',
                                  on_delete=models.PROTECT)

    class Meta:
        unique_together = ('supervisor', 'contract')

    def is_convener_approved(self) -> bool:
        """No one should be allowed to change after convener approved"""
        return self.contract.is_convener_approved()

    def is_supervisor_approved(self) -> bool:
        """Whether this supervisor have approved this contract"""
        return bool(self.supervisor_approval_date)

    def clean(self) -> None:
        errors = {}

        # Approval check
        if self.supervisor_approval_date:
            # The contract need to be submitted before approval
            if not self.contract.is_submitted():
                errors['contract'] = 'Un-submitted contract is not allowed to be approved.'

            for assessment in self.contract.assessment.all():
                if len(assessment.assessment_examine.all()) < 1:
                    errors['assessments'] = 'Please make sure you\'ve assigned at least one ' \
                                            'examiner for each assessment.'
                    break

        if self.contract.convener_approval_date:
            errors['convener_approve'] = 'convener approved contract is not allowed to modify.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Supervise, self).save(*args, **kwargs)


class AssessmentTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    description = models.CharField(max_length=200, default='', blank=True)
    max_weight = models.IntegerField(null=False, blank=False)
    min_weight = models.IntegerField(null=False, blank=False)
    default_weight = models.IntegerField(null=True, blank=True)

    def clean(self):
        errors = {}

        if not self.min_weight <= self.max_weight <= 100:
            errors['max_weight'] = 'weight must within the range of min_weight to 100'
        if not 0 <= self.min_weight <= self.max_weight:
            errors['min_weight'] = 'weight must within the range of 0 to max_weight'
        if not self.min_weight <= self.default_weight <= self.max_weight:
            errors['default_weight'] = 'weight must within the range of min_weight to max_weight'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(AssessmentTemplate, self).save()

    def __str__(self):
        return self.name


class Assessment(models.Model):
    template = models.ForeignKey(AssessmentTemplate, related_name='assessment',
                                 on_delete=models.PROTECT, null=False, blank=False)
    contract = models.ForeignKey(Contract, related_name='assessment',
                                 on_delete=models.CASCADE, null=False, blank=False)
    additional_description = models.CharField(max_length=200, default='', blank=True)
    due = models.DateField(null=True, blank=True)
    weight = models.IntegerField(null=False, blank=True)

    def is_convener_approved(self) -> bool:
        """No one should be allowed to change after convener approved"""
        return self.contract.is_convener_approved()

    def is_all_supervisors_approved(self) -> bool:
        """No one should be allowed to change after all supervisors approved"""
        return self.contract.is_all_supervisors_approved()

    def is_all_examiners_approved(self) -> bool:
        """
        Check if this assessment has been approved by all its examiners, one assessment
        should at least have one examiner.
        """
        if not self.assessment_examine.all():
            return False
        return not bool(AssessmentExamine.objects.filter(assessment=self,
                                                         examiner_approval_date__isnull=True))

    def get_all_examiners(self):
        return SrpmsUser.objects.filter(examine__assessment_examine__assessment=self)

    def clean(self):
        """Apply constraint to the model"""

        errors = {}

        if self.weight:
            # Ensure each assessment item is within the valid rage specified by the template
            if self.weight > self.template.max_weight or self.weight < self.template.min_weight:
                errors['weight'] = 'Please keep the weight within the valid range given by template'
        if self.contract.convener_approval_date:
            errors['convener_approve'] = 'convener approved contract is not allowed to modify.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        # Assign default marking weight based on template if not given
        if not self.weight:
            self.weight = self.template.default_weight

        return super(Assessment, self).save(*args, **kwargs)


class Examine(models.Model):
    contract = models.ForeignKey(Contract, related_name='examine', on_delete=models.CASCADE)
    examiner = models.ForeignKey(SrpmsUser, related_name='examine', on_delete=models.PROTECT)
    nominator = models.ForeignKey(SrpmsUser, related_name='examiner_nominate',
                                  on_delete=models.PROTECT)

    class Meta:
        unique_together = ('contract', 'examiner')

    def clean(self):
        errors = {}
        if self.contract.convener_approval_date:
            errors['convener_approve'] = 'convener approved contract is not allowed to modify.'
        if errors:
            raise ValidationError(errors)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.full_clean()
        super(Examine, self).save()


class AssessmentExamine(models.Model):
    """
    Store the assessment-examine relation, this is to allow multiple examiner for the same
    assessment method.

    The original EER diagram was a many-to-many relation with one side being a weak entity:

    [SrpmsUser] -- n -- <examine> -- m -- [[assessment]] -- m -- [Contract]
    [[assessment]] -- m -- <assess> -- 1 -- [contract]


    However this is not possible to implement in Django ORM, since it does not support weak
    entity, as such it must be decomposed to a diamond shape relation:

    [contract] -- 1 -- <examine by> -- n -- [examine] -- 1 -- <examine>
                                                                   |
                                                                   p
                                                                   |
                                                         [assessment examine]
                                                                   |
                                                                   q
                                                                   |
    [contract] -- 1 -- <assess by> -- m -- [assessment] -- 1 -- <examine by>
    """

    # This field exists sorely for convenient indexing, and would be overwrite to assessment's
    # contract on save.
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='assessment_examine')

    assessment = models.ForeignKey(Assessment, related_name='assessment_examine',
                                   on_delete=models.CASCADE)
    examine = models.ForeignKey(Examine, related_name='assessment_examine',
                                on_delete=models.CASCADE)
    examiner_approval_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('assessment', 'examine')

    def clean(self):
        errors = {}

        if self.contract and self.contract.convener_approval_date:
            errors['convener_approve'] = 'convener approved contract is not allowed to modify.'

        if self.assessment.contract != self.examine.contract:
            errors['assessment'] = 'assessment\'s contract is different from examine\'s contract'
            errors['examine'] = 'examine\'s contract is different from assessment\'s contract'

        if self.examiner_approval_date and not self.contract.is_all_supervisors_approved():
            errors['supervise'] = 'Examiner approval is not allowed before supervisor approve'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        self.contract = self.assessment.contract
        return super(AssessmentExamine, self).save(*args, **kwargs)


class AppPermission(models.Model):
    """A dummy model for holding permissions for this app"""

    class Meta:
        managed = False  # Do not create database table
