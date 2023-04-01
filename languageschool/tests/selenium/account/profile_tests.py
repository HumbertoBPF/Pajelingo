import random

import pytest
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import find_element, authenticate_user
from pajelingo.settings import FRONT_END_URL

PROFILE_URL = FRONT_END_URL + "/profile"
CSS_SELECTOR_FORM_INPUTS = (By.CSS_SELECTOR, "main form .form-control")
CSS_SELECTOR_LOGIN_FORM_SUBMIT_BUTTON = (By.CSS_SELECTOR, "main form .btn-success")
CSS_SELECTOR_UPDATE_ACCOUNT_FORM_SUBMIT_BUTTON = (By.CSS_SELECTOR, "main form .btn-info")
CSS_SELECTOR_UPDATE_PICTURE_BUTTON = (By.CSS_SELECTOR, "main .col-lg-3 .btn-info")
CSS_SELECTOR_EDIT_ACCOUNT_BUTTON = (By.CSS_SELECTOR, "main section .col-lg-9 .btn-info")
CSS_SELECTOR_DELETE_ACCOUNT_BUTTON = (By.CSS_SELECTOR, "main section .col-lg-9 .btn-danger")
CSS_SELECTOR_CREDENTIALS = (By.CSS_SELECTOR, "main section .col-lg-9 p")
CSS_SELECTOR_DIALOG_TILE = (By.CSS_SELECTOR, "body .modal .modal-header")
CSS_SELECTOR_DIALOG_BODY = (By.CSS_SELECTOR, "body .modal .modal-body")
CSS_SELECTOR_DIALOG_CANCEL_BUTTON = (By.CSS_SELECTOR, "body .modal .modal-footer .btn-secondary")
CSS_SELECTOR_DIALOG_DANGER_BUTTON = (By.CSS_SELECTOR, "body .modal .modal-footer .btn-danger")
CSS_SELECTOR_DIALOG_SUCCESS_BUTTON = (By.CSS_SELECTOR, "body .modal .modal-footer .btn-success")
CSS_SELECTOR_SELECT_LANGUAGE = (By.CSS_SELECTOR, "main section .form-select")
CSS_SELECTOR_SCORES_TABLE = (By.CSS_SELECTOR, "main section .table")


def assert_is_login_page(selenium_driver):
    find_element(selenium_driver, CSS_SELECTOR_FORM_INPUTS)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_LOGIN_FORM_SUBMIT_BUTTON)

    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUTS[0], CSS_SELECTOR_FORM_INPUTS[1])

    assert len(form_inputs) == 2
    assert submit_button.text == "Sign in"


def assert_is_update_account_page(selenium_driver):
    find_element(selenium_driver, CSS_SELECTOR_FORM_INPUTS)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_UPDATE_ACCOUNT_FORM_SUBMIT_BUTTON)

    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUTS[0], CSS_SELECTOR_FORM_INPUTS[1])

    assert len(form_inputs) == 4
    assert submit_button.text == "Update"


def assert_is_profile_page(selenium_driver, user):
    find_element(selenium_driver, CSS_SELECTOR_CREDENTIALS)
    credentials = selenium_driver.find_elements(CSS_SELECTOR_CREDENTIALS[0], CSS_SELECTOR_CREDENTIALS[1])
    update_picture_button = find_element(selenium_driver, CSS_SELECTOR_UPDATE_PICTURE_BUTTON)
    edit_account_button = find_element(selenium_driver, CSS_SELECTOR_EDIT_ACCOUNT_BUTTON)
    delete_account_button = find_element(selenium_driver, CSS_SELECTOR_DELETE_ACCOUNT_BUTTON)

    assert len(credentials) == 2
    assert credentials[0].text == "Username: {}".format(user.username)
    assert credentials[1].text == "Email: {}".format(user.email)
    assert update_picture_button.text == "Update picture"
    assert edit_account_button.text == "Edit account"
    assert delete_account_button.text == "Delete account"


def assert_select_language_options(select_language, languages_expected):
    select_language_options = select_language.find_elements(By.CSS_SELECTOR, "option")

    assert len(select_language_options) == len(languages_expected)
    # Check that for each language expected, there is a corresponding select option
    language_dict = {}

    for language in languages_expected:
        language_dict[language.language_name] = True

    for language_option in select_language_options:
        del language_dict[language_option.text]

    assert len(language_dict) == 0


def select_option_from_select_language(select_language, language):
    select_language_options = select_language.find_elements(By.CSS_SELECTOR, "option")

    for language_option in select_language_options:
        if language_option.text == language.language_name:
            language_option.click()
            break


def test_profile_requires_authentication(live_server, selenium_driver):
    selenium_driver.get(PROFILE_URL)
    assert_is_login_page(selenium_driver)


def test_profile(live_server, selenium_driver, account):
    user, password = account()[0]

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    assert_is_profile_page(selenium_driver, user)


