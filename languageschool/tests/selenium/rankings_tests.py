import math
import random
import time

import pytest
from selenium.webdriver.common.by import By

from languageschool.models import Score
from languageschool.tests.selenium.utils import find_element, authenticate_user, CSS_SELECTOR_PAGINATION, \
    CSS_SELECTOR_ACTIVE_PAGE_BUTTON, go_to_next_page, select_option_from_select_language
from pajelingo.settings import FRONT_END_URL

RANKINGS_URL = FRONT_END_URL + "/rankings"
CSS_SELECTOR_LANGUAGE_SELECT = (By.CSS_SELECTOR, "main .form-select")
CSS_SELECTOR_SELECT_OPTIONS = (By.CSS_SELECTOR, "main .form-select option")
CSS_SELECTOR_RANKING_TABLE = (By.CSS_SELECTOR, "main .table")
CSS_SELECTOR_IMAGE =  (By.CSS_SELECTOR, "main .justify-content-center img")


def create_users(accounts):
    users = []

    for account in accounts:
        users.append(account[0])

    return users


def assert_language_select(selenium_driver, languages):
    language_select = find_element(selenium_driver, CSS_SELECTOR_LANGUAGE_SELECT)
    language_select.click()

    languages_dict = {}

    for language in languages:
        languages_dict[language.language_name] = True

    find_element(selenium_driver, CSS_SELECTOR_SELECT_OPTIONS)
    language_options = selenium_driver.find_elements(CSS_SELECTOR_SELECT_OPTIONS[0], CSS_SELECTOR_SELECT_OPTIONS[1])

    for language_option in language_options:
        del languages_dict[language_option.text]

    assert len(languages_dict) == 0


def get_expected_score(username, language):
    scores = Score.objects.filter(user__username=username, language=language)
    expected_score = 0
    for score in scores:
        expected_score += score.score

    return expected_score


def assert_ranking_dynamic_rows(ranking_rows, checked_users, language, auth_user=None):
    if checked_users.get("dynamic_rows") is None:
        checked_users["dynamic_rows"] = {}

    ranking_users_dynamic_rows = checked_users["dynamic_rows"]
    nb_dynamic_rows = len(ranking_rows)

    if auth_user is not None:
        nb_dynamic_rows -= 2

    for i in range(nb_dynamic_rows):
        row = ranking_rows[i]
        columns = row.find_elements(By.CSS_SELECTOR, "td")

        position_column = columns[0].text
        username_column = columns[1].text
        score_column = columns[2].text

        expected_score = get_expected_score(username_column, language)

        assert position_column == str(len(ranking_users_dynamic_rows) + 1)
        assert ranking_users_dynamic_rows.get(username_column) is None
        assert score_column == str(expected_score)

        checked_users["dynamic_rows"][username_column] = {"position": position_column, "score": score_column}


def assert_authenticated_user_rows(ranking_rows, checked_users, language, auth_user):
    separator_row = ranking_rows[-2]
    columns = separator_row.find_elements(By.CSS_SELECTOR, "td")

    assert columns[0].text == "..."
    assert columns[1].text == "..."
    assert columns[2].text == "..."

    user_position = ranking_rows[-1]

    user_score = get_expected_score(auth_user.username, language)
    columns = user_position.find_elements(By.CSS_SELECTOR, "th")

    position_column = columns[0].text
    username_column = columns[1].text
    score_column = columns[2].text

    assert username_column == auth_user.username
    assert score_column == str(user_score)

    if checked_users.get("auth_user_row") is None:
        checked_users["auth_user_row"] = {"position": position_column, "score": score_column}
    else:
        assert position_column == checked_users["auth_user_row"].get("position")


def assert_ranking_content(selenium_driver, checked_users, language, auth_user=None):
    ranking_table = find_element(selenium_driver, CSS_SELECTOR_RANKING_TABLE)
    ranking_rows = ranking_table.find_elements(By.CSS_SELECTOR, "tbody tr")

    assert_ranking_dynamic_rows(ranking_rows, checked_users, language, auth_user=auth_user)

    if auth_user is not None:
        assert_authenticated_user_rows(ranking_rows, checked_users, language, auth_user=auth_user)


