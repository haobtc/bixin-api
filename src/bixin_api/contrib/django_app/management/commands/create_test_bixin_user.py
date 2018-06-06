from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        from bixin_api.contrib.django_app.models import BixinUser

        BixinUser.objects.get_or_create(
            openid='1111111',
            defaults=dict(
                username="hi-iam-user",
                target_id='111111',
            )
        )
        user = get_user_model()
        user.objects.create_superuser(username='hallow', password="111111", email='a@b.com')
        self.stdout.write(
            self.style.SUCCESS("succeed")
        )
