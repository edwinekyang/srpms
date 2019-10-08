"""
Test signals, i.e. notification emails are sent correctly.
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from django.core import mail

from .test_api_integration_special_topic import SpecialTopic


class SignalTest(SpecialTopic):
    def test_notifications(self):
        self.set_supervise()
        self.set_assessment()
        self.set_submit()

        # 3 emails, one for contract owner, 2 for supervisors
        self.assertEqual(len(mail.outbox), 3)

        self.set_examine()
        self.set_supervise_approve()

        # 3 more emails, 2 for contract owner (for each supervisor's approval), 2 for examiners
        self.assertEqual(len(mail.outbox), 7)

        self.set_examiner_approve()

        # 4 more emails, 2 for contract owner (for each examiner's approval), 2 for
        # examiner nominators
        self.assertEqual(len(mail.outbox), 11)

        self.set_convener_approve()

        # 3 more emails, one for contract owner, 2 for supervisors
        self.assertEqual(len(mail.outbox), 14)
