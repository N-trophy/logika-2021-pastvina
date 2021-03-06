from pastvina.models import Contribution, Crop, Livestock

"""
This script is run each 10 s on production server by systemd timer:
cat pastvina/cron.py | ./manage.py shell --settings=...
Run it manully to make single tisk.
"""


def main():
    print('Hello!')


if __name__ in ['__main__', 'django.core.management.commands.shell']:
    main()
