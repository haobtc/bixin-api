from django.core.management.base import BaseCommand


def create_bixin_user():
    from bixin_api.contrib.django_app.models import BixinUser

    user, created = BixinUser.objects.get_or_create(
        openid='openid_example',
        defaults=dict(
            username="hi-iam-user",
            target_id='111111',
        )
    )
    return user

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        create_bixin_user()
        self.stdout.write(
            self.style.SUCCESS("succeed")
        )
