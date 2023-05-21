import ast
import csv

from django.core.management import BaseCommand

from languageschool.models import Game, Category, Article, Word, Meaning, Conjugation, Score, GameRound, Language, User


def get_user_table():
    with open(f'C:/Users/Humberto/Desktop/Humberto/Study/WebDev/Pajelingo/backups/User.csv', mode='r') as f:
        rows = csv.reader(f)
        next(rows, None)

        for row in rows:
            User.objects.create()


class Command(BaseCommand):
    def handle(self, *args, **options):
        pass
