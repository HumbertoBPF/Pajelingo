import random

import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import Word, Badge, Score
from languageschool.tests.selenium.utils import find_element, wait_attribute_to_be_non_empty, authenticate_user
from languageschool.tests.utils import achieve_explorer_badge
from pajelingo.settings import FRONT_END_URL

CSS_SELECTOR_ARTICLE_INPUT = (By.CSS_SELECTOR, "main form #articleInput")
CSS_SELECTOR_WORD_INPUT = (By.CSS_SELECTOR, "main form #wordInput")
CSS_SELECTOR_VERIFY_ANSWER = (By.CSS_SELECTOR, "main form .btn-success")
CSS_SELECTOR_BADGE_NOTIFICATION_HEADER = (By.CSS_SELECTOR, "main .toast-container .toast-header")
CSS_SELECTOR_BADGE_NOTIFICATION_BODY = (By.CSS_SELECTOR, "main .toast-container .toast-body")


def submit_answer(selenium_driver, answer):
    article_input = find_element(selenium_driver, CSS_SELECTOR_ARTICLE_INPUT)
    verify_answer_button = find_element(selenium_driver, CSS_SELECTOR_VERIFY_ANSWER)

    article_input.send_keys(answer)
    verify_answer_button.click()


@pytest.mark.django_db
def test_article_game_play_form_rendering(live_server, selenium_driver, languages, words):
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
def test_article_game_play_non_authenticated_user(live_server, selenium_driver, languages, words, is_correct):
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

    if is_correct:
        expected_feedback = f"Correct answer :)\n{word}"
    else:
        expected_feedback = f"Wrong answer\n{word}"

    assert feedback_alert.text == expected_feedback


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_article_game_play_authenticated_user(live_server, selenium_driver, account, languages, words, is_correct):
    """
    Tests the feedback provided for authenticated users when they play the article game in case of a correct and of a
    wrong answer.
    """
    user, password = account()[0]
    achieve_explorer_badge(user)
    authenticate_user(selenium_driver, user.username, password)

    article_game_id = 2
    random_language = random.choice(languages)

    initial_score = Score.objects.filter(
        user=user,
        language=random_language,
        game__id=article_game_id
    ).first()
    expected_score = 1 if (initial_score is None) else initial_score.score + 1

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

    if is_correct:
        expected_feedback = f"Correct answer :)\n{word}\nYour score is {expected_score}"
    else:
        expected_feedback = f"Wrong answer\n{word}"

    assert feedback_alert.text == expected_feedback

    if is_correct:
        badge_explorer = Badge.objects.get(id=1)

        badge_notification_header = find_element(selenium_driver, CSS_SELECTOR_BADGE_NOTIFICATION_HEADER)
        badge_notification_body = find_element(selenium_driver, CSS_SELECTOR_BADGE_NOTIFICATION_BODY)

        assert badge_notification_header.text == f"New achievement: {badge_explorer.name}"
        assert badge_notification_body.text == badge_explorer.description
