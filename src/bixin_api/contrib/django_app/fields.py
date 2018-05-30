import json

from django.db import models


class BixinDecimalField(models.DecimalField):
    def __init__(self, **kw):
        kw.setdefault('max_digits', 65)
        kw.setdefault('decimal_places', 30)
        super(BixinDecimalField, self).__init__(**kw)


class JsonField(models.TextField):
    def __init__(self, **kw):
        kw.setdefault('default', json.dumps({}))
        super(JsonField, self).__init__(**kw)