def assert_ranking_users(checked_users, users, auth_user=None):
    dynamic_rows = checked_users.get("dynamic_rows")
    assert len(dynamic_rows) == len(users)

    if auth_user is not None:
        auth_user_row = checked_users.get("auth_user_row")
        assert auth_user_row.get("position") == "(You) {}".format(dynamic_rows.get(auth_user.username).get("position"))
        assert auth_user_row.get("score") == dynamic_rows.get(auth_user.username).get("score")

@pytest.mark.parametrize("is_authenticated", [True, False])
@pytest.mark.django_db
def test_rankings_two_pages(live_server, selenium_driver, account, score, languages, is_authenticated):
    accounts = account(n=random.randint(11, 20))
    auth_user = None

    if is_authenticated:
        auth_user, password = accounts[0]
        authenticate_user(selenium_driver, auth_user.username, password)

    users = create_users(accounts)
    score(users, languages)

    number_pages = math.ceil(len(users)/10)
    random_language = random.choice(languages)

    selenium_driver.get(RANKINGS_URL)

    language_select = find_element(selenium_driver, CSS_SELECTOR_LANGUAGE_SELECT)
    select_option_from_select_language(language_select, random_language)

    checked_users = {}

    for i in range(number_pages):
        time.sleep(3)
        current_page = i + 1

        assert_language_select(selenium_driver, languages)

        assert_ranking_content(selenium_driver, checked_users, random_language, auth_user=auth_user)

        pagination = find_element(selenium_driver, CSS_SELECTOR_PAGINATION)
        pagination_buttons = pagination.find_elements(By.CSS_SELECTOR, ".page-link")
        active_pagination_button = find_element(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON)

        assert len(pagination_buttons) == 3
        assert active_pagination_button.text == "{}\n(current)".format(current_page)

        if current_page == 1:
            assert pagination_buttons[0].text == "1\n(current)"
            assert pagination_buttons[1].text == "2"
            assert pagination_buttons[2].text == "›\nNext"
        elif current_page == 2:
            assert pagination_buttons[0].text == "‹\nPrevious"
            assert pagination_buttons[1].text == "1"
            assert pagination_buttons[2].text == "2\n(current)"

        go_to_next_page(selenium_driver, current_page, number_pages)

    assert_ranking_users(checked_users, users, auth_user=auth_user)


@pytest.mark.parametrize("is_authenticated", [True, False])
@pytest.mark.django_db
def test_rankings_three_pages(live_server, selenium_driver, account, score, languages, is_authenticated):
    accounts = account(n=random.randint(21, 30))
    auth_user = None

    if is_authenticated:
        auth_user, password = accounts[0]
        authenticate_user(selenium_driver, auth_user.username, password)

    users = create_users(accounts)
    score(users, languages)

    number_pages = math.ceil(len(users) / 10)
    random_language = random.choice(languages)

    selenium_driver.get(RANKINGS_URL)

    language_select = find_element(selenium_driver, CSS_SELECTOR_LANGUAGE_SELECT)
    select_option_from_select_language(language_select, random_language)

    checked_users = {}

    for i in range(number_pages):
        current_page = i + 1

        assert_language_select(selenium_driver, languages)

        assert_ranking_content(selenium_driver, checked_users, random_language, auth_user=auth_user)

        pagination = find_element(selenium_driver, CSS_SELECTOR_PAGINATION)
        pagination_buttons = pagination.find_elements(By.CSS_SELECTOR, ".page-link")
        active_pagination_button = find_element(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON)

        assert active_pagination_button.text == "{}\n(current)".format(current_page)

        if current_page == 1:
            assert len(pagination_buttons) == 4
            assert pagination_buttons[0].text == "1\n(current)"
            assert pagination_buttons[1].text == "…\nMore"
            assert pagination_buttons[2].text == "3"
            assert pagination_buttons[3].text == "›\nNext"
        elif current_page == 2:
            assert len(pagination_buttons) == 5
            assert pagination_buttons[0].text == "‹\nPrevious"
            assert pagination_buttons[1].text == "1"
            assert pagination_buttons[2].text == "2\n(current)"
            assert pagination_buttons[3].text == "3"
            assert pagination_buttons[4].text == "›\nNext"
        elif current_page == 3:
            assert len(pagination_buttons) == 4
            assert pagination_buttons[0].text == "‹\nPrevious"
            assert pagination_buttons[1].text == "1"
            assert pagination_buttons[2].text == "…\nMore"
            assert pagination_buttons[3].text == "3\n(current)"

        go_to_next_page(selenium_driver, current_page, number_pages)

    assert_ranking_users(checked_users, users, auth_user=auth_user)


