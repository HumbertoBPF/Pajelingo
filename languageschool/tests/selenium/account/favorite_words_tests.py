import random

import pytest
from django.utils.crypto import get_random_string

from languageschool.tests.selenium.utils import assert_is_login_page, authenticate_user
from languageschool.tests.selenium.word_list_test_utils import modal_form_rendering, search, \
    search_with_language_filter, search_with_search_pattern, search_with_search_pattern_and_language_filter, \
    toggle_favorite_word, search_with_no_results, access_meaning_page, toggle_favorite_word_in_meaning_page
from pajelingo.settings import FRONT_END_URL

FAVORITE_WORDS_URL = FRONT_END_URL + "/profile/favorite-words"


@pytest.mark.django_db
def test_favorite_words_requires_authentication(live_server, selenium_driver):
    selenium_driver.get(FAVORITE_WORDS_URL)
    assert_is_login_page(selenium_driver)


@pytest.mark.django_db
def test_favorite_words_modal_rendering(live_server, selenium_driver, account, languages):
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)
    selenium_driver.get(FAVORITE_WORDS_URL)
    modal_form_rendering(selenium_driver, languages, user)


@pytest.mark.django_db
def test_favorite_words_search(live_server, selenium_driver, account, languages):
    user, password = account()[0]
    # app_user = AppUser.objects.filter(user=user).first()
    authenticate_user(selenium_driver, user.username, password)
    selenium_driver.get(FAVORITE_WORDS_URL)
    # search(selenium_driver, app_user.favorite_words.all(), app_user)


@pytest.mark.django_db
def test_favorite_words_search_with_language_filters(live_server, selenium_driver, account, languages):
    user, password = account()[0]
    # app_user = AppUser.objects.filter(user=user).first()
    authenticate_user(selenium_driver, user.username, password)
    random_language = random.choice(languages)
    selenium_driver.get(FAVORITE_WORDS_URL)
    # search_with_language_filter(selenium_driver, app_user.favorite_words.all(), app_user, random_language)


@pytest.mark.django_db
def test_favorite_words_search_with_search_pattern(live_server, selenium_driver, account):
    user, password = account()[0]
    # app_user = AppUser.objects.filter(user=user).first()
    authenticate_user(selenium_driver, user.username, password)
    search_pattern = get_random_string(1)
    selenium_driver.get(FAVORITE_WORDS_URL)
    # search_with_search_pattern(selenium_driver, app_user.favorite_words.all(), app_user, search_pattern)


@pytest.mark.django_db
def test_favorite_words_search_with_search_pattern_and_language_filter(live_server, selenium_driver, account,
                                                                       languages):
    user, password = account()[0]
    # app_user = AppUser.objects.filter(user=user).first()
    authenticate_user(selenium_driver, user.username, password)
    search_pattern = get_random_string(1)
    random_language = random.choice(languages)
    selenium_driver.get(FAVORITE_WORDS_URL)
    # search_with_search_pattern_and_language_filter(selenium_driver, app_user.favorite_words.all(), app_user,
    #                                                search_pattern, random_language)


@pytest.mark.django_db
def test_favorite_words_toggle_favorite_word(live_server, selenium_driver, account):
    user, password = account()[0]
    # app_user = AppUser.objects.filter(user=user).first()
    authenticate_user(selenium_driver, user.username, password)
    selenium_driver.get(FAVORITE_WORDS_URL)
    # toggle_favorite_word(selenium_driver, app_user)


@pytest.mark.django_db
def test_favorite_words_search_no_results(live_server, selenium_driver, account):
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)
    selenium_driver.get(FAVORITE_WORDS_URL)
    search_with_no_results(selenium_driver)


@pytest.mark.django_db
def test_favorite_words_meaning(live_server, selenium_driver, account, words, meanings,):
    user, password = account()[0]
    # app_user = AppUser.objects.filter(user=user).first()
    authenticate_user(selenium_driver, user.username, password)
    selenium_driver.get(FAVORITE_WORDS_URL)
    # access_meaning_page(selenium_driver, app_user)


@pytest.mark.django_db
def test_favorite_words_meaning_toggle_favorite_word(live_server, selenium_driver, account, words, meanings):
    user, password = account()[0]
    # app_user = AppUser.objects.filter(user=user).first()
    authenticate_user(selenium_driver, user.username, password)
    selenium_driver.get(FAVORITE_WORDS_URL)
    # toggle_favorite_word_in_meaning_page(selenium_driver, app_user)
