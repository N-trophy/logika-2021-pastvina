"""
This script is run each 10 s on production server by systemd timer:
cat pastvina/cron/main.py | ./manage.py shell --settings=...
Run it manully to make single tisk.
"""
from django.core.management import BaseCommand

from pastvina.models import Tick


class Command(BaseCommand):
    help = 'Runs and iteration of updates.'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        last = Tick.objects.last()
        if last:
            last.delete()
            print("Last tick deleted.")
        else:
            print("No tick exists.")
