import time

from django.core.management.base import BaseCommand
from bixin_api.contrib.django_app.synchronizers import (
    execute_withdraw,
    WithdrawExecutor
)


def main():
    t = WithdrawExecutor()
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
    help = 'sync deposit order for once'

    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            dest='once',
            help='only run once',
        )

    def handle(self, *args, **options):
        once = options.pop('once', False)
        if once:
            execute_withdraw()
            self.stdout.write(
                self.style.SUCCESS("succeed")
            )
        else:
            main()
