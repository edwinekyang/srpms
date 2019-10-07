from typing import List
from accounts.models import SrpmsUser
from django.dispatch import receiver, Signal
from django.core.mail import send_mail
from django.db.models.signals import post_migrate

from .models import (Contract, Supervise, AssessmentExamine, ActivityLog, ActivityAction)
from srpms.settings import EMAIL_SENDER

contract_submit = Signal(providing_args=['contract', 'activity_log'])
contract_approve = Signal(providing_args=['contract', 'activity_log'])
supervise_approve = Signal(providing_args=['supervise', 'activity_log'])
examiner_approve = Signal(providing_args=['assessment_examine', 'activity_log'])

# List of actions
action_contract_submit = None
action_contract_un_submit = None
action_contract_approve = None
action_contract_disapprove = None
action_supervise_approve = None
action_supervise_disapprove = None
action_examiner_approve = None
action_examiner_disapprove = None


# noinspection PyUnusedLocal
@receiver(post_migrate, dispatch_uid='init_actions')
def init_actions(**kwargs):
    """
    Initiate activity actions after database migration completed, otherwise these actions
    won't exist in database.

    The 'get_or_create()' method is not recommend here as instance created here won't exist
    during test, and would cause errors during test.
    """
    global action_contract_submit
    global action_contract_un_submit
    global action_contract_approve
    global action_contract_disapprove
    global action_supervise_approve
    global action_supervise_disapprove
    global action_examiner_approve
    global action_examiner_disapprove

    action_contract_submit = ActivityAction.objects.get(name='contract_submit')
    action_contract_un_submit = ActivityAction.objects.get(name='contract_un_submit')
    action_contract_approve = ActivityAction.objects.get(name='contract_approve')
    action_contract_disapprove = ActivityAction.objects.get(name='contract_disapprove')
    action_supervise_approve = ActivityAction.objects.get(name='supervise_approve')
    action_supervise_disapprove = ActivityAction.objects.get(name='supervise_disapprove')
    action_examiner_approve = ActivityAction.objects.get(name='examiner_approve')
    action_examiner_disapprove = ActivityAction.objects.get(name='examiner_disapprove')


# TODO: HTML message for email notifications

def get_email_addr(users: List[SrpmsUser]) -> set:
    """
    Filter all available email addresses given a list of users.

    Note that some user might not have email address configured.
    """
    result = set()
    for user in users:
        if hasattr(user, 'email'):
            result.add(user.email)
    return result


# noinspection PyUnusedLocal
@receiver(contract_submit, dispatch_uid='contract_submit')
def contract_submit_notifications(contract: Contract, activity_log: ActivityLog, **kwargs):
    """
    Send notifications when owner submit/un-submit contract.
    """

    # Submit
    if activity_log.action == action_contract_submit:
        # Inform contract owner
        send_mail('We\'ve received your submitted contract',
                  'Your contract "{contract_title}" has been submitted '
                  'successfully to Student Research Project Management System.'
                  .format(contract_title=str(contract)),
                  EMAIL_SENDER,
                  get_email_addr([contract.owner]))
        # Inform contract supervisor
        send_mail('New contract submission',
                  'Contract "{contract_title}" (created by {contract_owner}) invited you '
                  'as the contract\'s supervisor.'
                  .format(contract_title=str(contract),
                          contract_owner=contract.owner.get_display_name()),
                  EMAIL_SENDER,
                  get_email_addr(contract.get_all_supervisors()))
    # Un-submit
    elif activity_log.action == action_contract_un_submit:
        # Inform contract owner if the actor is not contract owner, note that contract
        # owner normally don't have the privilege to un-submit their own contract.
        if activity_log.actor != contract.owner:
            send_mail('Contract status has been set to un-submit',
                      'Your contract "{contract_title}"\'s submit status has been '
                      'changed to un-submit.'
                      .format(contract_title=str(contract)),
                      EMAIL_SENDER,
                      get_email_addr([contract.owner]))


