"""
This script is run each 10 s on production server by systemd timer:
cat pastvina/cron/main.py | ./manage.py shell --settings=...
Run it manully to make single tisk.
"""
from django.core.management import BaseCommand

from pastvina.models import Round, Tick


class Command(BaseCommand):
    help = """Removes the last tick. You can provide a [round_id] to take the tick from a specific round.
    If round_id is not provided, removes the last tick from any round (not necessarily the last round).
    """

    def add_arguments(self, parser):
        parser.add_argument('round_id', nargs='?', type=int, default=None, help='round id to remove the last tick from')

    def handle(self, *args, **options):
        if options['round_id'] is None:
            last_tick = Tick.objects.last()
        else:
            round_ = Round.objects.filter(id=options['round_id']).last()
            if round_ is None:
                self.stderr.write(self.style.ERROR('No round ' + str(options['round_id']) + ' found'))
                return
            last_tick = Tick.objects.filter(round=round_).last()

        if last_tick is None:
            if options['round_id'] is None:
                self.stderr.write(self.style.ERROR('No tick exists'))
            else:
                self.stderr.write(self.style.ERROR('No tick exists in round ' + str(options['round_id'])))
            return

        tick_index = last_tick.index
        round_id = last_tick.round.id
        last_tick.delete()
        self.stdout.write(self.style.SUCCESS('Tick with index ' + str(tick_index) + ' deleted from round ' + str(round_id)))
