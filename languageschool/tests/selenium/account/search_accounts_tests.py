import math
import random

import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import User
from languageschool.tests.selenium.rankings_tests import RANKINGS_URL
from languageschool.tests.selenium.utils import wait_text_to_be_present, wait_number_of_elements_to_be, \
    CSS_SELECTOR_ACTIVE_PAGE_BUTTON, assert_pagination, go_to_next_page, assert_is_profile_page, scroll_to_element, \
    assert_profile_language_filter, assert_profile_scores, find_element, select_option_from_select_language
from languageschool.tests.utils import get_users_from_accounts
from pajelingo.settings import FRONT_END_URL

SEARCH_ACCOUNT_URL = FRONT_END_URL + "/accounts"
CSS_SELECTOR_SEARCH_INPUT = (By.CSS_SELECTOR, "main form .form-control")
CSS_SELECTOR_SUBMIT_BUTTON = (By.CSS_SELECTOR, "main form .btn-success")
CSS_SELECTOR_ACCOUNT_CARD = (By.CSS_SELECTOR, "main .card .card-body .card-text")
CSS_SELECTOR_LANGUAGE_SELECT = (By.CSS_SELECTOR, "main .form-select")


def assert_search_results(selenium_driver, q, current_page, accounts):
    query = "" if (q is None) else q

    number_pages = math.ceil(len(accounts) / 10)

    expected_number_of_cards = 10

    if (current_page == number_pages) and (len(accounts) % 10 != 0):
        expected_number_of_cards = len(accounts) % 10

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_ACCOUNT_CARD, expected_number_of_cards)

    account_cards = selenium_driver.find_elements(CSS_SELECTOR_ACCOUNT_CARD[0], CSS_SELECTOR_ACCOUNT_CARD[1])

    for account_card in account_cards:
        assert query.lower() in account_card.text.lower()
        assert User.objects.filter(
            username=account_card.text
        ).exists()


@pytest.mark.django_db
def test_search_account_form_rendering(live_server, selenium_driver):
    selenium_driver.get(SEARCH_ACCOUNT_URL)
    search_input = selenium_driver.find_element(CSS_SELECTOR_SEARCH_INPUT[0], CSS_SELECTOR_SEARCH_INPUT[1])
    submit_button = selenium_driver.find_element(CSS_SELECTOR_SUBMIT_BUTTON[0], CSS_SELECTOR_SUBMIT_BUTTON[1])

    assert search_input.get_attribute("placeholder") == "Search an account"
    assert submit_button.text == "Search account"


@pytest.mark.django_db
def test_search_all_account(live_server, selenium_driver, account):
    accounts = account(n=random.randint(11, 30))

    selenium_driver.get(SEARCH_ACCOUNT_URL)

    submit_button = selenium_driver.find_element(CSS_SELECTOR_SUBMIT_BUTTON[0], CSS_SELECTOR_SUBMIT_BUTTON[1])

    submit_button.click()

    number_pages = math.ceil(len(accounts)/10)

    for i in range(number_pages):
        current_page = i + 1

        wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, str(current_page))
        assert_search_results(selenium_driver, None, current_page, accounts)
        assert_pagination(selenium_driver, current_page, number_pages)
        go_to_next_page(selenium_driver, current_page, number_pages)


@pytest.mark.django_db
def test_search_account(live_server, selenium_driver, account):
    account(n=random.randint(11, 30))

    q = get_random_string(1)

    accounts = User.objects.filter(username__icontains=q)

    selenium_driver.get(SEARCH_ACCOUNT_URL)

    search_input = selenium_driver.find_element(CSS_SELECTOR_SEARCH_INPUT[0], CSS_SELECTOR_SEARCH_INPUT[1])
    submit_button = selenium_driver.find_element(CSS_SELECTOR_SUBMIT_BUTTON[0], CSS_SELECTOR_SUBMIT_BUTTON[1])

    search_input.send_keys(q)
    submit_button.click()

    number_pages = math.ceil(len(accounts)/10)

    for i in range(number_pages):
        current_page = i + 1

        wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, str(current_page))
        assert_search_results(selenium_driver, q, current_page, accounts)
        assert_pagination(selenium_driver, current_page, number_pages)
        go_to_next_page(selenium_driver, current_page, number_pages)


@pytest.mark.django_db
def test_select_account(live_server, selenium_driver, account, languages):
    account(n=random.randint(11, 30))

    selenium_driver.get(SEARCH_ACCOUNT_URL)

    submit_button = selenium_driver.find_element(CSS_SELECTOR_SUBMIT_BUTTON[0], CSS_SELECTOR_SUBMIT_BUTTON[1])

    submit_button.click()

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_ACCOUNT_CARD, 10)
    account_cards = selenium_driver.find_elements(CSS_SELECTOR_ACCOUNT_CARD[0], CSS_SELECTOR_ACCOUNT_CARD[1])

    account_card = random.choice(account_cards)
    username = account_card.text

    scroll_to_element(selenium_driver, account_card)
    account_card.click()

    assert_is_profile_page(selenium_driver, username)

    user = User.objects.get(username=username)
    random_language = random.choice(languages)

    assert_profile_language_filter(selenium_driver, languages)
    assert_profile_scores(selenium_driver, user, random_language)


@pytest.mark.django_db
def test_select_account_on_rankings_page(live_server, selenium_driver, account, score, languages):
    accounts = account(n=10)

    users = get_users_from_accounts(accounts)
    score(users, languages)

    random_language = random.choice(languages)

    selenium_driver.get(RANKINGS_URL)

    language_select = find_element(selenium_driver, CSS_SELECTOR_LANGUAGE_SELECT)
    select_option_from_select_language(language_select, random_language)

    css_selector_ranking_rows = (By.CSS_SELECTOR, "main .table tbody tr")
    wait_number_of_elements_to_be(selenium_driver, css_selector_ranking_rows, 10)

    ranking_rows = selenium_driver.find_elements(css_selector_ranking_rows[0], css_selector_ranking_rows[1])
    random_ranking_row = random.choice(ranking_rows)
    scroll_to_element(selenium_driver, random_ranking_row)

    record_columns = random_ranking_row.find_elements(By.CSS_SELECTOR, "td")
    username = record_columns[1].text

    random.choice(record_columns).click()

    assert_is_profile_page(selenium_driver, username)

    user = User.objects.get(username=username)
    random_language = random.choice(languages)

    assert_profile_language_filter(selenium_driver, languages)
    assert_profile_scores(selenium_driver, user, random_language)