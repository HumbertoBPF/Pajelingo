import random

import pytest
from selenium.webdriver.common.by import By

from languageschool.models import Word
from languageschool.tests.selenium.utils import find_element
from pajelingo.settings import FRONT_END_URL


def assert_languages(language_options, languages, default_option):
    """
    Asserts the presence of all the specified languages and of the default option in the option list of a select input.

    :param language_options: Selenium list of element consisting of option tags
    :param languages: Language model instances that must be present among the select options
    :type languages: list
    :param default_option: a default option that must be present among the select options as well
    :type default_option: str
    """
    expected_options = {default_option: True}

    for language in languages:
        expected_options[language.language_name] = True

    assert len(language_options) == len(languages) + 1
    # Check if all the expected options are present among the select options
    for language_option in language_options:
        del expected_options[language_option.text]

    assert len(expected_options) == 0


@pytest.mark.django_db
def test_vocabulary_game_setup_form_rendering(live_server, selenium_driver, languages):
    """
    Tests the setup form rendering, that is if a submit button, and select inputs for the base and target language are
    displayed with all the language choices available.
    """
    selenium_driver.get(FRONT_END_URL + "/vocabulary-game/setup")

    css_selector_form_selects = (By.CSS_SELECTOR, "main form .form-select")
    css_selector_select_options = (By.ID, "{}Item".format(languages[0].language_name))
    css_selector_submit_button = (By.CSS_SELECTOR, "main form .btn-success")

    form_selects = selenium_driver.find_elements(css_selector_form_selects[0], css_selector_form_selects[1])
    submit_button = find_element(selenium_driver, css_selector_submit_button)

    assert submit_button.text == "Start"
    # Check target language options
    form_selects[1].click()
    find_element(selenium_driver, css_selector_select_options)
    base_languages = form_selects[1].find_elements(By.CSS_SELECTOR, "option")
    assert_languages(base_languages, languages, default_option="Choose a target language")
    # Check base language options
    form_selects[0].click()
    find_element(selenium_driver, css_selector_select_options)
    base_languages = form_selects[0].find_elements(By.CSS_SELECTOR, "option")
    assert_languages(base_languages, languages, default_option="Choose a base language")


@pytest.mark.parametrize(
    "choose_base_language, choose_target_language", [
        (True, False),
        (False, True),
        (False, False)
    ]
)
@pytest.mark.django_db
def test_vocabulary_game_setup_base_and_target_languages_are_required(live_server, selenium_driver, words, languages,
                                                                      choose_base_language, choose_target_language):
    """
    Tests that it's required to specify a base and a target language during the setup of the vocabulary game.
    """
    random_base_language = random.choice(languages)
    random_target_language = random.choice(languages.exclude(id=random_base_language.id))

    selenium_driver.get(FRONT_END_URL + "/vocabulary-game/setup")

    css_selector_form_selects = (By.CSS_SELECTOR, "main form .form-select")
    css_selector_base_language_option = (By.ID, "{}Item".format(random_base_language.language_name))
    css_selector_target_language_option = (By.ID, "{}Item".format(random_target_language.language_name))
    css_selector_submit_button = (By.CSS_SELECTOR, "main form .btn-success")
    css_selector_alert_toast = (By.CSS_SELECTOR, "main .toast-container .toast")

    find_element(selenium_driver, css_selector_submit_button)
    form_selects = selenium_driver.find_elements(css_selector_form_selects[0], css_selector_form_selects[1])
    # Selecting the target language
    if choose_target_language:
        form_selects[1].click()
        find_element(selenium_driver, css_selector_target_language_option)
        target_language_option = form_selects[1]\
            .find_element(css_selector_target_language_option[0], css_selector_target_language_option[1])
        target_language_option.click()
    # Selecting the base language
    if choose_base_language:
        form_selects[0].click()
        find_element(selenium_driver, css_selector_base_language_option)
        base_language_option = form_selects[0]\
            .find_element(css_selector_base_language_option[0], css_selector_base_language_option[1])
        base_language_option.click()

    submit_button = find_element(selenium_driver, css_selector_submit_button)
    submit_button.click()

    alert_toast = find_element(selenium_driver, css_selector_alert_toast)

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "You must set both base and target languages."


