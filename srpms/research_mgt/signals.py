"""
Define signals. Mainly for the purpose of sending notifications, but not limited to this.

Signal with @receiver decorator would be automatically registered on app initialization, which
currently happen inside apps.py

Please be careful when using send_mail() function, as recipient in the recipient_list would be
able to see each other's address.
"""

__author__ = "Dajie (Cooper) Yang"
__credits__ = ["Dajie Yang"]

__maintainer__ = "Dajie (Cooper) Yang"
__email__ = "dajie.yang@anu.edu.au"

import re
from io import StringIO
from typing import List
from accounts.models import SrpmsUser
from django.dispatch import receiver, Signal
from django.core import management
from django.core.mail import send_mail
from django.db.models.signals import post_migrate, post_save

from .models import (Contract, Supervise, AssessmentExamine, ActivityLog, ActivityAction)
from srpms.settings import EMAIL_SENDER

CONTRACT_SUBMIT = Signal(providing_args=['contract', 'activity_log'])
CONTRACT_APPROVE = Signal(providing_args=['contract', 'activity_log'])
SUPERVISE_APPROVE = Signal(providing_args=['supervise', 'activity_log'])
EXAMINER_APPROVE = Signal(providing_args=['assessment_examine', 'activity_log'])

# List of actions
ACTION_CONTRACT_SUBMIT = None
ACTION_CONTRACT_UN_SUBMIT = None
ACTION_CONTRACT_APPROVE = None
ACTION_CONTRACT_DISAPPROVE = None
ACTION_SUPERVISE_APPROVE = None
ACTION_SUPERVISE_DISAPPROVE = None
ACTION_EXAMINER_APPROVE = None
ACTION_EXAMINER_DISAPPROVE = None


# noinspection PyUnusedLocal
@receiver(post_save, sender=ActivityAction, dispatch_uid='post_save_init_actions')
@receiver(post_migrate, dispatch_uid='post_migrate_init_actions')
def init_actions(**kwargs):
    """
    Initiate activity actions after database migration completed, otherwise these actions
    won't exist in database.

    The 'get_or_create()' method is not recommend here as instance created here won't exist
    during test, and would cause errors during test.
    """
    global ACTION_CONTRACT_SUBMIT
    global ACTION_CONTRACT_UN_SUBMIT
    global ACTION_CONTRACT_APPROVE
    global ACTION_CONTRACT_DISAPPROVE
    global ACTION_SUPERVISE_APPROVE
    global ACTION_SUPERVISE_DISAPPROVE
    global ACTION_EXAMINER_APPROVE
    global ACTION_EXAMINER_DISAPPROVE

    s_io = None
    try:
        s_io = StringIO()
        management.call_command('showmigrations', stdout=s_io)

        # Only initialize actions when corresponding migration is finished
        if re.search(r'(?<=\[)X(?=\] 0005_actitivity_actions)', s_io.getvalue()):
            ACTION_CONTRACT_SUBMIT = ActivityAction.objects.get(name='contract_submit')
            ACTION_CONTRACT_UN_SUBMIT = ActivityAction.objects.get(name='contract_un_submit')
            ACTION_CONTRACT_APPROVE = ActivityAction.objects.get(name='contract_approve')
            ACTION_CONTRACT_DISAPPROVE = ActivityAction.objects.get(name='contract_disapprove')
            ACTION_SUPERVISE_APPROVE = ActivityAction.objects.get(name='supervise_approve')
            ACTION_SUPERVISE_DISAPPROVE = ActivityAction.objects.get(name='supervise_disapprove')
            ACTION_EXAMINER_APPROVE = ActivityAction.objects.get(name='examiner_approve')
            ACTION_EXAMINER_DISAPPROVE = ActivityAction.objects.get(name='examiner_disapprove')

    except Exception as exc:
        raise exc
    finally:
        s_io.close() if s_io else None


# TODO: HTML message for email notifications

def get_email_addr(users: List[SrpmsUser]) -> list:
    """
    Filter all available email addresses given a list of users.

    Note that some user might not have email address configured.
    """
    result = set()
    for user in users:
        if hasattr(user, 'email'):
            result.add(user.email)
    return list(result)


