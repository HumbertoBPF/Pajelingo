import random

import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import Word, Badge, Score
from languageschool.tests.selenium.utils import wait_attribute_to_be_non_empty, authenticate_user, find_by_test_id
from languageschool.tests.utils import achieve_explorer_badge
from pajelingo.settings import FRONT_END_URL


@pytest.mark.django_db
def test_article_game_correct_answer_non_authenticated_user(live_server, selenium_driver, languages, words):
    """
    Tests the feedback provided for unauthenticated users when they play the article game in case of a correct and of a
    wrong answer.
    """
    random_language = random.choice(languages)
    selenium_driver.get(f"{FRONT_END_URL}/article-game/play?language={random_language.language_name}")

    word_input = find_by_test_id(selenium_driver, "word-disabled-input")

    word_input_placeholder = wait_attribute_to_be_non_empty(word_input, "placeholder", 10)

    word = Word.objects.filter(
        word_name=word_input_placeholder,
        language__language_name=random_language.language_name
    ).first()

    answer = word.article.article_name

    article_input = find_by_test_id(selenium_driver, "article-input")
    article_input.send_keys(answer)

    verify_answer_button = find_by_test_id(selenium_driver, "submit-answer-button")
    verify_answer_button.click()

    feedback_alert = find_by_test_id(selenium_driver, "feedback-alert")

    assert feedback_alert.text == f"Correct answer :)\n{word}"


@pytest.mark.django_db
def test_article_game_incorrect_answer_non_authenticated_user(live_server, selenium_driver, languages, words):
    """
    Tests the feedback provided for unauthenticated users when they play the article game in case of a correct and of a
    wrong answer.
    """
    random_language = random.choice(languages)
    selenium_driver.get(f"{FRONT_END_URL}/article-game/play?language={random_language.language_name}")

    word_input = find_by_test_id(selenium_driver, "word-disabled-input")

    word_input_placeholder = wait_attribute_to_be_non_empty(word_input, "placeholder", 10)

    word = Word.objects.filter(
        word_name=word_input_placeholder,
        language__language_name=random_language.language_name
    ).first()

    answer = get_random_string(5)

    article_input = find_by_test_id(selenium_driver, "article-input")
    article_input.send_keys(answer)

    verify_answer_button = find_by_test_id(selenium_driver, "submit-answer-button")
    verify_answer_button.click()

    feedback_alert = find_by_test_id(selenium_driver, "feedback-alert")

    assert feedback_alert.text == f"Wrong answer\n{word}"


@pytest.mark.django_db
def test_article_game_correct_answer_authenticated_user(live_server, selenium_driver, account, languages, words):
    """
    Tests the feedback provided for authenticated users when they play the article game in case of a correct and of a
    wrong answer.
    """
    user, password = account()[0]
    achieve_explorer_badge(user)
    authenticate_user(selenium_driver, user.username, password)

    random_language = random.choice(languages)

    initial_score = Score.objects.filter(
        user=user,
        language=random_language,
        game__id=2
    ).first()
    expected_score = 1 if (initial_score is None) else initial_score.score + 1

    selenium_driver.get(f"{FRONT_END_URL}/article-game/play?language={random_language.language_name}")

    word_input = find_by_test_id(selenium_driver, "word-disabled-input")

    word_input_placeholder = wait_attribute_to_be_non_empty(word_input, "placeholder", 10)

    word = Word.objects.filter(
        word_name=word_input_placeholder,
        language__language_name=random_language.language_name
    ).first()

    answer = word.article.article_name

    article_input = find_by_test_id(selenium_driver, "article-input")
    article_input.send_keys(answer)

    verify_answer_button = find_by_test_id(selenium_driver, "submit-answer-button")
    verify_answer_button.click()

    feedback_alert = find_by_test_id(selenium_driver, "feedback-alert")

    assert feedback_alert.text == f"Correct answer :)\n{word}\nYour score is {expected_score}"

    badge_explorer = Badge.objects.get(id=1)

    badge_notification = find_by_test_id(selenium_driver, f"notification-badge-{badge_explorer.id}")

    badge_notification_header = badge_notification.find_element(By.CSS_SELECTOR, ".toast-header")
    badge_notification_body = badge_notification.find_element(By.CSS_SELECTOR, ".toast-body")

    assert badge_notification_header.text == f"New achievement: {badge_explorer.name}"
    assert badge_notification_body.text == badge_explorer.description


@pytest.mark.django_db
def test_article_game_incorrect_answer_authenticated_user(live_server, selenium_driver, account, languages, words):
    """
    Tests the feedback provided for authenticated users when they play the article game in case of a correct and of a
    wrong answer.
    """
    user, password = account()[0]
    achieve_explorer_badge(user)
    authenticate_user(selenium_driver, user.username, password)

    random_language = random.choice(languages)

    selenium_driver.get(f"{FRONT_END_URL}/article-game/play?language={random_language.language_name}")

    word_input = find_by_test_id(selenium_driver, "word-disabled-input")

    word_input_placeholder = wait_attribute_to_be_non_empty(word_input, "placeholder", 10)

    word = Word.objects.filter(
        word_name=word_input_placeholder,
        language__language_name=random_language.language_name
    ).first()

    answer = get_random_string(5)

    article_input = find_by_test_id(selenium_driver, "article-input")
    article_input.send_keys(answer)

    verify_answer_button = find_by_test_id(selenium_driver, "submit-answer-button")
    verify_answer_button.click()

    feedback_alert = find_by_test_id(selenium_driver, "feedback-alert")

    assert feedback_alert.text == f"Wrong answer\n{word}"
