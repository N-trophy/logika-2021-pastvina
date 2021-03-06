"""
This script is run each 10 s on production server by systemd timer:
cat pastvina/cron/main.py | ./manage.py shell --settings=...
Run it manully to make single tisk.
"""


def rounds_update() -> None:
    from pastvina.cron.round import new as new_round

    # TODO: check if new round should be started, call round.new
    # Call when round is started according to time, but no tick is in database
    # This function creates new tick.

    pass


def ticks_update() -> None:
    from pastvina.models import Round

    from pastvina.cron.tick import new as new_tick

    # TODO: not working
    # Calculate ticck according to time of round, if tick does not exist in
    # db, create it and call new_tick.
    # Db maybe should be locked between request and new tick creation.
    # This function creates new tick.
    for round_ in Round.objects.all():
        if round_.is_running():
            new_round(round_, round_.tick())


if __name__ in ['__main__', 'django.core.management.commands.shell']:
    rounds_update()
    ticks_update()
