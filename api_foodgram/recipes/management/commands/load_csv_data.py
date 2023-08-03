import csv

from django.conf import settings
from django.core.management import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_file = 'ingredients.csv'
        filepath = f'{settings.BASE_DIR}/data/{csv_file}'
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, fieldnames=['name', 'measurement_unit'])
            imported = 0
            for row in reader:
                try:
                    Ingredient.objects.create(
                        name=row['name'],
                        measurement_unit=row['measurement_unit']
                    )
                    imported += 1
                except IntegrityError as e:
                    self.stderr.write(
                        self.style.ERROR(
                            f'Не удалось импортировать файл: {e}'
                        )
                    )
            self.stdout.write(self.style.SUCCESS(
                f'{imported} ингредиентов успешно импортированы.'
            ))
