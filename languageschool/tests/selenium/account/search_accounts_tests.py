import math
import random

import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import User
from languageschool.tests.selenium.rankings_tests import RANKINGS_URL
from languageschool.tests.selenium.utils import wait_text_to_be_present, wait_number_of_elements_to_be, \
    CSS_SELECTOR_ACTIVE_PAGE_BUTTON, assert_pagination, go_to_next_page, scroll_to_element, \
    find_element, assert_public_account_data, wait_attribute_to_be_non_empty, find_by_test_id
from languageschool.tests.utils import get_users, attribute_user_badges
from pajelingo.settings import FRONT_END_URL

SEARCH_ACCOUNT_URL = f"{FRONT_END_URL}/accounts"
TEST_ID_SPINNER = "spinner"
TEST_ID_SEARCH_INPUT = "search-input"
TEST_ID_SUBMIT_BUTTON = "submit-button"
CSS_SELECTOR_ACCOUNT_CARD = (By.CSS_SELECTOR, "main .card .card-body")
CSS_SELECTOR_LANGUAGE_SELECT = (By.CSS_SELECTOR, "main .form-select")


def get_username_from_account_card(account_card):
    username_field = account_card.find_element(By.CSS_SELECTOR, ".card-text:nth-of-type(1)")
    return username_field.text


def get_bio_from_account_card(account_card):
    bio_field = account_card.find_element(By.CSS_SELECTOR, ".card-text:nth-of-type(2)")
    bio = bio_field.text
    bio = bio.replace("Bio: ", "").replace("...", "")
    bio = "" if (bio == "-") else bio

    return bio


def assert_search_results(selenium_driver, q):
    account_cards = selenium_driver.find_elements(CSS_SELECTOR_ACCOUNT_CARD[0], CSS_SELECTOR_ACCOUNT_CARD[1])

    for account_card in account_cards:
        username = get_username_from_account_card(account_card)
        bio = get_bio_from_account_card(account_card)

        args = {
            "username": username
        }

        if len(bio) < 75:
            args["bio"] = bio
        else:
            args["bio__contains"] = bio

        assert User.objects.filter(**args).exists()
        assert q.lower() in username.lower()


@pytest.mark.django_db
def test_search_all_accounts(live_server, selenium_driver, account):
    number_pages = 3
    number_accounts = 30
    account(n=number_accounts)

    selenium_driver.get(SEARCH_ACCOUNT_URL)

    submit_button = find_by_test_id(selenium_driver, TEST_ID_SUBMIT_BUTTON)
    submit_button.click()

    for i in range(number_pages):
        current_page = i + 1

        wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, str(current_page))
        assert_search_results(selenium_driver, "")
        assert_pagination(selenium_driver, current_page, number_pages)
        go_to_next_page(selenium_driver, current_page, number_pages)


@pytest.mark.django_db
def test_search_account(live_server, selenium_driver, account):
    account(n=20)

    q = get_random_string(1)

    number_accounts = User.objects.filter(username__icontains=q).count()
    number_pages = math.ceil(number_accounts/10)

    selenium_driver.get(SEARCH_ACCOUNT_URL)

    search_input = find_by_test_id(selenium_driver, TEST_ID_SEARCH_INPUT).find_element(By.CSS_SELECTOR, "input")
    search_input.send_keys(q)

    submit_button = find_by_test_id(selenium_driver, TEST_ID_SUBMIT_BUTTON)
    submit_button.click()

    for i in range(number_pages):
        current_page = i + 1

        wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON, str(current_page))
        assert_search_results(selenium_driver, q)
        assert_pagination(selenium_driver, current_page, number_pages)
        go_to_next_page(selenium_driver, current_page, number_pages)


@pytest.mark.django_db
def test_select_account(live_server, selenium_driver, account, languages):
    account(n=10)
    attribute_user_badges()

    selenium_driver.get(SEARCH_ACCOUNT_URL)

    submit_button = find_by_test_id(selenium_driver, TEST_ID_SUBMIT_BUTTON)
    submit_button.click()

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_ACCOUNT_CARD, 10)
    account_cards = selenium_driver.find_elements(CSS_SELECTOR_ACCOUNT_CARD[0], CSS_SELECTOR_ACCOUNT_CARD[1])

    account_card = random.choice(account_cards)
    username = get_username_from_account_card(account_card)

    user = User.objects.get(username=username)

    scroll_to_element(selenium_driver, account_card)
    account_card.click()

    assert_public_account_data(selenium_driver, user)


@pytest.mark.django_db
def test_select_account_on_rankings_page(live_server, selenium_driver, account, score, languages):
    accounts = account(n=10)
    attribute_user_badges()

    users = get_users(accounts)
    score(users, languages)

    random_language = random.choice(languages)

    selenium_driver.get(RANKINGS_URL)

    language_select = find_element(selenium_driver, CSS_SELECTOR_LANGUAGE_SELECT)
    wait_attribute_to_be_non_empty(language_select, "innerHTML", 10)
    language_select.find_element(By.ID, random_language.language_name).click()

    css_selector_ranking_rows = (By.CSS_SELECTOR, "main .table tbody tr")
    wait_number_of_elements_to_be(selenium_driver, css_selector_ranking_rows, 10)

    ranking_rows = selenium_driver.find_elements(css_selector_ranking_rows[0], css_selector_ranking_rows[1])
    random_ranking_row = random.choice(ranking_rows)
    scroll_to_element(selenium_driver, random_ranking_row)

    record_columns = random_ranking_row.find_elements(By.CSS_SELECTOR, "td")
    username = record_columns[1].text

    user = User.objects.get(username=username)

    random.choice(record_columns).click()

    assert_public_account_data(selenium_driver, user)
