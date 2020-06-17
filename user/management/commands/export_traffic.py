import csv
import os

from django.core.management.base import BaseCommand
from user.models import UserTraffic
from BefreeBingo.settings import BASE_DIR


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not os.path.exists(os.path.join(BASE_DIR, 'media')):
            os.mkdir(os.path.join(BASE_DIR, 'media'))

        with open(os.path.join(BASE_DIR, 'media', 'user_traffic.csv'), 'w', newline='') as csv_file:
            stream_writer = csv.writer(csv_file, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            fields = (
                'partner_id',
                'click_id',
                'site_id',
                'source',
                'ip',
                'created_at',
                'updated_at',
                'balance_filled'
            )

            stream_writer.writerow(fields)
            instances = UserTraffic.objects.values_list(*fields)

            for item in instances.all():
                stream_writer.writerow(item)

            self.stdout.write(f'{instances.count()} rows written!', self.style.SUCCESS)
