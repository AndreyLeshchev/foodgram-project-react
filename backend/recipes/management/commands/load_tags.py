import csv

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Загрузка тэгов в базу данных.'

    def handle(self, *args, **options):
        with open(
            'data/tags.csv', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            for row in reader:
                Tag.objects.get_or_create(
                    name=row[0], color=row[1], slug=row[2]
                )
            self.stdout.write(
                self.style.SUCCESS('Загрузка тэгов выполнена.')
            )
