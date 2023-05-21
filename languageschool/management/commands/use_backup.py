import ast
import csv

from django.core.management import BaseCommand

from languageschool.models import Game, Category, Article, Word, Meaning, Conjugation, Score, GameRound, Language, User


def replace_none_strings(row):
    columns = []
    for column in row:
        columns.append(None if column == "None" else column)
    return columns

def get_user_table():
    with open(f'C:/Users/Humberto/Desktop/Humberto/Study/WebDev/Pajelingo/backups/User.csv', mode='r') as f:
        rows = csv.reader(f)
        next(rows, None)

        for row in rows:
            columns = replace_none_strings(row)

            pk, username, email, is_active, is_staff, last_login, date_joined = columns
            user = User.objects.create(
                pk=pk,
                username=username,
                email=email,
                is_active=is_active,
                is_staff=is_staff,
                last_login=last_login,
                date_joined=date_joined
            )
            user.set_password("str0ng-p4ssw0rd")
            user.save()



class Command(BaseCommand):
    def handle(self, *args, **options):
        get_user_table()
