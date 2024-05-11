import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в базу данных.'

    def handle(self, *args, **options):
        with open(
            'data/ingredients.csv', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0], measurement_unit=row[1]
                )
            self.stdout.write(
                self.style.SUCCESS('Загрузка ингредиентов выполнена.')
            )
