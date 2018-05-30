from django.conf import settings

from functools import wraps

from django.http import HttpResponseNotFound


def require_debug(view_fn):

    @wraps(view_fn)
    def wrapped(*args, **kwargs):
        if not settings.DEBUG:
            return HttpResponseNotFound()
        return view_fn(*args, **kwargs)

    return wrapped
