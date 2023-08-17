import random

import pytest
from selenium.webdriver.common.by import By

from languageschool.models import Score
from languageschool.tests.selenium.utils import authenticate_user, go_to_next_page, find_by_test_id, \
    wait_attribute_to_be_non_empty
from languageschool.tests.utils import get_users
from pajelingo.settings import FRONT_END_URL

RANKINGS_URL = f"{FRONT_END_URL}/rankings"
CSS_SELECTOR_RANKING_TABLE = (By.CSS_SELECTOR, "main .table")

TEST_ID_RANKING_SEPARATOR = "ranking-separator"
TEST_ID_USER_SCORE_RECORD = "user-score-record"

TEST_ID_LANGUAGE_SELECT = "select-language"
TEST_ID_ELLIPSIS_START = "ellipsis-start"
TEST_ID_ELLIPSIS_END = "ellipsis-end"
TEST_ID_PREVIOUS_PAGE = "previous-page"
TEST_ID_NEXT_PAGE = "next-page"
TEST_ID_CURRENT_PAGE = "current-page"


def assert_language_select(selenium_driver, languages):
    language_select = find_by_test_id(selenium_driver, TEST_ID_LANGUAGE_SELECT)
    language_select.click()

    for language in languages:
        option = language_select.find_element(By.ID, language.language_name)
        assert option.text == language.language_name
        assert option.get_attribute("value") == language.language_name


def get_expected_score(username, language):
    scores = Score.objects.filter(user__username=username, language=language)
    expected_score = 0

    for score in scores:
        expected_score += score.score

    return expected_score


def assert_ranking_dynamic_rows(selenium_driver, page, language):
    for i in range(10):
        row = find_by_test_id(selenium_driver, f"{i + 1}th-ranking-record")
        columns = row.find_elements(By.CSS_SELECTOR, "td")

        position_column = columns[0].text
        username_column = columns[1].text
        score_column = columns[2].text

        expected_score = get_expected_score(username_column, language)

        assert position_column == str(10 * (page - 1) + i + 1)
        assert score_column == str(expected_score)


def assert_authenticated_user_rows(selenium_driver, language, auth_user):
    separator_row = find_by_test_id(selenium_driver, TEST_ID_RANKING_SEPARATOR)
    columns = separator_row.find_elements(By.CSS_SELECTOR, "td")

    assert columns[0].text == "..."
    assert columns[1].text == "..."
    assert columns[2].text == "..."

    user_position = find_by_test_id(selenium_driver, TEST_ID_USER_SCORE_RECORD)

    user_score = get_expected_score(auth_user.username, language)
    columns = user_position.find_elements(By.CSS_SELECTOR, "th")

    username_column = columns[1].text
    score_column = columns[2].text

    assert username_column == auth_user.username
    assert score_column == str(user_score)

def assert_page_of_two(selenium_driver, page):
    current_page_button = find_by_test_id(selenium_driver, TEST_ID_CURRENT_PAGE)
    assert current_page_button.text == f"{page}\n(current)"

    if page == 1:
        next_page_button = find_by_test_id(selenium_driver, TEST_ID_NEXT_PAGE)
        second_page_button = find_by_test_id(selenium_driver, "2th-page")
        assert second_page_button.text == "2"
        assert next_page_button.text == "›\nNext"
    elif page == 2:
        previous_page_button = find_by_test_id(selenium_driver, TEST_ID_PREVIOUS_PAGE)
        first_page_button = find_by_test_id(selenium_driver, "1th-page")
        assert previous_page_button.text == "‹\nPrevious"
        assert first_page_button.text == "1"

def assert_page_of_three(selenium_driver, page):
    current_page_button = find_by_test_id(selenium_driver, TEST_ID_CURRENT_PAGE)
    assert current_page_button.text == f"{page}\n(current)"

    if page == 1:
        next_page_button = find_by_test_id(selenium_driver, TEST_ID_NEXT_PAGE)
        ellipsis_end = find_by_test_id(selenium_driver, TEST_ID_ELLIPSIS_END)
        third_page_button = find_by_test_id(selenium_driver, "3th-page")
        assert ellipsis_end.text == "…\nMore"
        assert third_page_button.text == "3"
        assert next_page_button.text == "›\nNext"
    elif page == 2:
        previous_page_button = find_by_test_id(selenium_driver, TEST_ID_PREVIOUS_PAGE)
        first_page_button = find_by_test_id(selenium_driver, "1th-page")
        third_page_button = find_by_test_id(selenium_driver, "3th-page")
        next_page_button = find_by_test_id(selenium_driver, TEST_ID_NEXT_PAGE)
        assert previous_page_button.text == "‹\nPrevious"
        assert first_page_button.text == "1"
        assert third_page_button.text == "3"
        assert next_page_button.text == "›\nNext"
    elif page == 3:
        previous_page_button = find_by_test_id(selenium_driver, TEST_ID_PREVIOUS_PAGE)
        first_page_button = find_by_test_id(selenium_driver, "1th-page")
        ellipsis_start = find_by_test_id(selenium_driver, TEST_ID_ELLIPSIS_START)
        assert previous_page_button.text == "‹\nPrevious"
        assert first_page_button.text == "1"
        assert ellipsis_start.text == "…\nMore"

