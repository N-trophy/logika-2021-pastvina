from django.core.management import BaseCommand, CommandError
from django.contrib.auth.models import User
from pastvina.models import Round, Tick, TeamHistory


class Command(BaseCommand):
    help = 'Adds money to user with given id.'

    def add_arguments(self, parser):
        parser.add_argument('usernames', nargs='+', type=str, help='List of users to add the money to.')
        parser.add_argument('-a', '--amount', type=int, help='Amount of money to add.')
        parser.add_argument('-r', '--round', nargs='?', type=int, default=None, help='Round id in which to add money.')

    def handle(self, *args, **options):
        if options['round'] is not None:
            try:
                round_ = Round.objects.get(id=options['round'])
            except Round.DoesNotExist:
                raise CommandError('Round "%s" does not exist.' % options['round'])
            tick = Tick.objects.filter(round=round_).order_by('index').last()
        else:
            tick = Tick.objects.last()

        if tick is None:
            raise CommandError("Could not find suitable tick.")

        if options['amount'] is None:
            raise CommandError("Amount not specified.")

        for username in options['usernames']:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError('User "%s" does not exist.' % username)

            user_stats, _ = TeamHistory.objects.get_or_create(user=user, tick=tick, defaults={'money': 0})

            user_stats.money += options['amount']
            user_stats.save()

            self.stdout.write(self.style.SUCCESS(f'Amount {options["amount"]} was added to {username} successfully'
                                                 f' (tick {tick}).'))
