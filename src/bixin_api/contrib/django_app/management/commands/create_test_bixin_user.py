from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        from bixin_api.contrib.django_app.models import BixinUser
        BixinUser.objects.create(
            id=125103,
            username="hi-iam-user",
            target_id='111111',
            openid='1111111'
        )
        self.stdout.write(
            self.style.SUCCESS("succeed")
        )
