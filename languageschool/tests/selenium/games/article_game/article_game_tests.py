import random

import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import Word
from languageschool.tests.selenium.utils import find_element, wait_attribute_to_be_non_empty, authenticate_user
from pajelingo.settings import FRONT_END_URL

CSS_SELECTOR_ARTICLE_INPUT = (By.CSS_SELECTOR, "main form #articleInput")
CSS_SELECTOR_WORD_INPUT = (By.CSS_SELECTOR, "main form #wordInput")
CSS_SELECTOR_VERIFY_ANSWER = (By.CSS_SELECTOR, "main form .btn-success")


def submit_answer(selenium_driver, answer):
    article_input = find_element(selenium_driver, CSS_SELECTOR_ARTICLE_INPUT)
    verify_answer_button = find_element(selenium_driver, CSS_SELECTOR_VERIFY_ANSWER)

    article_input.send_keys(answer)
    verify_answer_button.click()


@pytest.mark.django_db
def test_article_game_play_form_rendering(live_server, selenium_driver, article_game, languages, words):
    """
    Tests the presence of the HTML elements concerning the page when users can play the article game.
    """
    random_language = random.choice(languages)
    selenium_driver.get(FRONT_END_URL + "/article-game/play?language={}".format(random_language.language_name))

    article_input = find_element(selenium_driver, CSS_SELECTOR_ARTICLE_INPUT)
    word_input = find_element(selenium_driver, CSS_SELECTOR_WORD_INPUT)
    verify_answer_button = find_element(selenium_driver, CSS_SELECTOR_VERIFY_ANSWER)

    article_input_placeholder = wait_attribute_to_be_non_empty(article_input, "placeholder", 10)
    word_input_placeholder = wait_attribute_to_be_non_empty(word_input, "placeholder", 10)

    assert article_input_placeholder == "Article"
    assert Word.objects.filter(
        word_name=word_input_placeholder,
        language__language_name=random_language.language_name
    ).exists()
    assert verify_answer_button.text == "Verify answer"


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_article_game_play_non_authenticated_user(live_server, selenium_driver,
                                                  article_game, languages, words, is_correct):
    """
    Tests the feedback provided for unauthenticated users when they play the article game in case of a correct and of a
    wrong answer.
    """
    random_language = random.choice(languages)
    selenium_driver.get(FRONT_END_URL + "/article-game/play?language={}".format(random_language.language_name))

    css_selector_alert = (By.CSS_SELECTOR, "main .alert-{}".format("success" if is_correct else "danger"))

    word_input = find_element(selenium_driver, CSS_SELECTOR_WORD_INPUT)

    word_input_placeholder = wait_attribute_to_be_non_empty(word_input, "placeholder", 10)

    word = Word.objects.filter(
        word_name=word_input_placeholder,
        language__language_name=random_language.language_name
    ).first()

    answer = word.article.article_name if is_correct else get_random_string(5)

    submit_answer(selenium_driver, answer)

    feedback_alert = find_element(selenium_driver, css_selector_alert)

    expected_feedback = "{}\n{}".format("Correct answer :)" if is_correct else "Wrong answer", word)

    assert feedback_alert.text == expected_feedback


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_article_game_play_authenticated_user(live_server, selenium_driver,
                                              article_game, account, languages, words, is_correct):
    """
    Tests the feedback provided for authenticated users when they play the article game in case of a correct and of a
    wrong answer.
    """
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)

    random_language = random.choice(languages)
    selenium_driver.get(FRONT_END_URL + "/article-game/play?language={}".format(random_language.language_name))

    css_selector_alert = (By.CSS_SELECTOR, "main .alert-{}".format("success" if is_correct else "danger"))

    word_input = find_element(selenium_driver, CSS_SELECTOR_WORD_INPUT)

    word_input_placeholder = wait_attribute_to_be_non_empty(word_input, "placeholder", 10)

    word = Word.objects.filter(
        word_name=word_input_placeholder,
        language__language_name=random_language.language_name
    ).first()

    answer = word.article.article_name if is_correct else get_random_string(5)

    submit_answer(selenium_driver, answer)

    feedback_alert = find_element(selenium_driver, css_selector_alert)

    expected_feedback = "{}\n{}{}".format(
        "Correct answer :)" if is_correct else "Wrong answer", word, "\nYour score is 1" if is_correct else "")

    assert feedback_alert.text == expected_feedback
