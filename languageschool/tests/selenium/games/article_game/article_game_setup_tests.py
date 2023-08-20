import random

import pytest
from selenium.webdriver.common.by import By

from languageschool.models import Word
from languageschool.tests.selenium.utils import find_element, find_by_test_id, setup_article_game
from pajelingo.settings import FRONT_END_URL


@pytest.mark.django_db
def test_article_game_setup_form_submission_error(live_server, selenium_driver, languages):
    """
    Tests an invalid submission of the article game setup form, that is, that after the submission an alert toast with
    an error message is displayed.
    """
    setup_article_game(selenium_driver, None)

    error_toast = find_by_test_id(selenium_driver, "error-toast")

    assert error_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert error_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == "You must choose a language."


@pytest.mark.django_db
def test_article_game_setup_form_submission(live_server, selenium_driver, languages, words):
    """
    Tests a valid submission of the article game form, which should display a word in the selected language, an input
    for the answer and a submission button to verify the answer.
    """
    random_language = random.choice(languages)

    setup_article_game(selenium_driver, random_language)

    article_input = find_by_test_id(selenium_driver, "article-input")
    word_disabled_input = find_by_test_id(selenium_driver, "word-disabled-input")

    word = word_disabled_input.get_attribute("placeholder")

    assert article_input.get_attribute("placeholder") == "Article"
    assert Word.objects.filter(
        word_name=word,
        language__language_name=random_language
    ).exists()