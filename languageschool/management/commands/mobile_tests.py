import argparse
import random

from django.core.management import BaseCommand

from languageschool.models import Game, Language, Score, Word, User


class SetUpAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        list_of_ids = [self.create_test_user("test-android@test.com", "test-android", "str0ng-p4ssw0rd", "bio"),
                       self.create_test_user("update-test-android0@test.com", "update-test-android0",
                                             "upd4te-str0ng-p4ssw0rd0", "bio 0"),
                       self.create_test_user("update-test-android1@test.com", "update-test-android1",
                                             "upd4te-str0ng-p4ssw0rd1", "bio 1"),
                       self.create_test_user("update-test-android2@test.com", "update-test-android2",
                                             "upd4te-str0ng-p4ssw0rd2", "bio 2"),
                       self.create_test_user("update-test-android3@test.com", "update-test-android3",
                                             "upd4te-str0ng-p4ssw0rd3", "bio 3"),
                       self.create_test_user("update-test-android4@test.com", "update-test-android4",
                                             "upd4te-str0ng-p4ssw0rd4", "bio 4"),
                       self.create_test_user("test-android-delete@test.com", "test-android-delete",
                                             "str0ng-p4ssw0rd", "bio delete")]

        test_user = User.objects.get(pk=list_of_ids[0])

        games = Game.objects.all()
        languages = Language.objects.all()
        words = Word.objects.all()

        for i in range(10):
            for language in languages:
                words_in_language = words.filter(language=language)
                random_word = random.choice(words_in_language)

                test_user.favorite_words.add(random_word)
                test_user.save()

        for game in games:
            for language in languages:
                Score.objects.create(user=test_user, language=language, game=game, score=random.randint(1, 1000))

        print("Users created for mobile tests:")
        print(list_of_ids)

    def create_test_user(self, email, username, password, bio):
        test_user = User.objects.create_user(email=email, username=username, password=password, bio=bio)
        return test_user.id


class TearDownAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        self.delete_test_user_by_id(list_of_ids=values)
        self.delete_test_user_by_username(username="new-test-android")
        print("Tear down completed")

    def delete_test_user_by_id(self, list_of_ids):
        for pk in list_of_ids:
            try:
                user = User.objects.get(pk=pk)
                user.delete()
            except User.DoesNotExist:
                print(f"User with pk {pk} was not found")

    def delete_test_user_by_username(self, username):
        try:
            user = User.objects.get(username=username)
            user.delete()
        except User.DoesNotExist:
            print(f"User with username {username} was not found")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--setup', action=SetUpAction, help="Sets up mobile test data (create data necessary to mobile tests)", nargs=0)
        parser.add_argument('--teardown', action=TearDownAction, nargs='*', help="Tears down mobile test data (delete data necessary to mobile tests)")

    def handle(self, *args, **options):
        pass