def assert_page_of_five(selenium_driver, page):
    current_page_button = find_by_test_id(selenium_driver, TEST_ID_CURRENT_PAGE)
    assert current_page_button.text == f"{page}\n(current)"

    if page == 1:
        ellipsis_end = find_by_test_id(selenium_driver, TEST_ID_ELLIPSIS_END)
        last_page_button = find_by_test_id(selenium_driver, "5th-page")
        next_page_button = find_by_test_id(selenium_driver, TEST_ID_NEXT_PAGE)
        assert ellipsis_end.text == "…\nMore"
        assert last_page_button.text == "5"
        assert next_page_button.text == "›\nNext"
    elif page == 5:
        previous_page_button = find_by_test_id(selenium_driver, TEST_ID_PREVIOUS_PAGE)
        first_page_button = find_by_test_id(selenium_driver, "1th-page")
        ellipsis_start = find_by_test_id(selenium_driver, TEST_ID_ELLIPSIS_START)
        assert previous_page_button.text == "‹\nPrevious"
        assert first_page_button.text == "1"
        assert ellipsis_start.text == "…\nMore"
    elif page == 2:
        previous_page_button = find_by_test_id(selenium_driver, TEST_ID_PREVIOUS_PAGE)
        first_page_button = find_by_test_id(selenium_driver, "1th-page")
        ellipsis_end = find_by_test_id(selenium_driver, TEST_ID_ELLIPSIS_END)
        last_page_button = find_by_test_id(selenium_driver, "5th-page")
        next_page_button = find_by_test_id(selenium_driver, TEST_ID_NEXT_PAGE)
        assert previous_page_button.text == "‹\nPrevious"
        assert first_page_button.text == "1"
        assert ellipsis_end.text == "…\nMore"
        assert last_page_button.text == "5"
        assert next_page_button.text == "›\nNext"
    elif page == 4:
        previous_page_button = find_by_test_id(selenium_driver, TEST_ID_PREVIOUS_PAGE)
        first_page_button = find_by_test_id(selenium_driver, "1th-page")
        ellipsis_start = find_by_test_id(selenium_driver, TEST_ID_ELLIPSIS_START)
        last_page_button = find_by_test_id(selenium_driver, "5th-page")
        next_page_button = find_by_test_id(selenium_driver, TEST_ID_NEXT_PAGE)
        assert previous_page_button.text == "‹\nPrevious"
        assert first_page_button.text == "1"
        assert ellipsis_start.text == "…\nMore"
        assert last_page_button.text == "5"
        assert next_page_button.text == "›\nNext"
    else:
        previous_page_button = find_by_test_id(selenium_driver, TEST_ID_PREVIOUS_PAGE)
        first_page_button = find_by_test_id(selenium_driver, "1th-page")
        ellipsis_start = find_by_test_id(selenium_driver, TEST_ID_ELLIPSIS_START)
        ellipsis_end = find_by_test_id(selenium_driver, TEST_ID_ELLIPSIS_END)
        last_page_button = find_by_test_id(selenium_driver, "5th-page")
        next_page_button = find_by_test_id(selenium_driver, TEST_ID_NEXT_PAGE)
        assert previous_page_button.text == "‹\nPrevious"
        assert first_page_button.text == "1"
        assert ellipsis_start.text == "…\nMore"
        assert last_page_button.text == "5"
        assert ellipsis_end.text == "…\nMore"
        assert next_page_button.text == "›\nNext"

@pytest.mark.django_db
def test_rankings_unauthenticated_user_two_pages(live_server, selenium_driver, account, score, languages):
    number_of_pages = 2
    accounts = account(n=20)

    users = get_users(accounts)
    score(users, languages)

    random_language = random.choice(languages)

    selenium_driver.get(RANKINGS_URL)

    select_language = find_by_test_id(selenium_driver, TEST_ID_LANGUAGE_SELECT)
    wait_attribute_to_be_non_empty(select_language, "innerHTML", 10)
    select_language.find_element(By.ID, random_language.language_name).click()

    for i in range(number_of_pages):
        current_page = i + 1

        assert_language_select(selenium_driver, languages)

        assert_ranking_dynamic_rows(selenium_driver, current_page, random_language)

        assert_page_of_two(selenium_driver, current_page)

        go_to_next_page(selenium_driver, current_page, number_of_pages)

