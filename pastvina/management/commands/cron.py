"""
This script is run each 10 s on production server by systemd timer:
cat pastvina/cron/main.py | ./manage.py shell --settings=...
Run it manully to make single tisk.
"""
from django.core.management import BaseCommand
from django.db import transaction

from pastvina.models import Round, Tick
from django.utils import timezone


def rounds_update() -> None:
    from ._round import new as new_round

    current_time = timezone.now()
    for round_ in Round.objects.all():
        if round_.is_running() and not Tick.objects.filter(round=round_).exists():
            t = Tick(round=round_, index=0, start=current_time)
            t.save()

            new_round(round_, t)


def ticks_update() -> None:
    from pastvina.models import Round
    from ._tick import new as new_tick

    current_time = timezone.now()
    for round_ in Round.objects.all():
        if not round_.is_running():
            continue
        last_tick = Tick.objects.filter(round=round_).last()
        if last_tick is None:
            continue
        delta = (current_time - last_tick.start).total_seconds()
        if delta < 10 * round_.period:
            continue
        next_tick = Tick(round=round_, index=last_tick.index + 1, start=current_time)
        next_tick.save()
        print(f'created {next_tick} in round {round_}')
        new_tick(last_tick, next_tick)


class Command(BaseCommand):
    help = 'Runs one iteration of updates.'

    @transaction.atomic
    def handle(self, *args, **options):
        rounds_update()
        ticks_update()
