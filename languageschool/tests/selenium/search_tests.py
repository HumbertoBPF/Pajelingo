import math
import random

import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import Word
from languageschool.tests.selenium.utils import assert_menu, find_element, wait_text_to_be_present
from pajelingo.settings import FRONT_END_URL

SEARCH_URL = FRONT_END_URL + "/search"
CSS_SELECTOR_SEARCH_FORM_INPUT = (By.CSS_SELECTOR, "main form .form-floating .form-control")
CSS_SELECTOR_FORM_CHECK = (By.CSS_SELECTOR, "main form .form-check")
CSS_SELECTOR_SUBMIT_BUTTON = (By.CSS_SELECTOR, "main form .btn-success")
CSS_SELECTOR_CARDS = (By.CSS_SELECTOR, "main .card")
CSS_SELECTOR_PAGINATION = (By.CSS_SELECTOR, "main .pagination")
CSS_SELECTOR_ACTIVE_PAGE_BUTTON = (By.CSS_SELECTOR, "main .pagination .active .page-link")

def assert_search_results(selenium_driver, words, current_page, number_pages, language=None, search__pattern=""):
    cards = selenium_driver.find_elements(CSS_SELECTOR_CARDS[0], CSS_SELECTOR_CARDS[1])

    assert len(cards) == len(words) % 12 if (current_page == number_pages) else 12

    for card in cards:
        flag_img = card.find_element(By.CSS_SELECTOR, "img")
        alt_flag_img = flag_img.get_attribute("alt")
        language_name = alt_flag_img.split(" language flag")[0]
        word_name = card.find_element(By.CSS_SELECTOR, ".card-body .card-text").text
        assert Word.objects.filter(
            language__language_name=language_name,
            word_name=word_name
        ).exists()

        if language is not None:
            assert language_name == language.language_name

        assert search__pattern.lower() in word_name.lower()


def assert_pagination(selenium_driver, current_page, number_pages):
    pagination = find_element(selenium_driver, CSS_SELECTOR_PAGINATION)

    page_buttons = pagination.find_elements(By.CSS_SELECTOR, ".page-link")
    active_page_button = find_element(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON)
    first_page_button = page_buttons[0 if (current_page == 1) else 1]
    last_page_button = page_buttons[-1 if (current_page == number_pages) else -2]

    expected_text_first_page_button = "1\n(current)" if (current_page == 1) else "1"
    expected_text_last_page_button = "{}\n(current)".format(number_pages) \
        if (current_page == number_pages) else str(number_pages)

    if current_page != 1:
        assert page_buttons[0].text == "‹\nPrevious"

    assert active_page_button.text == "{}\n(current)".format(current_page)
    assert first_page_button.text == expected_text_first_page_button
    assert last_page_button.text == expected_text_last_page_button

    if current_page != number_pages:
        assert page_buttons[-1].text == "›\nNext"


def go_to_next_page(selenium_driver, current_page, number_pages):
    if current_page != number_pages:
        pagination = find_element(selenium_driver, CSS_SELECTOR_PAGINATION)
        page_buttons = pagination.find_elements(By.CSS_SELECTOR, ".page-link")
        selenium_driver.execute_script("arguments[0].click();", page_buttons[-1])


@pytest.mark.django_db
def test_search_form(live_server, selenium_driver, languages):
    """
    Tests that the search form is displayed with a search text input, all the languages as options in the checkbox
    group, and the submit button.
    """
    selenium_driver.get(SEARCH_URL)

    assert_menu(selenium_driver)

    search_form_input = find_element(selenium_driver, CSS_SELECTOR_SEARCH_FORM_INPUT)
    find_element(selenium_driver, CSS_SELECTOR_FORM_CHECK)
    search_form_checkboxes = selenium_driver.find_elements(CSS_SELECTOR_FORM_CHECK[0], CSS_SELECTOR_FORM_CHECK[1])
    search_form_submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    assert search_form_input.get_attribute("placeholder") == "Search for..."
    assert len(search_form_checkboxes) == len(languages)

    for i in range(len(languages)):
        assert search_form_checkboxes[i].find_element(By.CSS_SELECTOR, "label").text == languages[i].language_name
        assert search_form_checkboxes[i].find_element(By.CSS_SELECTOR, "input")\
                   .get_attribute("value") == languages[i].language_name

    assert search_form_submit_button.text == "Search"


