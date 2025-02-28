from django.core.management.base import BaseCommand

import helpers.billing
from customers.models import Customer
from subscriptions import utils as subs_utils


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--clear-dangling", action="store_true", default=False)

    def handle(self, *args, **options):
        # python manage.py sync_user_subs --clear-dangling
        clear_dangling = options.get("clear_dangling")
        if clear_dangling:
            print("Clearing dangling active subs that are not in use")
            subs_utils.clear_dangling_subs()
        else:
            print("Sync active subs")
            

            
