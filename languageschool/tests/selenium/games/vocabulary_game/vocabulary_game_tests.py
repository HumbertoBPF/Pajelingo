import random

import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import Word, Badge, Score
from languageschool.tests.selenium.utils import wait_attribute_to_be_non_empty, authenticate_user, find_by_test_id
from languageschool.tests.utils import achieve_explorer_badge
from pajelingo.settings import FRONT_END_URL


def get_correct_answer(word_to_translate, base_language):
    correct_translation = ""

    for synonym in word_to_translate.synonyms.all():
        if synonym.language == base_language:
            # Getting the correct answer
            if len(correct_translation) != 0:
                correct_translation += ", "
            correct_translation += synonym.word_name

    return correct_translation


@pytest.mark.django_db
def test_vocabulary_game_correct_answer_non_authenticated_user(live_server, selenium_driver, languages, words):
    """
    Tests the feedback provided for unauthenticated users when they play the vocabulary game in case of a correct and
    of an incorrect answer.
    """
    base_language = random.choice(languages)
    target_language = random.choice(languages.exclude(id=base_language.id))

    selenium_driver \
        .get(f"{FRONT_END_URL}/vocabulary-game/play?base_language={base_language}&target_language={target_language}")

    word_input = find_by_test_id(selenium_driver, "word-input")

    word_input_placeholder = wait_attribute_to_be_non_empty(word_input, "placeholder", 10)

    word = Word.objects.filter(
        word_name=word_input_placeholder,
        language=target_language
    ).first()

    synonym = word.synonyms.filter(language=base_language).first()
    answer = synonym.word_name

    answer_input = find_by_test_id(selenium_driver, "answer-input")
    answer_input.send_keys(answer)

    submit_button = find_by_test_id(selenium_driver, "submit-answer-button")
    submit_button.click()

    feedback_alert = find_by_test_id(selenium_driver, "feedback-alert")

    assert feedback_alert.text == f"Correct answer :)\n{word.word_name}: {get_correct_answer(word, base_language)}"


@pytest.mark.django_db
def test_vocabulary_game_incorrect_answer_non_authenticated_user(live_server, selenium_driver, languages, words):
    """
    Tests the feedback provided for unauthenticated users when they play the vocabulary game in case of a correct and
    of an incorrect answer.
    """
    base_language = random.choice(languages)
    target_language = random.choice(languages.exclude(id=base_language.id))

    selenium_driver \
        .get(f"{FRONT_END_URL}/vocabulary-game/play?base_language={base_language}&target_language={target_language}")

    word_input = find_by_test_id(selenium_driver, "word-input")

    word_input_placeholder = wait_attribute_to_be_non_empty(word_input, "placeholder", 10)

    word = Word.objects.filter(
        word_name=word_input_placeholder,
        language=target_language
    ).first()

    answer = get_random_string(8)

    answer_input = find_by_test_id(selenium_driver, "answer-input")
    answer_input.send_keys(answer)

    submit_button = find_by_test_id(selenium_driver, "submit-answer-button")
    submit_button.click()

    feedback_alert = find_by_test_id(selenium_driver, "feedback-alert")

    assert feedback_alert.text == f"Wrong answer\n{word.word_name}: {get_correct_answer(word, base_language)}"


@pytest.mark.django_db
def test_vocabulary_game_correct_answer_authenticated_user(live_server, selenium_driver, account, languages, words):
    """
    Tests the feedback provided for authenticated users when they play the vocabulary game in case of a correct and of
    an incorrect answer.
    """
    user, password = account()[0]
    achieve_explorer_badge(user)
    authenticate_user(selenium_driver, user.username, password)

    base_language = random.choice(languages)
    target_language = random.choice(languages.exclude(id=base_language.id))

    initial_score = Score.objects.filter(
        user=user,
        language=target_language,
        game__id=1
    ).first()
    expected_score = 1 if (initial_score is None) else initial_score.score + 1

    selenium_driver \
        .get(f"{FRONT_END_URL}/vocabulary-game/play?base_language={base_language}&target_language={target_language}")

    word_input = find_by_test_id(selenium_driver, "word-input")

    word_input_placeholder = wait_attribute_to_be_non_empty(word_input, "placeholder", 10)

    word = Word.objects.filter(
        word_name=word_input_placeholder,
        language=target_language
    ).first()

    synonym = word.synonyms.filter(language=base_language).first()
    answer = synonym.word_name

    answer_input = find_by_test_id(selenium_driver, "answer-input")
    answer_input.send_keys(answer)

    submit_button = find_by_test_id(selenium_driver, "submit-answer-button")
    submit_button.click()

    feedback_alert = find_by_test_id(selenium_driver, "feedback-alert")

    correct_answer = get_correct_answer(word, base_language)

    assert (feedback_alert.text ==
            f"Correct answer :)\n{word.word_name}: {correct_answer}\nYour score is {expected_score}")

    badge_explorer = Badge.objects.get(id=1)

    badge_notification = find_by_test_id(selenium_driver, f"notification-badge-{badge_explorer.id}")

    badge_notification_header = badge_notification.find_element(By.CSS_SELECTOR, ".toast-header")
    badge_notification_body = badge_notification.find_element(By.CSS_SELECTOR, ".toast-body")

    assert badge_notification_header.text == f"New achievement: {badge_explorer.name}"
    assert badge_notification_body.text == badge_explorer.description


@pytest.mark.django_db
def test_vocabulary_game_incorrect_answer_authenticated_user(live_server, selenium_driver, account, languages, words):
    """
    Tests the feedback provided for authenticated users when they play the vocabulary game in case of a correct and of
    an incorrect answer.
    """
    user, password = account()[0]
    achieve_explorer_badge(user)
    authenticate_user(selenium_driver, user.username, password)

    base_language = random.choice(languages)
    target_language = random.choice(languages.exclude(id=base_language.id))

    selenium_driver \
        .get(f"{FRONT_END_URL}/vocabulary-game/play?base_language={base_language}&target_language={target_language}")

    word_input = find_by_test_id(selenium_driver, "word-input")

    word_input_placeholder = wait_attribute_to_be_non_empty(word_input, "placeholder", 10)

    word = Word.objects.filter(
        word_name=word_input_placeholder,
        language=target_language
    ).first()

    answer = get_random_string(8)

    answer_input = find_by_test_id(selenium_driver, "answer-input")
    answer_input.send_keys(answer)

    submit_button = find_by_test_id(selenium_driver, "submit-answer-button")
    submit_button.click()

    feedback_alert = find_by_test_id(selenium_driver, "feedback-alert")

    correct_answer = get_correct_answer(word, base_language)

    assert feedback_alert.text == f"Wrong answer\n{word.word_name}: {correct_answer}"
