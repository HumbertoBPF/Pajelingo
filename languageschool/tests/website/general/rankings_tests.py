import random

import pytest
from django.urls import reverse
from django.utils.crypto import get_random_string
from pytest_django.asserts import assertQuerysetEqual
from rest_framework import status

from languageschool.models import Language


def create_test_score_data(accounts, games, languages, score):
    """
    Creates score data for the test.

    :param accounts: accounts fixture
    :param games: games fixture
    :param languages: languages fixture
    :param score: score fixture
    """
    users = []

    for user, password in accounts:
        users.append(user)

    score(users=users, games=games, languages=languages)


def assert_ranking(accounts, languages, response, language_filter):
    """
    Asserts that:

    - The returned status code is 200
    - The returned language context parameter matches the specified languages
    - The returned language context parameter matches the specified language filter
    - The scores are in decreasing order and that the expected number of scores was returned

    :param languages: languages fixture
    :param accounts: accounts fixture
    :param response: response object
    :param language_filter: language filter
    :type language_filter: Language
    """
    scores = response.context.get("scores")

    assert response.status_code == status.HTTP_200_OK
    assertQuerysetEqual(response.context.get("languages"), languages, ordered=False)
    if language_filter is not None:
        assert response.context.get("language").language_name == language_filter.language_name
    assert len(scores) == min(len(accounts), 10)
    # Checking if the scores are in decreasing order
    last_score = scores[0]
    for i in range(1, len(scores)):
        assert last_score.get("score") >= scores[i].get("score")
        last_score = scores[i]


def request_and_assert_rankings(client, accounts, games, languages, score, language_filter):
    """
    Requests the rankings, that is:

    - Prepare test score data
    - Requests the rankings through the concerned endpoint
    - Assert the request result

    :param client: Django test client
    :param accounts: accounts fixture
    :param games: games fixture
    :param languages: languages fixture
    :param score: score fixture
    :param language_filter: language filter that must be applied when requesting the rankings
    :type language_filter: Language

    :return: the resulting HTTP response object
    """
    create_test_score_data(accounts, games, languages, score)

    url = reverse('rankings')
    data = {}

    if language_filter is not None:
        data["language"] = language_filter.language_name

    response = client.get(url, data=data)

    assert_ranking(accounts, languages, response, language_filter)

    return response


@pytest.mark.parametrize(
    "has_language_filter", [True, False]
)
@pytest.mark.django_db
def test_rankings(client, account, games, languages, score, has_language_filter):
    accounts = account(n=random.randint(5, 30))
    language_filter = random.choice(languages) if has_language_filter else None
    request_and_assert_rankings(client, accounts, games, languages, score, language_filter)


@pytest.mark.django_db
def test_rankings_invalid_language_filter(client, account, games, languages, score):
    accounts = account(n=random.randint(5, 30))

    create_test_score_data(accounts, games, languages, score)

    url = reverse('rankings')
    data = {"language": get_random_string(random.randint(10, 30))}

    response = client.get(url, data=data)

    assert_ranking(accounts, languages, response, languages.first())


@pytest.mark.parametrize(
    "has_language_filter", [True, False]
)
@pytest.mark.django_db
def test_rankings_authenticated_user(client, account, games, languages, score, has_language_filter):
    accounts = account(n=random.randint(5, 30))
    user, password = accounts[0]
    language_filter = random.choice(languages) if has_language_filter else None

    client.login(username=user.username, password=password)

    response = request_and_assert_rankings(client, accounts, games, languages, score, language_filter)

    assert response.context.get('my_position') is not None
    assert response.context.get('my_score') is not None