def test_profile_delete_account(live_server, selenium_driver, account):
    user, password = account()[0]

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    delete_account_button = find_element(selenium_driver, CSS_SELECTOR_DELETE_ACCOUNT_BUTTON)
    delete_account_button.click()

    delete_dialog_title = find_element(selenium_driver, CSS_SELECTOR_DIALOG_TILE)
    delete_dialog_body = find_element(selenium_driver, CSS_SELECTOR_DIALOG_BODY)
    delete_dialog_cancel_button = find_element(selenium_driver, CSS_SELECTOR_DIALOG_CANCEL_BUTTON)
    delete_dialog_delete_button = find_element(selenium_driver, CSS_SELECTOR_DIALOG_DANGER_BUTTON)

    assert delete_dialog_title.text == "Are you sure?"
    assert delete_dialog_body.text == "Are you sure that you want to delete your profile? All information such as " \
                                      "scores in the games is going to be permanently lost!"
    assert delete_dialog_cancel_button.text == "Cancel"
    assert delete_dialog_delete_button.text == "Yes, I want to delete my profile"

    delete_dialog_delete_button.click()

    assert_is_login_page(selenium_driver)
    assert not User.objects.filter(
        username=user.username,
        email=user.email
    ).exists()


def test_profile_update_account_redirect(live_server, selenium_driver, account):
    user, password = account()[0]

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    edit_account_button = find_element(selenium_driver, CSS_SELECTOR_EDIT_ACCOUNT_BUTTON)
    edit_account_button.click()

    assert_is_update_account_page(selenium_driver)


def test_profile_update_profile_picture(live_server, selenium_driver, account):
    user, password = account()[0]

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    update_picture_button = find_element(selenium_driver, CSS_SELECTOR_UPDATE_PICTURE_BUTTON)
    update_picture_button.click()

    profile_picture_dialog_title = find_element(selenium_driver, CSS_SELECTOR_DIALOG_TILE)
    profile_picture_dialog_cancel_button = find_element(selenium_driver, CSS_SELECTOR_DIALOG_CANCEL_BUTTON)
    profile_picture_dialog_success_button = find_element(selenium_driver, CSS_SELECTOR_DIALOG_SUCCESS_BUTTON)

    assert profile_picture_dialog_title.text == "Update profile picture"
    assert profile_picture_dialog_cancel_button.text == "Cancel"
    assert profile_picture_dialog_success_button.text == "Update"

    profile_picture_dialog_success_button.click()

    assert_is_profile_page(selenium_driver, user)


@pytest.mark.parametrize(
    "filename", [
        "C:\\Users\\Humberto\\Desktop\\Humberto\\Study\\WebDev\\Pajelingo\\requirements.txt",
        "C:\\Users\\Humberto\\Desktop\\Humberto\\Study\\WebDev\\Pajelingo\\languageschool\\views.py"
    ]
)
def test_profile_update_profile_picture_error_file_format(live_server, selenium_driver, account, filename):
    user, password = account()[0]

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    update_picture_button = find_element(selenium_driver, CSS_SELECTOR_UPDATE_PICTURE_BUTTON)
    update_picture_button.click()

    profile_picture_dialog_title = find_element(selenium_driver, CSS_SELECTOR_DIALOG_TILE)
    profile_picture_dialog_body = find_element(selenium_driver, CSS_SELECTOR_DIALOG_BODY)
    profile_picture_dialog_cancel_button = find_element(selenium_driver, CSS_SELECTOR_DIALOG_CANCEL_BUTTON)
    profile_picture_dialog_success_button = find_element(selenium_driver, CSS_SELECTOR_DIALOG_SUCCESS_BUTTON)

    assert profile_picture_dialog_title.text == "Update profile picture"
    assert profile_picture_dialog_cancel_button.text == "Cancel"
    assert profile_picture_dialog_success_button.text == "Update"

    file_input = profile_picture_dialog_body.find_element(By.CSS_SELECTOR, "input")
    file_input.send_keys(filename)

    profile_picture_dialog_success_button.click()


def test_profile_user_scores(live_server, selenium_driver, account, languages, score, games):
    user, password = account()[0]
    random_language = random.choice(languages)
    scores = score([user], games, languages)

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    select_language = find_element(selenium_driver, CSS_SELECTOR_SELECT_LANGUAGE)
    scores_table = find_element(selenium_driver, CSS_SELECTOR_SCORES_TABLE)

    assert_select_language_options(select_language, languages)

    select_option_from_select_language(select_language, random_language)

    scores_table_headers = scores_table.find_elements(By.CSS_SELECTOR, "thead tr th")
    score_table_records = scores_table.find_elements(By.CSS_SELECTOR, "tbody tr")

    assert scores_table_headers[0].text == "Game"
    assert scores_table_headers[1].text == "Score"

    expected_scores = scores.filter(user=user, language=random_language)

    assert len(score_table_records) == len(expected_scores)

    for score_table_record in score_table_records:
        columns = score_table_record.find_elements(By.CSS_SELECTOR, "td")

        game_name = columns[0].text
        score = columns[1].text

        assert expected_scores.filter(
            game__game_name=game_name,
            score=score
        ).exists()
