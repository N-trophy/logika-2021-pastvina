"""
This script is run each 10 s on production server by systemd timer:
cat pastvina/cron/main.py | ./manage.py shell --settings=...
Run it manully to make single tisk.
"""
from django.core.management import BaseCommand

from pastvina.models import Round, Tick
from django.utils import timezone


def rounds_update() -> None:
    from .round import new as new_round

    for round_ in Round.objects.all():
        if round_.is_running() and not Tick.objects.filter(round=round_).exists():
            t = Tick(round=round_, index=0, start=timezone.now())
            t.save()

            new_round(round_, t)


def ticks_update() -> None:
    from pastvina.models import Round
    from .tick import new as new_tick

    for round_ in Round.objects.all():
        if round_.is_running():
            last_tick = Tick.objects.filter(round=round_).last()
            now = timezone.now()
            if (now - Tick.objects.filter(round=round_).last().start).total_seconds() + 1 >= 10 * round_.period:
                next_tick = Tick(round=round_, index=last_tick, start=now)
                next_tick.save()
                new_tick(last_tick, next_tick)


class Command(BaseCommand):
    help = 'Runs and iteration of updates.'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        rounds_update()
        ticks_update()
