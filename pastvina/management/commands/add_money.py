from django.core.management import BaseCommand, CommandError
from pastvina.models import Round, Tick, TeamHistory


class Command(BaseCommand):
    help = 'Adds money to user with given id.'

    def add_arguments(self, parser):
        parser.add_argument('user_ids', nargs='+', type=int, help='List of users to add the money to.')
        parser.add_argument('--amount', type=int, help='Amount of money to add.')

    def handle(self, *args, **options):
        tick = Tick.objects.last()

        if 'amount' not in options:
            raise CommandError("Amount not specified.")

        for user_id in options['user_ids']:
            try:
                user_stats = TeamHistory.objects.get(user=user_id, tick=tick)
            except TeamHistory.DoesNotExist:
                raise CommandError('User "%s" does not exist' % user_id)

            user_stats.money += options['amount']
            user_stats.save()

            self.stdout.write(self.style.SUCCESS(f'Amount {options["amount"]} was added to {user_id} successfully'
                                                 f'(tick {tick}).'))
