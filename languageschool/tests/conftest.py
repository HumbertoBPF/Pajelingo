import random

import pytest
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from languageschool.models import Language, Word, Article, Category, Conjugation, Game, Score, Meaning, AppUser


@pytest.fixture
def languages():
    Language.objects.create(language_name="English",
                            personal_pronoun_1="I",
                            personal_pronoun_2="you",
                            personal_pronoun_3="he/she/it",
                            personal_pronoun_4="we",
                            personal_pronoun_5="you",
                            personal_pronoun_6="they")
    Language.objects.create(language_name="French",
                            personal_pronoun_1="je",
                            personal_pronoun_2="tu",
                            personal_pronoun_3="il/elle",
                            personal_pronoun_4="nous",
                            personal_pronoun_5="vous",
                            personal_pronoun_6="ils/elles")
    Language.objects.create(language_name="Portuguese",
                            personal_pronoun_1="eu",
                            personal_pronoun_2="tu",
                            personal_pronoun_3="ele/ela",
                            personal_pronoun_4="nós",
                            personal_pronoun_5="vós",
                            personal_pronoun_6="eles/elas")
    Language.objects.create(language_name="Spanish",
                            personal_pronoun_1="yo",
                            personal_pronoun_2="tú",
                            personal_pronoun_3="él/ella/usted",
                            personal_pronoun_4="nosotros",
                            personal_pronoun_5="vosotros",
                            personal_pronoun_6="ellos/ellas/ustedes")
    Language.objects.create(language_name="German",
                            personal_pronoun_1="ich",
                            personal_pronoun_2="du",
                            personal_pronoun_3="er/sie/es",
                            personal_pronoun_4="wir",
                            personal_pronoun_5="ihr",
                            personal_pronoun_6="sie/Sie")
    return Language.objects.all()


@pytest.fixture
def articles(languages):
    for language in languages:
        for _ in range(3):
            Article.objects.create(article_name=get_random_string(random.randint(3, 10)), language=language)
    return Article.objects.all()


@pytest.fixture
def words(languages, articles):
    for _ in range(5):
        synonyms = []
        for language in languages:
            articles_language = articles.filter(language=language)
            article_index = random.randint(0, len(articles_language) - 1)
            word = Word.objects.create(word_name=get_random_string(random.randint(10, 30)),
                                       language=language,
                                       article=articles_language[article_index])
            word.synonyms.set(synonyms.copy())
            synonyms.append(word)
    return Word.objects.all()


@pytest.fixture
def meanings(words):
    for word in words:
        for _ in range(random.randint(1, 5)):
            Meaning.objects.create(word=word, meaning=get_random_string(random.randint(1, 255)))
    return Meaning.objects.all()


@pytest.fixture
def verb_category():
    return Category.objects.create(category_name="verbs")


@pytest.fixture
def verbs(languages, verb_category):
    for language in languages:
        for _ in range(5):
            Word.objects.create(word_name=get_random_string(random.randint(10, 30)),
                                language=language,
                                category=verb_category)
    return Word.objects.all()


@pytest.fixture
def conjugations(verbs):
    for verb in verbs:
        Conjugation.objects.create(word=verb,
                                   conjugation_1=get_random_string(random.randint(10, 30)),
                                   conjugation_2=get_random_string(random.randint(10, 30)),
                                   conjugation_3=get_random_string(random.randint(10, 30)),
                                   conjugation_4=get_random_string(random.randint(10, 30)),
                                   conjugation_5=get_random_string(random.randint(10, 30)),
                                   conjugation_6=get_random_string(random.randint(10, 30)),
                                   tense=get_random_string(random.randint(10, 30)))
    return Conjugation.objects.all()


@pytest.fixture
def vocabulary_game():
    return Game.objects.create(id=1, game_tag="vocabulary_game", game_name="Vocabulary Game")


@pytest.fixture
def article_game():
    return Game.objects.create(id=2, game_tag="article_game", game_name="Article Game")


@pytest.fixture
def conjugation_game():
    return Game.objects.create(id=3, game_tag="conjugation_game", game_name="Conjugation Game")


@pytest.fixture
def account():
    return account_factory


def account_factory(n=1):
    accounts_list = []

    for _ in range(n):
        password = get_random_string(random.randint(6, 30))
        user = User.objects.create_user(username=get_random_string(random.randint(10, 30)),
                                        email=get_random_string(random.randint(10, 30)) + "@test.com",
                                        password=password)
        AppUser.objects.create(user=user)
        accounts_list.append((user, password))
    return accounts_list


@pytest.fixture
def score():
    def create_score(users, games, languages, initial_score=None):
        for user in users:
            for game in games:
                for language in languages:
                    score = initial_score
                    if initial_score is None:
                        score = random.randint(100, 1000)
                    Score.objects.create(user=user, game=game, language=language, score=score)
        return Score.objects.all()
    return create_score


def is_user_authenticated(client, user):
    """
    Verifies if the specified user is authenticated in the current session.

    :param client: Django client fixture
    :param user: instance of a user that we want to check that is authenticated
    :type user: User

    :return: boolean indicating if the specified user is authenticated
    """
    return auth.get_user(client).username == user.username
