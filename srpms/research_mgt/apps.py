from django.apps import AppConfig
from django.db.models.signals import post_save


class ResearchMgtConfig(AppConfig):
    name = 'research_mgt'

    def ready(self) -> None:
        super(ResearchMgtConfig, self).ready()

        # Connect signals after app is ready, we do the import here so that every function
        # in signals.py that decorated with @receiver would all be registered automatically.

        # noinspection PyUnresolvedReferences
        from . import signals
