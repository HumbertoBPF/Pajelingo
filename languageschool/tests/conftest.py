import random

import pytest
from django.utils.crypto import get_random_string
from rest_framework.test import APIClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from languageschool.models import Language, Word, Article, Category, Conjugation, Game, Score, Meaning, User, Badge
from languageschool.tests.utils import get_valid_password, get_random_email, get_random_username, get_random_bio


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def languages():
    for _ in range(5):
        Language.objects.create(language_name=get_random_string(random.randint(10, 15)),
                               personal_pronoun_1=get_random_string(random.randint(1, 8)),
                               personal_pronoun_2=get_random_string(random.randint(1, 8)),
                               personal_pronoun_3=get_random_string(random.randint(1, 8)),
                               personal_pronoun_4=get_random_string(random.randint(1, 8)),
                               personal_pronoun_5=get_random_string(random.randint(1, 8)),
                               personal_pronoun_6=get_random_string(random.randint(1, 8)))
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
            random_article = random.choice(articles_language)
            word = Word.objects.create(word_name=get_random_string(random.randint(10, 30)),
                                       language=language,
                                       article=random_article)
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
    return Word.objects.filter(category=verb_category)


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


def game_factory(pk, game_name, link):
    return Game.objects.create(id=pk,
                               game_name=game_name,
                               android_game_activity=get_random_string(16),
                               instructions=get_random_string(64),
                               link=link)


@pytest.fixture(autouse=True)
def badges():
    Badge.objects.create(id=1,
                         name="Explorer",
                         color="008000" ,
                         description="Discover all the games in one language")
    Badge.objects.create(id=2,
                         name="Linguistic mastery",
                         color="0000FF",
                         description="Score more than 100 in all games in one language")
    Badge.objects.create(id=3,
                         name="Bilingual",
                         color="CD7F32",
                         description="Score than 100 in all games and two languages")
    Badge.objects.create(id=4,
                         name="Trilingual",
                         color="C0C0C0",
                         description="Score more than 100 in all games and three languages")
    Badge.objects.create(id=5,
                         name="Polyglot",
                         color="FFD700",
                         description="Score more than 100 in all games and four languages")
    return Badge.objects.all()


@pytest.fixture
def account(words, badges):
    def account_factory(n=1, is_active=True):
        accounts_list = []

        for _ in range(n):
            password = get_valid_password()

            user = User.objects.create_user(username=get_random_username(),
                                            email=get_random_email(),
                                            bio=get_random_bio(),
                                            password=password,
                                            is_active=is_active)

            for i in range(10):
                favorite_word = random.choice(words)
                user.favorite_words.add(favorite_word)

            user_badges = random.sample(list(badges.values_list("id", flat=True)), k=2)
            user.badges.add(*user_badges)

            accounts_list.append((user, password))
        return accounts_list
    return account_factory


@pytest.fixture
def score():
    def create_score(users, languages, initial_score=None):
        for user in users:
            for game in Game.objects.all():
                for language in languages:
                    score = initial_score
                    if initial_score is None:
                        score = random.randint(100, 1000)
                    Score.objects.create(user=user, game=game, language=language, score=score)
        return Score.objects.all()
    return create_score


@pytest.fixture
def categories():
    for i in range(random.randint(10, 30)):
        category = Category(category_name=get_random_string(random.randint(10, 30)))
        category.save()
    return Category.objects.all()


@pytest.fixture(autouse=True)
def games():
    game_factory(1, "Vocabulary training", "/vocabulary-game/")
    game_factory(2, "Guess the article", "/article-game/")
    game_factory(3, "Conjugation game", "/conjugation-game/")
    return Game.objects.all()


@pytest.fixture(scope="package", params=["Chrome", "Firefox", "Edge"])
def selenium_driver(request):
    # The window-size is necessary because sometimes Selenium does not find some web elements when in headless mode
    if request.param == "Firefox":
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument('--window-size=1920,1080')
        driver = webdriver.Firefox(service=Service("C:/Users/Humberto/Downloads/geckodriver.exe"), options=options)
    elif request.param == "Edge":
        options = EdgeOptions()
        options.add_argument("--headless")
        options.add_argument('--window-size=1920,1080')
        driver = webdriver.Edge(service=Service("C:/Users/Humberto/Downloads/msedgedriver.exe"), options=options)
    else:
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--window-size=1920,1080')
        driver = webdriver.Chrome(service=Service("C:/Users/Humberto/Downloads/chromedriver.exe"), options=options)
    yield driver
    driver.close()
