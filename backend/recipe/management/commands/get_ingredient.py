import csv

from django.core.management.base import BaseCommand

from recipe.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка всех ингредиентов в базу из ingredients.csv.'

    def handle(self, *args, **kwargs):
        file_path = '../data/ingredients.csv'
        ingredients_to_create = []
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                ingredient_name = row[0].strip()
                measurement_unit = row[1].strip()
                ingredients_to_create.append(Ingredient(
                    name=ingredient_name,
                    measurement_unit=measurement_unit
                ))

        Ingredient.objects.bulk_create(ingredients_to_create,
                                       ignore_conflicts=True)
        self.stdout.write('Ингредиенты добавлены в базу.')