@pytest.mark.django_db
def test_rankings_authenticated_user_two_pages(live_server, selenium_driver, account, score, languages):
    number_of_pages = 2
    accounts = account(n=20)

    auth_user, password = accounts[0]
    authenticate_user(selenium_driver, auth_user.username, password)

    users = get_users(accounts)
    score(users, languages)

    random_language = random.choice(languages)

    selenium_driver.get(RANKINGS_URL)

    select_language = find_by_test_id(selenium_driver, TEST_ID_LANGUAGE_SELECT)
    wait_attribute_to_be_non_empty(select_language, "innerHTML", 10)
    select_language.find_element(By.ID, random_language.language_name).click()

    for i in range(number_of_pages):
        current_page = i + 1

        assert_language_select(selenium_driver, languages)

        assert_ranking_dynamic_rows(selenium_driver, current_page, random_language)
        assert_authenticated_user_rows(selenium_driver, random_language, auth_user)

        assert_page_of_two(selenium_driver, current_page)

        go_to_next_page(selenium_driver, current_page, number_of_pages)

@pytest.mark.django_db
def test_rankings_unauthenticated_user_three_pages(live_server, selenium_driver, account, score, languages):
    number_of_pages = 3
    accounts = account(n=30)

    users = get_users(accounts)
    score(users, languages)

    random_language = random.choice(languages)

    selenium_driver.get(RANKINGS_URL)

    select_language = find_by_test_id(selenium_driver, TEST_ID_LANGUAGE_SELECT)
    wait_attribute_to_be_non_empty(select_language, "innerHTML", 10)
    select_language.find_element(By.ID, random_language.language_name).click()

    for i in range(number_of_pages):
        current_page = i + 1

        assert_language_select(selenium_driver, languages)

        assert_ranking_dynamic_rows(selenium_driver, current_page, random_language)

        assert_page_of_three(selenium_driver, current_page)

        go_to_next_page(selenium_driver, current_page, number_of_pages)

@pytest.mark.django_db
def test_rankings_authenticated_user_three_pages(live_server, selenium_driver, account, score, languages):
    number_of_pages = 3
    accounts = account(n=30)

    auth_user, password = accounts[0]
    authenticate_user(selenium_driver, auth_user.username, password)

    users = get_users(accounts)
    score(users, languages)

    random_language = random.choice(languages)

    selenium_driver.get(RANKINGS_URL)

    select_language = find_by_test_id(selenium_driver, TEST_ID_LANGUAGE_SELECT)
    wait_attribute_to_be_non_empty(select_language, "innerHTML", 10)
    select_language.find_element(By.ID, random_language.language_name).click()

    for i in range(number_of_pages):
        current_page = i + 1

        assert_language_select(selenium_driver, languages)

        assert_ranking_dynamic_rows(selenium_driver, current_page, random_language)
        assert_authenticated_user_rows(selenium_driver, random_language, auth_user)

        assert_page_of_three(selenium_driver, current_page)

        go_to_next_page(selenium_driver, current_page, number_of_pages)

@pytest.mark.django_db
def test_rankings_unauthenticated_user_more_than_three_pages(live_server, selenium_driver, account, score, languages):
    number_of_pages = 5
    accounts = account(n=50)

    users = get_users(accounts)
    score(users, languages)

    random_language = random.choice(languages)

    selenium_driver.get(RANKINGS_URL)

    select_language = find_by_test_id(selenium_driver, TEST_ID_LANGUAGE_SELECT)
    wait_attribute_to_be_non_empty(select_language, "innerHTML", 10)
    select_language.find_element(By.ID, random_language.language_name).click()

    for i in range(number_of_pages):
        current_page = i + 1

        assert_language_select(selenium_driver, languages)

        assert_ranking_dynamic_rows(selenium_driver, current_page, random_language)

        assert_page_of_five(selenium_driver, current_page)

        go_to_next_page(selenium_driver, current_page, number_of_pages)

@pytest.mark.django_db
def test_rankings_authenticated_user_more_than_three_pages(live_server, selenium_driver, account, score, languages):
    number_of_pages = 5
    accounts = account(n=50)

    auth_user, password = accounts[0]
    authenticate_user(selenium_driver, auth_user.username, password)

    users = get_users(accounts)
    score(users, languages)

    random_language = random.choice(languages)

    selenium_driver.get(RANKINGS_URL)

    select_language = find_by_test_id(selenium_driver, TEST_ID_LANGUAGE_SELECT)
    wait_attribute_to_be_non_empty(select_language, "innerHTML", 10)
    select_language.find_element(By.ID, random_language.language_name).click()

    for i in range(5):
        current_page = i + 1

        assert_language_select(selenium_driver, languages)

        assert_ranking_dynamic_rows(selenium_driver, current_page, random_language)
        assert_authenticated_user_rows(selenium_driver, random_language, auth_user)

        assert_page_of_five(selenium_driver, current_page)

        go_to_next_page(selenium_driver, current_page, number_of_pages)