# noinspection PyUnusedLocal
@receiver(CONTRACT_SUBMIT, dispatch_uid='contract_submit')
def contract_submit_notifications(contract: Contract, activity_log: ActivityLog, **kwargs):
    """
    Send notifications when owner submit/un-submit contract.
    """

    # Submit
    if activity_log.action == ACTION_CONTRACT_SUBMIT:
        # Inform contract owner
        send_mail('We\'ve received your submitted contract',
                  'Your contract "{contract_title}" has been submitted '
                  'successfully to Student Research Project Management System.'
                  .format(contract_title=str(contract)),
                  EMAIL_SENDER,
                  get_email_addr([contract.owner]))
        # Inform contract supervisor
        for address in get_email_addr(contract.get_all_supervisors()):
            send_mail('New contract submission',
                      'Contract "{contract_title}" (created by {contract_owner}) invited you '
                      'as the contract\'s supervisor.'
                      .format(contract_title=str(contract),
                              contract_owner=contract.owner.get_display_name()),
                      EMAIL_SENDER,
                      [address])
    # Un-submit
    elif activity_log.action == ACTION_CONTRACT_UN_SUBMIT:
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
@receiver(CONTRACT_APPROVE, dispatch_uid='contract_approve')
def contract_approve_notifications(contract: Contract, activity_log: ActivityLog, **kwargs):
    """
    Send notifications on convener approve/disapprove a contract.
    """

    # Approve
    if activity_log.action == ACTION_CONTRACT_APPROVE:
        # Inform contract owner and all its supervisors
        for address in get_email_addr(list(contract.get_all_supervisors()) + [contract.owner]):
            send_mail('Contract approved by course convener',
                      'Contract "{contract_title}" has been approved by '
                      'course convener {convener_name}.'
                      .format(contract_title=str(contract),
                              convener_name=contract.convener.get_display_name()),
                      EMAIL_SENDER,
                      [address])
    # Disapprove
    elif activity_log.action == ACTION_CONTRACT_DISAPPROVE:
        # Inform supervisors. Contract owner is not being notified here, since the owner would
        # need to wait for supervisor's disapproval before editing the contract. Also, if it's
        # just a matter of changing examiner, the contract owner doesn't really need to be
        # involve.
        for address in get_email_addr(contract.get_all_supervisors()):
            send_mail('Contract disapproved by convener',
                      'Contract "{contract_title}" has been disapproved by convener {convener_name}'
                      '{disapprove_reason}'
                      .format(contract_title=str(contract),
                              convener_name=activity_log.actor.get_display_name(),
                              disapprove_reason='' if not activity_log.message else
                              ', with the following message "{message}"'
                              .format(message=activity_log.message)),
                      EMAIL_SENDER,
                      [address])


# noinspection PyUnusedLocal
@receiver(SUPERVISE_APPROVE, dispatch_uid='supervise_approve')
def supervise_approve_notifications(supervise: Supervise, activity_log: ActivityLog, **kwargs):
    """
    Send notifications on supervisor approve/disapprove a contract
    """

    # Approve
    if activity_log.action == ACTION_SUPERVISE_APPROVE:
        # Inform contract owner
        send_mail('Contract approved by supervisor',
                  'Your contract "{contract_title}" has been approved by '
                  'contract supervisor {supervisor_name}.'
                  .format(contract_title=str(supervise.contract),
                          supervisor_name=supervise.supervisor.get_display_name()),
                  EMAIL_SENDER,
                  get_email_addr([supervise.contract.owner]))
        # Inform examiners
        for address in get_email_addr(SrpmsUser.objects.filter(
                examine__nominator=supervise.supervisor,
                examine__contract=supervise.contract,
                examine__assessment_examine__examiner_approval_date__isnull=True)):
            send_mail('New contract assessment',
                      'Contract "{contract_title}"\'s supervisor {supervisor_name} invites you '
                      'as the examiner for its assessment.'
                      .format(contract_title=str(supervise.contract),
                              supervisor_name=supervise.supervisor.get_display_name()),
                      EMAIL_SENDER,
                      [address])
    # Disapprove
    elif activity_log.action == ACTION_SUPERVISE_DISAPPROVE:
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
@receiver(EXAMINER_APPROVE, dispatch_uid='examiner_approve')
def examiner_approve_notifications(assessment_examine: AssessmentExamine,
                                   activity_log: ActivityLog, **kwargs):
    """
    Send notification on examiner approve/disapprove an assessment
    """

    # Approve
    if activity_log.action == ACTION_EXAMINER_APPROVE:
        # Inform contract owner and examiner nominator
        for address in get_email_addr([assessment_examine.contract.owner,
                                       assessment_examine.examine.nominator]):
            send_mail('Contract assessment approved',
                      'Contract "{contract_title}"\'s assessment "{assessment_name}" has '
                      'been approved by examiner {examiner_name}.'
                      .format(contract_title=str(assessment_examine.contract),
                              assessment_name=assessment_examine.assessment.template.name,
                              examiner_name=assessment_examine.examine.examiner.get_display_name()),
                      EMAIL_SENDER,
                      [address])
    # Disapprove
    elif activity_log.action == ACTION_EXAMINER_DISAPPROVE:
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
@receiver(CONTRACT_APPROVE, dispatch_uid='contract_approve_pdf')
def contract_approve_generate_pdf(**kwargs):
    """
    TODO: Generate PDF version of agreement on contract final approval
    """
    pass
