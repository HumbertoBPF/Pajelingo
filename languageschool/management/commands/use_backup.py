import ast
import csv

from django.core.management import BaseCommand

from languageschool.models import Game, Category, Article, Word, Meaning, Conjugation, Score, GameRound, Language, User

def update_user_table_with_app_user_data():
    with open(f'C:/Users/Humberto/Desktop/Humberto/Study/WebDev/Pajelingo/backups/AppUser.csv', mode='r') as f:
        reader = csv.reader(f)
        next(reader, None)

        for row in reader:
            _, picture, user_id, favorite_words = row
            obj = User.objects.filter(id=user_id).first()
            obj.picture = picture
            obj.favorite_words.set(ast.literal_eval(favorite_words))
            obj.save()


def set_word_table_synonyms():
    with open(f'C:/Users/Humberto/Desktop/Humberto/Study/WebDev/Pajelingo/backups/Word.csv', mode='r') as f:
        reader = csv.reader(f)
        next(reader, None)

        for row in reader:
            word_id, word_name, image, language_id, article_id, category_id, synonyms = row
            word = Word.objects.filter(id=word_id).first()
            word.synonyms.set(ast.literal_eval(synonyms))
            word.save()


def fill_table(cls, many_to_many=None):
    if many_to_many is None:
        many_to_many = []

    with open(f'C:/Users/Humberto/Desktop/Humberto/Study/WebDev/Pajelingo/backups/{cls.__name__}.csv', mode='r') as f:
        reader = csv.reader(f)
        headers = next(reader, None)

        for row in reader:
            args = {}

            for i in range(len(row)):
                header = headers[i]
                column = row[i]

                if header in many_to_many:
                    continue

                args[header] = None if column == "None" else column

            cls.objects.create(**args)


class Command(BaseCommand):
    def handle(self, *args, **options):
        fill_table(User)

        for user in User.objects.all():
            user.set_password("str0ng-p4ssw0rd")
            user.save()

        fill_table(Game)
        fill_table(Language)
        fill_table(Category)
        fill_table(Article)
        fill_table(Word, many_to_many=["synonyms"])
        fill_table(Meaning)
        fill_table(Conjugation)
        fill_table(Score)
        update_user_table_with_app_user_data()
        fill_table(GameRound)
        set_word_table_synonyms()
