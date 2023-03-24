import random

import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import Word
from languageschool.tests.selenium.utils import find_element, wait_attribute_to_be_non_empty, authenticate_user
from pajelingo.settings import FRONT_END_URL

def get_languages(languages):
    base_language = random.choice(languages)

    target_language_options = []

    for language in languages:
        if language.language_name != base_language.language_name:
            target_language_options.append(language)

    target_language = random.choice(target_language_options)

    return base_language, target_language


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
def test_vocabulary_game_play_form_rendering(live_server, selenium_driver, vocabulary_game, languages, words):
    """
    Tests the rendering of the form that the player sees during the gameplay. The form must contain a disabled input
    with the word to be translated, an input to receive the user's answer, and a submit button.
    """
    base_language, target_language = get_languages(languages)
    selenium_driver\
        .get(FRONT_END_URL + "/vocabulary-game/play?base_language={}&target_language={}"
             .format(base_language, target_language))

    css_selector_word_input = (By.CSS_SELECTOR, "main form #wordInput")
    css_selector_answer_input = (By.CSS_SELECTOR, "main form #answerInput")
    css_selector_submit_button = (By.CSS_SELECTOR, "main form .btn-success")

    word_input = find_element(selenium_driver, css_selector_word_input)
    answer_input = find_element(selenium_driver, css_selector_answer_input)
    submit_button = find_element(selenium_driver, css_selector_submit_button)

    word_input_placeholder = wait_attribute_to_be_non_empty(word_input, "placeholder", 10)
    answer_input_placeholder = wait_attribute_to_be_non_empty(answer_input, "placeholder", 10)

    assert Word.objects.filter(
        word_name=word_input_placeholder,
        language=target_language
    ).exists()
    assert answer_input_placeholder == "Provide the translation in {}".format(base_language.language_name)
    assert submit_button.text == "Verify answer"


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_vocabulary_game_play_non_authenticated_user(live_server, selenium_driver, vocabulary_game, languages, words,
                                                     is_correct):
    """
    Tests the feedback provided for unauthenticated users when they play the vocabulary game in case of a correct and
    of an incorrect answer.
    """
    base_language, target_language = get_languages(languages)
    selenium_driver \
        .get(FRONT_END_URL + "/vocabulary-game/play?base_language={}&target_language={}"
             .format(base_language, target_language))

    css_selector_word_input = (By.CSS_SELECTOR, "main form #wordInput")
    css_selector_answer_input = (By.CSS_SELECTOR, "main form #answerInput")
    css_selector_submit_button = (By.CSS_SELECTOR, "main form .btn-success")
    css_selector_alert = (By.CSS_SELECTOR, "main .alert-{}".format("success" if is_correct else "danger"))

    word_input = find_element(selenium_driver, css_selector_word_input)
    answer_input = find_element(selenium_driver, css_selector_answer_input)
    submit_button = find_element(selenium_driver, css_selector_submit_button)

    word_input_placeholder = wait_attribute_to_be_non_empty(word_input, "placeholder", 10)

    word = Word.objects.filter(
        word_name=word_input_placeholder,
        language=target_language
    ).first()

    answer = word.synonyms.all().filter(language=base_language).first()

    answer_input.send_keys(answer.word_name if is_correct else get_random_string(8))

    submit_button.click()

    feedback_alert = find_element(selenium_driver, css_selector_alert)

    expected_feedback = "{}\n{}: {}".format("Correct answer :)" if is_correct else "Wrong answer", word.word_name,
                                            get_correct_answer(word, base_language))

    assert feedback_alert.text == expected_feedback


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_vocabulary_game_play_authenticated_user(live_server, selenium_driver, account, vocabulary_game, languages,
                                                 words, is_correct):
    """
    Tests the feedback provided for authenticated users when they play the vocabulary game in case of a correct and of
    an incorrect answer.
    """
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)

    base_language, target_language = get_languages(languages)
    selenium_driver \
        .get(FRONT_END_URL + "/vocabulary-game/play?base_language={}&target_language={}"
             .format(base_language, target_language))

    css_selector_word_input = (By.CSS_SELECTOR, "main form #wordInput")
    css_selector_answer_input = (By.CSS_SELECTOR, "main form #answerInput")
    css_selector_submit_button = (By.CSS_SELECTOR, "main form .btn-success")
    css_selector_alert = (By.CSS_SELECTOR, "main .alert-{}".format("success" if is_correct else "danger"))

    word_input = find_element(selenium_driver, css_selector_word_input)
    answer_input = find_element(selenium_driver, css_selector_answer_input)
    submit_button = find_element(selenium_driver, css_selector_submit_button)

    word_input_placeholder = wait_attribute_to_be_non_empty(word_input, "placeholder", 10)

    word = Word.objects.filter(
        word_name=word_input_placeholder,
        language=target_language
    ).first()

    answer = word.synonyms.all().filter(language=base_language).first()

    answer_input.send_keys(answer.word_name if is_correct else get_random_string(8))

    submit_button.click()

    feedback_alert = find_element(selenium_driver, css_selector_alert)

    expected_feedback = "{}\n{}: {}{}".format("Correct answer :)" if is_correct else "Wrong answer", word.word_name,
                                              get_correct_answer(word, base_language),
                                              "\nYour score is 1" if is_correct else "")

    assert feedback_alert.text == expected_feedback
