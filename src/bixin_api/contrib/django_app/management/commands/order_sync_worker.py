import time

from bixin_api.contrib.django_app.synchronizers import TransferSync
from django.core.management.base import BaseCommand


def main():
    t = TransferSync()
    t.start()
    print("Start syncing...")
    while True:
        try:
            time.sleep(2)
        except KeyboardInterrupt:
            print("Exiting...please wait and don't press CRTL+C")
            t.stop()
            t.join()
            exit(0)


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        main()



