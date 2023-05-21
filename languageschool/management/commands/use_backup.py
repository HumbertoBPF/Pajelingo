import ast
import csv

from django.core.management import BaseCommand

from languageschool.models import Game, Category, Article, Word, Meaning, Conjugation, Score, GameRound, Language, User

def fill_table(cls):
    with open(f'C:/Users/Humberto/Desktop/Humberto/Study/WebDev/Pajelingo/backups/{cls.__name__}.csv', mode='r') as f:
        rows = csv.reader(f)
        headers = next(rows, None)

        for row in rows:
            args = {}

            for i in range(len(row)):
                header = headers[i]
                column = row[i]
                args[header] = None if column == "None" else column

            cls.objects.create(**args)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # fill_user_table()
        # fill_table(Game)
        # fill_table(Language)
        fill_table(Category)
