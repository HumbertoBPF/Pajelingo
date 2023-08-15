import random

import pytest
from selenium.webdriver.common.by import By

from languageschool.models import Word
from languageschool.tests.selenium.utils import find_element, find_by_test_id
from pajelingo.settings import FRONT_END_URL

ARTICLE_GAME_SETUP_URL = f"{FRONT_END_URL}/article-game/setup"
TEST_ID_SELECT_LANGUAGE = "select-language"
TEST_ID_ERROR_TOAST = "error-toast"
TEST_ID_START_BUTTON = "start-button"
TEST_ID_ARTICLE_INPUT = "article-input"
TEST_ID_WORD_DISABLE_INPUT = "word-disabled-input"


@pytest.mark.django_db
def test_article_game_setup_form_submission_error(live_server, selenium_driver, languages):
    """
    Tests an invalid submission of the article game setup form, that is, that after the submission an alert toast with
    an error message is displayed.
    """
    selenium_driver.get(ARTICLE_GAME_SETUP_URL)

    submit_button = find_by_test_id(selenium_driver, TEST_ID_START_BUTTON)
    submit_button.click()

    error_toast = find_by_test_id(selenium_driver, TEST_ID_ERROR_TOAST)

    assert error_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert error_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == "You must choose a language."


@pytest.mark.django_db
def test_article_game_setup_form_submission(live_server, selenium_driver, languages, words):
    """
    Tests a valid submission of the article game form, which should display a word in the selected language, an input
    for the answer and a submission button to verify the answer.
    """
    random_language = random.choice(languages).language_name

    selenium_driver.get(ARTICLE_GAME_SETUP_URL)

    form_select = find_by_test_id(selenium_driver, TEST_ID_SELECT_LANGUAGE)
    form_select.click()

    css_selector_select_option = (By.ID, random_language)
    select_option = find_element(selenium_driver, css_selector_select_option)
    select_option.click()

    submit_button = find_by_test_id(selenium_driver, TEST_ID_START_BUTTON)
    submit_button.click()

    article_input = find_by_test_id(selenium_driver, TEST_ID_ARTICLE_INPUT)
    word_disabled_input = find_by_test_id(selenium_driver, TEST_ID_WORD_DISABLE_INPUT)

    word = word_disabled_input.get_attribute("placeholder")

    assert article_input.get_attribute("placeholder") == "Article"
    assert Word.objects.filter(
        word_name=word,
        language__language_name=random_language
    ).exists()