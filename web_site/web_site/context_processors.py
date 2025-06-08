from django.conf import settings
import re


def path_without_prefix(request):
    path = request.get_full_path()
    m = re.match(r"^{}(.*)$".format(settings.URL_PREFIX), path)
    if m:
        path = m.group(1)
    return {'PATH_WITHOUT_PREFIX': path}
