import random

import pytest

from languageschool.models import Score, Badge


@pytest.mark.django_db
def test_achieve_explorer_badge(account, languages, games):
    user, _ = account()[0]
    random_language = random.choice(languages)

    for game in games:
        Score.objects.create(
            user=user,
            language=random_language,
            game=game,
            score=random.randint(1, 1000)
        )

    Badge.update_badges(user)

    assert user.badges.filter(id=1).exists()


@pytest.mark.django_db
def test_achieve_linguistic_mastery_badge(account, languages, games):
    random_language = random.choice(languages)
    user, _ = account()[0]

    for game in games:
        Score.objects.create(
            user=user,
            language=random_language,
            game=game,
            score=random.randint(100, 1000)
        )

    Badge.update_badges(user)

    assert user.badges.filter(id=1).exists()
    assert user.badges.filter(id=2).exists()


@pytest.mark.django_db
def test_achieve_bilingual_badge(account, languages, games):
    random_language_ids = random.sample(list(languages.values_list("id", flat=True)), k=2)
    user, _ = account()[0]

    for pk in random_language_ids:
        for game in games:
            Score.objects.create(
                user=user,
                language_id=pk,
                game=game,
                score=random.randint(100, 1000)
            )

    Badge.update_badges(user)

    assert user.badges.filter(id=1).exists()
    assert user.badges.filter(id=2).exists()
    assert user.badges.filter(id=3).exists()


@pytest.mark.django_db
def test_achieve_trilingual_badge(account, languages, games):
    random_language_ids = random.sample(list(languages.values_list("id", flat=True)), k=3)
    user, _ = account()[0]

    for pk in random_language_ids:
        for game in games:
            Score.objects.create(
                user=user,
                language_id=pk,
                game=game,
                score=random.randint(100, 1000)
            )

    Badge.update_badges(user)

    assert user.badges.filter(id=1).exists()
    assert user.badges.filter(id=2).exists()
    assert user.badges.filter(id=3).exists()
    assert user.badges.filter(id=4).exists()


@pytest.mark.django_db
def test_achieve_polyglot_badge(account, languages, games):
    number_languages = random.randint(4, languages.count())
    random_language_ids = random.sample(list(languages.values_list("id", flat=True)), k=number_languages)
    user, _ = account()[0]

    for pk in random_language_ids:
        for game in games:
            Score.objects.create(
                user=user,
                language_id=pk,
                game=game,
                score=random.randint(100, 1000)
            )

    Badge.update_badges(user)

    assert user.badges.filter(id=1).exists()
    assert user.badges.filter(id=2).exists()
    assert user.badges.filter(id=3).exists()
    assert user.badges.filter(id=4).exists()
    assert user.badges.filter(id=5).exists()
