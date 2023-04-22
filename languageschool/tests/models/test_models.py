import random

import pytest
from django.db import IntegrityError
from django.utils.crypto import get_random_string

from languageschool.models import Article, Word, Conjugation, Score, Game


@pytest.mark.django_db
def test_unique_fields_article(languages):
    article_name = get_random_string(random.randint(3, 5))
    language = random.choice(languages)
    Article.objects.create(article_name=article_name, language=language)
    with pytest.raises(IntegrityError) as e:
        Article.objects.create(article_name=article_name, language=language)
    assert str(e.value).startswith("UNIQUE constraint failed:")


@pytest.mark.django_db
def test_unique_fields_word(languages, articles):
    word_name = get_random_string(random.randint(10, 30))
    language = random.choice(languages)
    article = random.choice(articles)
    Word.objects.create(word_name=word_name, language=language, article=article)
    with pytest.raises(IntegrityError) as e:
        Word.objects.create(word_name=word_name, language=language, article=article)
    assert str(e.value).startswith("UNIQUE constraint failed:")


@pytest.mark.django_db
def test_unique_fields_conjugation(words):
    word = random.choice(words)
    tense = get_random_string(random.randint(10, 30))
    Conjugation.objects.create(word=word, tense=tense)
    with pytest.raises(IntegrityError) as e:
        Conjugation.objects.create(word=word, tense=tense)
    assert str(e.value).startswith("UNIQUE constraint failed:")


@pytest.mark.django_db
def test_unique_fields_score(account, languages):
    user, _ = account()[0]
    language = random.choice(languages)
    game = random.choice(Game.objects.all())
    Score.objects.create(user=user, language=language, game=game, score=random.randint(10, 100))
    with pytest.raises(IntegrityError) as e:
        Score.objects.create(user=user, language=language, game=game, score=random.randint(10, 100))
    assert str(e.value).startswith("UNIQUE constraint failed:")
