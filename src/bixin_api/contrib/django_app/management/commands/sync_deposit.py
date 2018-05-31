from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'sync deposit order for once'

    def handle(self, *args, **options):
        from bixin_api.contrib.django_app.synchronizers import sync_transfer_to_deposit
        sync_transfer_to_deposit()
        self.stdout.write(
            self.style.SUCCESS("succeed")
        )
