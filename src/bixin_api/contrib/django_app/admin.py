from django.contrib import admin

# Register your models here.


from . import models


admin.site.register(
    (
        models.BixinUser,
        models.Event,
        models.Deposit,
        models.Withdraw,
    )
)