@pytest.mark.parametrize("is_authenticated", [True, False])
@pytest.mark.django_db
def test_rankings_more_than_three_pages(live_server, selenium_driver, account, score, languages, is_authenticated):
    accounts = account(n=random.randint(31, 50))
    auth_user = None

    if is_authenticated:
        auth_user, password = accounts[0]
        authenticate_user(selenium_driver, auth_user.username, password)

    users = create_users(accounts)
    score(users, languages)

    number_pages = math.ceil(len(users) / 10)
    random_language = random.choice(languages)

    selenium_driver.get(RANKINGS_URL)

    language_select = find_element(selenium_driver, CSS_SELECTOR_LANGUAGE_SELECT)
    select_option_from_select_language(language_select, random_language)

    checked_users = {}

    for i in range(number_pages):
        current_page = i + 1

        assert_language_select(selenium_driver, languages)

        assert_ranking_content(selenium_driver, checked_users, random_language, auth_user=auth_user)

        pagination = find_element(selenium_driver, CSS_SELECTOR_PAGINATION)
        pagination_buttons = pagination.find_elements(By.CSS_SELECTOR, ".page-link")
        active_pagination_button = find_element(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON)

        assert active_pagination_button.text == "{}\n(current)".format(current_page)

        if current_page == 1:
            assert len(pagination_buttons) == 4
            assert pagination_buttons[0].text == "1\n(current)"
            assert pagination_buttons[1].text == "…\nMore"
            assert pagination_buttons[2].text == str(number_pages)
            assert pagination_buttons[3].text == "›\nNext"
        elif current_page == number_pages:
            assert len(pagination_buttons) == 4
            assert pagination_buttons[0].text == "‹\nPrevious"
            assert pagination_buttons[1].text == "1"
            assert pagination_buttons[2].text == "…\nMore"
            assert pagination_buttons[3].text == "{}\n(current)".format(number_pages)
        elif current_page == 2:
            assert len(pagination_buttons) == 6
            assert pagination_buttons[0].text == "‹\nPrevious"
            assert pagination_buttons[1].text == "1"
            assert pagination_buttons[2].text == "2\n(current)"
            assert pagination_buttons[3].text == "…\nMore"
            assert pagination_buttons[4].text == str(number_pages)
            assert pagination_buttons[5].text == "›\nNext"
        elif current_page == number_pages - 1:
            assert len(pagination_buttons) == 6
            assert pagination_buttons[0].text == "‹\nPrevious"
            assert pagination_buttons[1].text == "1"
            assert pagination_buttons[2].text == "…\nMore"
            assert pagination_buttons[3].text == "{}\n(current)".format(number_pages-1)
            assert pagination_buttons[4].text == str(number_pages)
            assert pagination_buttons[5].text == "›\nNext"
        else:
            assert len(pagination_buttons) == 7
            assert pagination_buttons[0].text == "‹\nPrevious"
            assert pagination_buttons[1].text == "1"
            assert pagination_buttons[2].text == "…\nMore"
            assert pagination_buttons[3].text == "{}\n(current)".format(current_page)
            assert pagination_buttons[4].text == "…\nMore"
            assert pagination_buttons[5].text == str(number_pages)
            assert pagination_buttons[6].text == "›\nNext"

        go_to_next_page(selenium_driver, current_page, number_pages)

    assert_ranking_users(checked_users, users, auth_user=auth_user)
