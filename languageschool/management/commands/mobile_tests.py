import argparse
import random

from django.contrib.auth.models import User
from django.core.management import BaseCommand

from languageschool.models import Game, Language, Score, Word


class SetUpAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        list_of_ids = [self.create_test_user("test-android@test.com", "test-android", "str0ng-p4ssw0rd"),
                       self.create_test_user("update-test-android0@test.com", "update-test-android0",
                                             "upd4te-str0ng-p4ssw0rd0"),
                       self.create_test_user("update-test-android1@test.com", "update-test-android1",
                                             "upd4te-str0ng-p4ssw0rd1"),
                       self.create_test_user("update-test-android2@test.com", "update-test-android2",
                                             "upd4te-str0ng-p4ssw0rd2"),
                       self.create_test_user("update-test-android3@test.com", "update-test-android3",
                                             "upd4te-str0ng-p4ssw0rd3"),
                       self.create_test_user("update-test-android4@test.com", "update-test-android4",
                                             "upd4te-str0ng-p4ssw0rd4"),
                       self.create_test_user("test-android-delete@test.com", "test-android-delete", "str0ng-p4ssw0rd")]

        test_user = User.objects.get(pk=list_of_ids[0])
        # test_app_user = AppUser.objects.get(user=test_user)

        games = Game.objects.all()
        languages = Language.objects.all()
        words = Word.objects.all()

        for i in range(10):
            for language in languages:
                words_in_language = words.filter(language=language)
                random_word = random.choice(words_in_language)

                # test_app_user.favorite_words.add(random_word)
                # test_app_user.save()

        for game in games:
            for language in languages:
                Score.objects.create(user=test_user, language=language, game=game, score=random.randint(1, 1000))

        print("Users created for mobile tests:")
        print(list_of_ids)

    def create_test_user(self, email, username, password):
        test_user = User.objects.create_user(email=email, username=username)
        test_user.set_password(password)
        test_user.save()
        return test_user.id


class TearDownAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        self.delete_test_user_by_id(list_of_ids=values)
        self.delete_test_user_by_username(username="new-test-android")
        print("Tear down completed")

    def delete_test_user_by_id(self, list_of_ids):
        for pk in list_of_ids:
            user = User.objects.filter(pk=pk).first()
            if user is not None:
                user.delete()

    def delete_test_user_by_username(self, username):
        user = User.objects.filter(username=username).first()
        if user is not None:
            user.delete()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--setup', action=SetUpAction, help="Sets up mobile test data (create data necessary to mobile tests)", nargs=0)
        parser.add_argument('--teardown', action=TearDownAction, nargs='*', help="Tears down mobile test data (delete data necessary to mobile tests)")

    def handle(self, *args, **options):
        pass

