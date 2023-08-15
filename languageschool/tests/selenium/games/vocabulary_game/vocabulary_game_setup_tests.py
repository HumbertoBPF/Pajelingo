import random

import pytest
from selenium.webdriver.common.by import By

from languageschool.models import Word
from languageschool.tests.selenium.utils import find_element, find_by_test_id
from pajelingo.settings import FRONT_END_URL

VOCABULARY_GAME_SETUP_URL = f"{FRONT_END_URL}/vocabulary-game/setup"
TEST_ID_SELECT_BASE_LANGUAGE = "select-base-language"
TEST_ID_SELECT_TARGET_LANGUAGE = "select-target-language"
TEST_ID_ERROR_TOAST = "toast-error"
TEST_ID_START_BUTTON = "start-button"
TEST_ID_WORD_INPUT = "word-input"
TEST_ID_ANSWER_INPUT = "answer-input"


@pytest.mark.django_db
def test_vocabulary_game_setup_requires_base_language(live_server, selenium_driver, words, languages):
    """
    Tests that it's required to specify a base and a target language during the setup of the vocabulary game.
    """
    random_target_language = random.choice(languages)

    selenium_driver.get(VOCABULARY_GAME_SETUP_URL)

    css_selector_target_language_option = (By.ID, random_target_language.language_name)

    select_target_language = find_by_test_id(selenium_driver, TEST_ID_SELECT_TARGET_LANGUAGE)
    select_target_language.click()

    find_element(selenium_driver, css_selector_target_language_option)
    target_language_option = select_target_language\
        .find_element(css_selector_target_language_option[0], css_selector_target_language_option[1])
    target_language_option.click()

    submit_button = find_by_test_id(selenium_driver, TEST_ID_START_BUTTON)
    submit_button.click()

    error_toast = find_by_test_id(selenium_driver, TEST_ID_ERROR_TOAST)

    assert error_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert error_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "You must set both base and target languages."


@pytest.mark.django_db
def test_vocabulary_game_setup_requires_target_language(live_server, selenium_driver, words, languages):
    """
    Tests that it's required to specify a base and a target language during the setup of the vocabulary game.
    """
    random_base_language = random.choice(languages)

    selenium_driver.get(VOCABULARY_GAME_SETUP_URL)

    css_selector_base_language_option = (By.ID, random_base_language.language_name)

    select_base_language = find_by_test_id(selenium_driver, TEST_ID_SELECT_BASE_LANGUAGE)
    select_base_language.click()

    find_element(selenium_driver, css_selector_base_language_option)
    base_language_option = select_base_language \
        .find_element(css_selector_base_language_option[0], css_selector_base_language_option[1])
    base_language_option.click()

    submit_button = find_by_test_id(selenium_driver, TEST_ID_START_BUTTON)
    submit_button.click()

    error_toast = find_by_test_id(selenium_driver, TEST_ID_ERROR_TOAST)

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

    selenium_driver.get(VOCABULARY_GAME_SETUP_URL)

    css_selector_random_language_option = (By.ID, random_language.language_name)

    # Selecting the base language
    select_base_language = find_by_test_id(selenium_driver, TEST_ID_SELECT_BASE_LANGUAGE)
    select_base_language.click()

    find_element(selenium_driver, css_selector_random_language_option)
    base_language_option = select_base_language\
        .find_element(css_selector_random_language_option[0], css_selector_random_language_option[1])
    base_language_option.click()

    # Selecting the target language
    select_target_language = find_by_test_id(selenium_driver, TEST_ID_SELECT_TARGET_LANGUAGE)
    select_target_language.click()

    find_element(selenium_driver, css_selector_random_language_option)
    target_language_option = select_target_language \
        .find_element(css_selector_random_language_option[0], css_selector_random_language_option[1])
    target_language_option.click()

    submit_button = find_by_test_id(selenium_driver, TEST_ID_START_BUTTON)
    submit_button.click()

    error_toast = find_by_test_id(selenium_driver, TEST_ID_ERROR_TOAST)

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

    selenium_driver.get(VOCABULARY_GAME_SETUP_URL)

    # Selecting the base language
    select_base_language = find_by_test_id(selenium_driver, TEST_ID_SELECT_BASE_LANGUAGE)
    select_base_language.click()

    css_selector_base_language_option = (By.ID, random_base_language)
    find_element(selenium_driver, css_selector_base_language_option)

    base_language_option = select_base_language\
        .find_element(css_selector_base_language_option[0], css_selector_base_language_option[1])
    base_language_option.click()

    # Selecting the target language
    select_target_language = find_by_test_id(selenium_driver, TEST_ID_SELECT_TARGET_LANGUAGE)
    select_target_language.click()

    css_selector_target_language_option = (By.ID, random_target_language.language_name)
    find_element(selenium_driver, css_selector_target_language_option)

    target_language_option = select_target_language\
        .find_element(css_selector_target_language_option[0], css_selector_target_language_option[1])
    target_language_option.click()

    submit_button = find_by_test_id(selenium_driver, TEST_ID_START_BUTTON)
    submit_button.click()

    word_input = find_by_test_id(selenium_driver, TEST_ID_WORD_INPUT)
    answer_input = find_by_test_id(selenium_driver, TEST_ID_ANSWER_INPUT)

    word_name = word_input.get_attribute("placeholder")
    answer_placeholder = answer_input.get_attribute("placeholder")

    assert Word.objects.filter(
        word_name=word_name,
        language=random_target_language
    ).exists()
    assert answer_placeholder == "Provide the translation in {}".format(random_base_language.language_name)
