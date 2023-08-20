import math
import random

import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import Word
from languageschool.tests.selenium.utils import authenticate_user, find_by_test_id, get_language_from_word_card, \
    get_word_name_from_card_word, assert_pagination, go_to_next_page
from pajelingo.settings import FRONT_END_URL

CSS_SELECTOR_CARDS = (By.CSS_SELECTOR, "main .card")


@pytest.mark.django_db
def test_favorite_words_search(live_server, selenium_driver, account, languages):
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)

    find_by_test_id(selenium_driver, "profile-dropdown").click()
    find_by_test_id(selenium_driver, "profile-item").click()
    find_by_test_id(selenium_driver, "favorite-item").click()

    number_words = user.favorite_words.count()
    number_pages = math.ceil(number_words / 12)

    for i in range(number_pages):
        current_page = i + 1

        cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

        for card in cards:
            language_name = get_language_from_word_card(card)
            word_name = get_word_name_from_card_word(card)

            word = Word.objects.filter(
                language__language_name=language_name,
                word_name=word_name
            ).first()

            assert word is not None

            if user.favorite_words.contains(word):
                find_by_test_id(selenium_driver, "heart-filled-icon")
            else:
                find_by_test_id(selenium_driver, "heart-icon")

        assert_pagination(selenium_driver, current_page, number_pages)

        go_to_next_page(selenium_driver, current_page, number_pages)


@pytest.mark.django_db
def test_favorite_words_search_with_search_pattern_and_language_filter(live_server, selenium_driver, account,
                                                                       languages):
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)

    find_by_test_id(selenium_driver, "profile-dropdown").click()
    find_by_test_id(selenium_driver, "profile-item").click()
    find_by_test_id(selenium_driver, "favorite-item").click()

    search_pattern = get_random_string(1)
    random_language = random.choice(languages)

    filter_button = find_by_test_id(selenium_driver, "filter-button")
    filter_button.click()

    search_form_input = find_by_test_id(selenium_driver, "search-input").find_element(By.CSS_SELECTOR, "input")
    search_form_input.send_keys(search_pattern)

    for language in languages:
        if language.id != random_language.id:
            language_checkbox = find_by_test_id(selenium_driver, f"{language.language_name}-check-item")
            language_checkbox.click()

    search_form_submit_button = find_by_test_id(selenium_driver, "apply-filters-button")
    search_form_submit_button.click()

    number_words = user.favorite_words.filter(word_name__icontains=search_pattern, language=random_language).count()
    number_pages = math.ceil(number_words / 12)

    for i in range(number_pages):
        current_page = i + 1

        cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

        for card in cards:
            language_name = get_language_from_word_card(card)
            word_name = get_word_name_from_card_word(card)

            word = Word.objects.filter(
                language__language_name=language_name,
                word_name=word_name
            ).first()

            assert word is not None

            if user.favorite_words.contains(word):
                find_by_test_id(selenium_driver, "heart-filled-icon")
            else:
                find_by_test_id(selenium_driver, "heart-icon")

            assert language_name == random_language.language_name
            assert search_pattern.lower() in word_name.lower()

        assert_pagination(selenium_driver, current_page, number_pages)

        go_to_next_page(selenium_driver, current_page, number_pages)


@pytest.mark.django_db
def test_favorite_words_search_no_results(live_server, selenium_driver, account, languages):
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)

    find_by_test_id(selenium_driver, "profile-dropdown").click()
    find_by_test_id(selenium_driver, "profile-item").click()
    find_by_test_id(selenium_driver, "favorite-item").click()

    filter_button = find_by_test_id(selenium_driver, "filter-button")
    filter_button.click()

    for language in languages:
        language_check = find_by_test_id(selenium_driver, f"{language.language_name}-check-item")
        language_check.click()

    search_form_submit_button = find_by_test_id(selenium_driver, "apply-filters-button")
    search_form_submit_button.click()

    no_results = find_by_test_id(selenium_driver, "no-results")
    no_results_img = find_by_test_id(selenium_driver,  "no-results-img")

    assert no_results.text == "No result matching your search was found"
    assert no_results_img.get_attribute("alt") == "No results"
