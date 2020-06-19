import csv
import os

from BefreeBingo.settings import BASE_DIR
from django.core.management import BaseCommand
from user.models import UserTraffic

class Command(BaseCommand):

    def handle(self, *args, **options):
        csv_target_path = os.path.join(BASE_DIR, 'media', 'user_traffic.csv')

        if os.path.exists(csv_target_path):
            with open(csv_target_path, 'r', newline='') as csv_file:
                reader = csv.reader(csv_file, delimiter='|', quotechar='"')

                counter = 0
                fields = {}

                for row in reader:
                    if counter == 0:
                        for i in range(0, len(row)):
                            fields[i] = row[i]
                    else:
                        context = {}
                        for i in range(0, len(row)):
                            context[fields[i]] = row[i] if row[i] not in ['False', 'True'] else row[i] == 'True'
                        UserTraffic.objects.create(**context)
                    counter += 1

                self.stdout.write(f'{counter} instances are created!', self.style.SUCCESS)
