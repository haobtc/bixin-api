import logging
import time
from threading import Thread

from django.core.management.base import BaseCommand
from bixin_api.contrib.django_app.synchronizers import sync_transfer_to_deposit


class StoppableThread(Thread):
    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stopped = False
        self.setDaemon(True)

    def stop(self):
        self._stopped = True


class TransferSync(StoppableThread):

    def run(self):
        while not self._stopped:
            time.sleep(0.05)
            try:
                sync_transfer_to_deposit()
            except Exception:
                logging.exception(
                    "Failed to sync deposit orders:"
                )


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