@pytest.mark.django_db
def test_vocabulary_game_setup_base_and_target_languages_must_not_be_equal(live_server, selenium_driver, words,
                                                                           languages):
    """
    Tests that the base and target language picked must not be the same.
    """
    random_language = random.choice(languages)

    selenium_driver.get(FRONT_END_URL + "/vocabulary-game/setup")

    css_selector_form_selects = (By.CSS_SELECTOR, "main form .form-select")
    css_selector_random_language_option = (By.ID, "{}Item".format(random_language.language_name))
    css_selector_submit_button = (By.CSS_SELECTOR, "main form .btn-success")
    css_selector_alert_toast = (By.CSS_SELECTOR, "main .toast-container .toast")

    find_element(selenium_driver, css_selector_submit_button)
    form_selects = selenium_driver.find_elements(css_selector_form_selects[0], css_selector_form_selects[1])
    # Selecting the target language
    form_selects[1].click()
    find_element(selenium_driver, css_selector_random_language_option)
    target_language_option = form_selects[1]\
        .find_element(css_selector_random_language_option[0], css_selector_random_language_option[1])
    target_language_option.click()
    # Selecting the base language
    form_selects[0].click()
    find_element(selenium_driver, css_selector_random_language_option)
    base_language_option = form_selects[0]\
        .find_element(css_selector_random_language_option[0], css_selector_random_language_option[1])
    base_language_option.click()

    submit_button = find_element(selenium_driver, css_selector_submit_button)
    submit_button.click()

    alert_toast = find_element(selenium_driver, css_selector_alert_toast)

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "Base and target languages must be different."


@pytest.mark.django_db
def test_vocabulary_game_setup_form_submission(live_server, selenium_driver, words, languages):
    """
    Tests the setup of the vocabulary game, that is, that when valid base and target languages are chosen, a word in
    the target language is chosen randomly and its translation in the base language is asked.
    """
    random_base_language = random.choice(languages)
    random_target_language = random.choice(languages.exclude(id=random_base_language.id))

    selenium_driver.get(FRONT_END_URL + "/vocabulary-game/setup")

    css_selector_form_selects = (By.CSS_SELECTOR, "main form .form-select")
    css_selector_base_language_option = (By.ID, "{}Item".format(random_base_language.language_name))
    css_selector_target_language_option = (By.ID, "{}Item".format(random_target_language.language_name))
    css_selector_submit_button = (By.CSS_SELECTOR, "main form .btn-success")

    find_element(selenium_driver, css_selector_submit_button)
    form_selects = selenium_driver.find_elements(css_selector_form_selects[0], css_selector_form_selects[1])
    # Selecting the target language
    form_selects[1].click()
    find_element(selenium_driver, css_selector_target_language_option)
    target_language_option = form_selects[1]\
        .find_element(css_selector_target_language_option[0], css_selector_target_language_option[1])
    target_language_option.click()
    # Selecting the base language
    form_selects[0].click()
    find_element(selenium_driver, css_selector_base_language_option)
    base_language_option = form_selects[0]\
        .find_element(css_selector_base_language_option[0], css_selector_base_language_option[1])
    base_language_option.click()

    submit_button = find_element(selenium_driver, css_selector_submit_button)
    submit_button.click()

    css_selector_word_input = (By.CSS_SELECTOR, "main form #wordInput")
    css_selector_answer_input = (By.CSS_SELECTOR, "main form #answerInput")
    css_selector_verify_answer_button = (By.CSS_SELECTOR, "main form .btn-success")

    word_input = find_element(selenium_driver, css_selector_word_input)
    answer_input = find_element(selenium_driver, css_selector_answer_input)
    verify_answer_button = find_element(selenium_driver, css_selector_verify_answer_button)

    word_name = word_input.get_attribute("placeholder")
    answer_placeholder = answer_input.get_attribute("placeholder")

    assert Word.objects.filter(
        word_name=word_name,
        language=random_target_language
    ).exists()
    assert answer_placeholder == "Provide the translation in {}".format(random_base_language.language_name)
    assert verify_answer_button.text == "Verify answer"