# noinspection PyUnusedLocal
@receiver(contract_approve, dispatch_uid='contract_approve')
def contract_approve_notifications(contract: Contract, activity_log: ActivityLog, **kwargs):
    """
    Send notifications on convener approve/disapprove a contract.
    """

    # Approve
    if activity_log.action == action_contract_approve:
        # Inform contract owner and all its supervisors
        send_mail('Your contract has been approved by course convener',
                  'Your contract "{contract_title}" has been approved by '
                  'course convener {convener_name}.'
                  .format(contract_title=str(contract),
                          convener_name=contract.convener.get_display_name()),
                  EMAIL_SENDER,
                  get_email_addr(list(contract.get_all_supervisors()) + [contract.owner]))
    # Disapprove
    elif activity_log.action == action_contract_disapprove:
        # Inform supervisors. Contract owner is not being notified here, since the owner would
        # need to wait for supervisor's disapproval before editing the contract. Also, if it's
        # just a matter of changing examiner, the contract owner doesn't really need to be
        # involve.
        send_mail('Contract disapproved by convener',
                  'Contract "{contract_title}" has been disapproved by convener {convener_name}'
                  '{disapprove_reason}'
                  .format(contract_title=str(contract),
                          convener_name=activity_log.actor.get_display_name(),
                          disapprove_reason='' if not activity_log.message else
                          ', with the following message "{message}"'
                          .format(message=activity_log.message)),
                  EMAIL_SENDER,
                  get_email_addr(contract.get_all_supervisors()))


# noinspection PyUnusedLocal
@receiver(supervise_approve, dispatch_uid='supervise_approve')
def supervise_approve_notifications(supervise: Supervise, activity_log: ActivityLog, **kwargs):
    """
    Send notifications on supervisor approve/disapprove a contract
    """

    # Approve
    if activity_log.action == action_supervise_approve:
        # Inform contract owner
        send_mail('Your contract has been approved by supervisor',
                  'Your contract "{contract_title}" has been approved by '
                  'contract supervisor {supervisor_name}.'
                  .format(contract_title=str(supervise.contract),
                          supervisor_name=supervise.supervisor.get_display_name()),
                  EMAIL_SENDER,
                  get_email_addr([supervise.contract.owner]))
        # Inform examiners
        send_mail('New contract assessment',
                  'Contract "{contract_title}" invites you as the examiner for its assessment.'
                  .format(contract_title=str(supervise.contract)),
                  EMAIL_SENDER,
                  get_email_addr(supervise.contract.get_all_examiners()))
    # Disapprove
    elif activity_log.action == action_supervise_disapprove:
        # Inform contract owner
        send_mail('Contract disapproved by supervisor',
                  'Contract "{contract_title}" has been disapproved by '
                  'contract supervisor {supervisor_name}'
                  '{disapprove_reason}'
                  .format(contract_title=str(supervise.contract),
                          supervisor_name=supervise.supervisor.get_display_name(),
                          disapprove_reason='' if not activity_log.message else
                          ', with the following message "{message}"'
                          .format(message=activity_log.message)),
                  EMAIL_SENDER,
                  get_email_addr([supervise.contract.owner]))
        # TODO: ? Inform examiners that already approved, as their approval would be cleared


# noinspection PyUnusedLocal
@receiver(examiner_approve, dispatch_uid='examiner_approve')
def examiner_approve_notifications(assessment_examine: AssessmentExamine,
                                   activity_log: ActivityLog, **kwargs):
    """
    Send notification on examiner approve/disapprove an assessment
    """

    # Approve
    if activity_log.action == action_examiner_approve:
        # Inform contract owner and examiner nominator
        send_mail('Contract assessment approved',
                  'Contract "{contract_title}"\'s assessment "{assessment_name}" has '
                  'been approved by examiner {examiner_name}.'
                  .format(contract_title=str(assessment_examine.contract),
                          assessment_name=assessment_examine.assessment.template.name,
                          examiner_name=assessment_examine.examine.examiner.get_display_name()),
                  EMAIL_SENDER,
                  get_email_addr([assessment_examine.contract.owner,
                                  assessment_examine.examine.nominator]))
    # Disapprove
    elif activity_log.action == action_examiner_disapprove:
        send_mail('Contract assessment disapproved by examiner',
                  'Contract "{contract_title}"\'s assessment "{assessment_name}" '
                  'disapproved by examiner {examiner_name}'
                  '{disapprove_reason}'
                  .format(contract_title=str(assessment_examine.contract),
                          assessment_name=assessment_examine.assessment.template.name,
                          examiner_name=assessment_examine.examine.examiner.get_display_name(),
                          disapprove_reason='' if not activity_log.message else
                          ', because "{message}"'.format(message=activity_log.message)),
                  EMAIL_SENDER,
                  get_email_addr([assessment_examine.examine.nominator]))
        # TODO: ? Inform contract owner


# noinspection PyUnusedLocal
@receiver(contract_approve, dispatch_uid='contract_approve_pdf')
def contract_approve_generate_pdf(**kwargs):
    """
    TODO: Generate PDF version of agreement on contract final approval
    """
    pass
