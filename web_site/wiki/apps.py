from django.apps import AppConfig
from wiki.core.plugins.loader import load_wiki_plugins


class WikiConfig(AppConfig):
    name = 'wiki'

    def ready(self):
        load_wiki_plugins()



