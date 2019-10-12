"""
Initialize the research_mgt app, and is being configure to initialize signals after app is ready.
"""

__author__ = 'Dajie (Cooper) Yang'
__credits__ = ['Dajie Yang']

__maintainer__ = 'Dajie (Cooper) Yang'
__email__ = 'dajie.yang@anu.edu.au'

from django.apps import AppConfig


class ResearchMgtConfig(AppConfig):
    name = 'research_mgt'

    def ready(self) -> None:
        super(ResearchMgtConfig, self).ready()

        # Connect signals after app is ready, we do the import here so that every function
        # in signals.py that decorated with @receiver would all be registered automatically.

        # noinspection PyUnresolvedReferences
        from . import signals
        signals.init_actions()
