import ast
import csv

import pytest
from django.core.management import call_command

from languageschool.models import Score, Conjugation, Meaning, Article, Category, Language, Game, Word, AppUser
from languageschool.tests.utils import get_users_from_accounts


def assert_backup_file(cls, many_to_many=None):
    if many_to_many is None:
        many_to_many = []

    with open(f'C:/Users/Humberto/Desktop/Humberto/Study/WebDev/Pajelingo/backups/{cls.__name__}.csv', mode='r') as f:
        rows = csv.reader(f)
        headers = next(rows, None)

        for row in rows:
            args = {}

            for i in range(len(row)):
                if headers[i] in many_to_many:
                    many_to_many_field = ast.literal_eval(row[i])
                    if len(many_to_many_field) == 0:
                        args[headers[i]] = None
                    else:
                        args[headers[i]+"__in"] = many_to_many_field
                else:
                    args[headers[i]] = None if (row[i] == "None") else row[i]

            assert cls.objects.filter(**args).exists()


@pytest.mark.django_db
def test_create_backup(games, languages, categories, articles, words, meanings, conjugations, score, account):
    accounts = account(n=10)
    users = get_users_from_accounts(accounts)
    score(users, languages)
    call_command("create_backup")

    assert_backup_file(Game)
    assert_backup_file(Language)
    assert_backup_file(Category)
    assert_backup_file(Article)
    assert_backup_file(Word, many_to_many=["synonyms"])
    assert_backup_file(Meaning)
    assert_backup_file(Conjugation)
    assert_backup_file(Score)
    assert_backup_file(AppUser, many_to_many=["favorite_words"])