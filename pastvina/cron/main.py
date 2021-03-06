"""
This script is run each 10 s on production server by systemd timer:
cat pastvina/cron/main.py | ./manage.py shell --settings=...
Run it manully to make single tisk.
"""
from pastvina.models import Round, Tick
from django.utils import timezone


def rounds_update() -> list(Tick):
    from pastvina.cron.round import new as new_round

    created_ticks = []

    for round_ in Round.objects.all():
        if round_.is_running() and not Tick.objects.filter(round=round_).exists():
            t = Tick(round=round_, index=0, start=timezone.now())
            t.save()
            created_ticks.append(t)

            new_round(round_, t)


def ticks_update() -> None:
    from pastvina.models import Round
    from pastvina.cron.tick import new as new_tick

    for round_ in Round.objects.all():
        if round_.is_running():
            last_tick = Tick.objects.filter(round=round_).last()
            now = timezone.now()
            if now.total_seconds() + 1 >= Tick.objects.filter(round=round_).last().start.total_seconds() + 10 * round_.period:
                next_tick = Tick(round=round_, index=last_tick, start=now)
                next_tick.save()
                new_tick(last_tick, next_tick)


if __name__ in ['__main__', 'django.core.management.commands.shell']:
    rounds_update()
    ticks_update()