@pytest.mark.django_db
def test_search(live_server, selenium_driver, words, languages):
    selenium_driver.get(SEARCH_URL)

    find_element(selenium_driver, CSS_SELECTOR_FORM_CHECK)
    search_form_checkboxes = selenium_driver.find_elements(CSS_SELECTOR_FORM_CHECK[0], CSS_SELECTOR_FORM_CHECK[1])
    search_form_submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    for search_form_checkbox in search_form_checkboxes:
        search_form_checkbox.find_element(By.CSS_SELECTOR, ".form-check-input").click()

    search_form_submit_button.click()

    number_pages = math.ceil(len(words) / 12)

    for i in range(number_pages):
        current_page = i + 1
        wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, str(current_page))

        assert_search_results(selenium_driver, words, current_page, number_pages)
        assert_pagination(selenium_driver, current_page, number_pages)

        go_to_next_page(selenium_driver, current_page, number_pages)


@pytest.mark.django_db
def test_search_with_language_filter(live_server, selenium_driver, words, languages):
    random_language = random.choice(languages)

    selenium_driver.get(SEARCH_URL)

    find_element(selenium_driver, CSS_SELECTOR_FORM_CHECK)
    search_form_checkboxes = selenium_driver.find_elements(CSS_SELECTOR_FORM_CHECK[0], CSS_SELECTOR_FORM_CHECK[1])
    search_form_submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    for search_form_checkbox in search_form_checkboxes:
        if search_form_checkbox.text == random_language.language_name:
            search_form_checkbox.find_element(By.CSS_SELECTOR, ".form-check-input").click()

    search_form_submit_button.click()

    words = words.filter(language=random_language)
    number_pages = math.ceil(len(words) / 12)

    for i in range(number_pages):
        current_page = i + 1
        wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, str(current_page))

        assert_search_results(selenium_driver, words, current_page, number_pages, language=random_language)
        assert_pagination(selenium_driver, current_page, number_pages)

        go_to_next_page(selenium_driver, current_page, number_pages)


@pytest.mark.django_db
def test_search_with_search_pattern(live_server, selenium_driver, words, languages):
    search_pattern = get_random_string(1)
    selenium_driver.get(SEARCH_URL)

    search_form_input = find_element(selenium_driver, CSS_SELECTOR_SEARCH_FORM_INPUT)
    find_element(selenium_driver, CSS_SELECTOR_FORM_CHECK)
    search_form_checkboxes = selenium_driver.find_elements(CSS_SELECTOR_FORM_CHECK[0], CSS_SELECTOR_FORM_CHECK[1])
    search_form_submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    search_form_input.send_keys(search_pattern)
    for search_form_checkbox in search_form_checkboxes:
        search_form_checkbox.find_element(By.CSS_SELECTOR, ".form-check-input").click()

    search_form_submit_button.click()

    words = words.filter(word_name__icontains=search_pattern)
    number_pages = math.ceil(len(words) / 12)

    for i in range(number_pages):
        current_page = i + 1
        wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, str(current_page))

        assert_search_results(selenium_driver, words, current_page, number_pages, search__pattern=search_pattern)
        assert_pagination(selenium_driver, current_page, number_pages)

        go_to_next_page(selenium_driver, current_page, number_pages)


@pytest.mark.django_db
def test_search_with_search_pattern_and_language_filter(live_server, selenium_driver, words, languages):
    search_pattern = get_random_string(1)
    random_language = random.choice(languages)

    selenium_driver.get(SEARCH_URL)

    search_form_input = find_element(selenium_driver, CSS_SELECTOR_SEARCH_FORM_INPUT)
    find_element(selenium_driver, CSS_SELECTOR_FORM_CHECK)
    search_form_checkboxes = selenium_driver.find_elements(CSS_SELECTOR_FORM_CHECK[0], CSS_SELECTOR_FORM_CHECK[1])
    search_form_submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    search_form_input.send_keys(search_pattern)
    for search_form_checkbox in search_form_checkboxes:
        if search_form_checkbox.text == random_language.language_name:
            search_form_checkbox.find_element(By.CSS_SELECTOR, ".form-check-input").click()

    search_form_submit_button.click()

    words = words.filter(word_name__icontains=search_pattern, language=random_language)
    number_pages = math.ceil(len(words) / 12)

    for i in range(number_pages):
        current_page = i + 1
        wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, str(current_page))

        assert_search_results(selenium_driver, words, current_page, number_pages,
                              language=random_language, search__pattern=search_pattern)
        assert_pagination(selenium_driver, current_page, number_pages)

        go_to_next_page(selenium_driver, current_page, number_pages)
