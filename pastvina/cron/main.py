"""
This script is run each 10 s on production server by systemd timer:
cat pastvina/cron/main.py | ./manage.py shell --settings=...
Run it manully to make single tisk.
"""


def rounds_update() -> None:
    from pastvina.models import Round
    from pastvina.cron.round import new as new_round
    from pastvina.cron.tick import new as new_tick

    # TODO: not working
    for round_ in Round.objects.all():
        if round_.is_running():
            new_round(round_, round_.tick())


if __name__ in ['__main__', 'django.core.management.commands.shell']:
    rounds_update()
