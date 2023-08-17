import random

import pytest
from django.utils.crypto import get_random_string

from languageschool.tests.selenium.utils import authenticate_user
from languageschool.tests.selenium.word_list_test_utils import search, \
    search_with_search_pattern_and_language_filter, \
    toggle_favorite_word, search_with_no_results, access_meaning_page, toggle_favorite_word_in_meaning_page
from pajelingo.settings import FRONT_END_URL

SEARCH_URL = FRONT_END_URL + "/dictionary"


@pytest.mark.parametrize("is_authenticated", [True, False])
@pytest.mark.django_db
def test_search(live_server, account, selenium_driver, words, languages, is_authenticated):
    user, password = account()[0]

    if is_authenticated:
        authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(SEARCH_URL)
    search(selenium_driver, words, user if is_authenticated else None)


@pytest.mark.parametrize("is_authenticated", [True, False])
@pytest.mark.django_db
def test_search_with_search_pattern_and_language_filter(live_server, selenium_driver, account, words, languages,
                                                        is_authenticated):
    user, password = account()[0]

    if is_authenticated:
        authenticate_user(selenium_driver, user.username, password)

    search_pattern = get_random_string(1)
    random_language = random.choice(languages)
    selenium_driver.get(SEARCH_URL)
    search_with_search_pattern_and_language_filter(selenium_driver, words, user if is_authenticated else None,
                                                   search_pattern, random_language)


@pytest.mark.django_db
def test_search_toggle_favorite_word(live_server, selenium_driver, account):
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)
    selenium_driver.get(SEARCH_URL)
    toggle_favorite_word(selenium_driver, user)


@pytest.mark.django_db
def test_search_no_results(live_server, selenium_driver, words, languages):
    selenium_driver.get(SEARCH_URL)
    search_with_no_results(selenium_driver)


@pytest.mark.parametrize("is_authenticated", [True, False])
@pytest.mark.django_db
def test_meaning(live_server, selenium_driver, account, words, meanings, is_authenticated):
    user, password = account()[0]

    if is_authenticated:
        authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(SEARCH_URL)
    access_meaning_page(selenium_driver, user if is_authenticated else None)


@pytest.mark.django_db
def test_meaning_toggle_favorite_word(live_server, selenium_driver, account, words, meanings):
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)
    selenium_driver.get(SEARCH_URL)
    toggle_favorite_word_in_meaning_page(selenium_driver, user)
