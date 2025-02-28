from django.core.management.base import BaseCommand

import helpers.billing
from customers.models import Customer
from subscriptions import utils as subs_utils


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--day-start", default=0, type=int)
        parser.add_argument("--day-end", default=0, type=int)
        parser.add_argument("--days-left", default=0, type=int)
        parser.add_argument("--days-ago", default=0, type=int)
        parser.add_argument("--clear-dangling", action="store_true", default=False)

    def handle(self, *args, **options):
        # python manage.py sync_user_subs --clear-dangling
        day_start = options.get("day_start")
        day_end = options.get("day_end")
        days_left = options.get("days_left")
        days_ago = options.get("days_ago")
        clear_dangling = options.get("clear_dangling")

        if clear_dangling:
            print("Clearing dangling active subs that are not in use")
            subs_utils.clear_dangling_subs()
        else:
            print("Sync active subs")
            done = subs_utils.refresh_active_users_subscriptions(
                active_only=True,
                verbose=True,
                day_start=day_start,
                day_end=day_end,
                days_ago=days_ago,
                days_left=days_left,
            )
            if done:
                print("Done")
            

            
