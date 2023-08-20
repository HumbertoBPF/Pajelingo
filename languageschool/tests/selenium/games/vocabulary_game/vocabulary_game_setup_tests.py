import random

import pytest
from selenium.webdriver.common.by import By

from languageschool.models import Word
from languageschool.tests.selenium.utils import find_by_test_id, setup_vocabulary_game


@pytest.mark.django_db
def test_vocabulary_game_setup_requires_base_language(live_server, selenium_driver, words, languages):
    """
    Tests that it's required to specify a base and a target language during the setup of the vocabulary game.
    """
    random_target_language = random.choice(languages)

    setup_vocabulary_game(selenium_driver, None, random_target_language)

    error_toast = find_by_test_id(selenium_driver, "toast-error")

    assert error_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert error_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "You must set both base and target languages."


@pytest.mark.django_db
def test_vocabulary_game_setup_requires_target_language(live_server, selenium_driver, words, languages):
    """
    Tests that it's required to specify a base and a target language during the setup of the vocabulary game.
    """
    random_base_language = random.choice(languages)

    setup_vocabulary_game(selenium_driver, random_base_language, None)

    error_toast = find_by_test_id(selenium_driver, "toast-error")

    assert error_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert error_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "You must set both base and target languages."


@pytest.mark.django_db
def test_vocabulary_game_setup_base_and_target_languages_must_not_be_equal(live_server, selenium_driver, words,
                                                                           languages):
    """
    Tests that the base and target language picked must not be the same.
    """
    random_language = random.choice(languages)

    setup_vocabulary_game(selenium_driver, random_language, random_language)

    error_toast = find_by_test_id(selenium_driver, "toast-error")

    assert error_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert error_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "Base and target languages must be different."


@pytest.mark.django_db
def test_vocabulary_game_setup_form_submission(live_server, selenium_driver, words, languages):
    """
    Tests the setup of the vocabulary game, that is, that when valid base and target languages are chosen, a word in
    the target language is chosen randomly and its translation in the base language is asked.
    """
    random_base_language = random.choice(languages)
    random_target_language = random.choice(languages.exclude(id=random_base_language.id))

    setup_vocabulary_game(selenium_driver, random_base_language, random_target_language)

    word_input = find_by_test_id(selenium_driver, "word-input")
    answer_input = find_by_test_id(selenium_driver, "answer-input")

    word_name = word_input.get_attribute("placeholder")
    answer_placeholder = answer_input.get_attribute("placeholder")

    assert Word.objects.filter(
        word_name=word_name,
        language=random_target_language
    ).exists()
    assert answer_placeholder == "Provide the translation in {}".format(random_base_language.language_name)
