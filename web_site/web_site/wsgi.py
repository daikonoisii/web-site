"""
WSGI config for web_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append('/var/lib/web_site')
os.environ.setdefault("PYTHON_EGG_CACHE", "/var/lib/web_site/egg_cache")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_site.settings')

application = get_wsgi_application()
