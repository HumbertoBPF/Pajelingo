from django.contrib.auth.models import User
from django.core.management import BaseCommand

import csv

from languageschool.models import AppUser, Game, Language, Category, Article, Word, Meaning, Conjugation, Score, \
    GameRound


def write_in_csv(filename, columns, data):
    # writing to csv file
    with open(f"C:/Users/Humberto/Desktop/Humberto/Study/WebDev/Pajelingo/backups/{filename}", 'w', newline='') as f:
        # creating a csv dict writer object
        writer = csv.writer(f)

        # writing headers (field names)
        writer.writerow(columns)

        # writing data rows
        writer.writerows(data)


def extract(cls, columns, foreign_keys=None, many_to_many=None):
    data = []

    if foreign_keys is None:
        foreign_keys = []

    if many_to_many is None:
        many_to_many = []

    records = cls.objects.all()

    for record in records:
        row = []

        for column in columns:
            attr = getattr(record, column)
            row.append("None" if attr is None else attr)

        for column in foreign_keys:
            obj = getattr(record, column)
            row.append("None" if obj is None else obj.id)

        for column in many_to_many:
            objs = getattr(record, column).all()
            many_to_many_column = []
            if objs is not None:
                for obj in objs:
                    many_to_many_column.append(obj.id)
            row.append(many_to_many_column)

        data.append(row)

    write_in_csv(f"{cls.__name__}.csv", columns + foreign_keys + many_to_many, data)


class Command(BaseCommand):
    def handle(self, *args, **options):
        extract(Game, ["id", "game_name", "android_game_activity", "image", "link", "instructions"])
        extract(Language, ["id", "language_name", "personal_pronoun_1", "personal_pronoun_2", "personal_pronoun_3",
                           "personal_pronoun_4", "personal_pronoun_5", "personal_pronoun_6", "flag_image"])
        extract(Category, ["id", "category_name"])
        extract(Article, ["id", "article_name"], foreign_keys=["language"])
        extract(Word, ["id", "word_name", "image"], foreign_keys=["language", "article", "category"],
                many_to_many=["synonyms"])
        extract(Meaning, ["id", "meaning"], foreign_keys=["word"])
        extract(Conjugation,
                ["id", "conjugation_1", "conjugation_2", "conjugation_3",
                 "conjugation_4", "conjugation_5", "conjugation_6", "tense"], foreign_keys=["word"])
        extract(Score, ["id", "score"], foreign_keys=["user", "language", "game"])
        extract(GameRound, ["id", "round_data"], foreign_keys=["game", "user"])
        extract(AppUser, ["id", "picture"], foreign_keys=["user"], many_to_many=["favorite_words"])
        extract(User, ["id", "username", "email", "is_active", "is_staff", "last_login", "date_joined"])