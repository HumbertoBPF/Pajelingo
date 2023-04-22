import random

import pytest
from selenium.webdriver.common.by import By

from languageschool.models import Conjugation, Game
from languageschool.tests.selenium.utils import find_element
from pajelingo.settings import FRONT_END_URL

CONJUGATION_GAME_SETUP_URL = FRONT_END_URL + "/conjugation-game/setup"
CSS_SELECTOR_INSTRUCTIONS = (By.CSS_SELECTOR, "main section")
CSS_SELECTOR_FORM_SELECT = (By.CSS_SELECTOR, "main form .form-select")
CSS_SELECTOR_SUBMIT_BUTTON = (By.CSS_SELECTOR, "main form .btn-success")

@pytest.mark.django_db
def test_conjugation_game_setup_form_rendering(live_server, selenium_driver, languages):
    """
    Tests the rendering of the conjugation game setup form, that is, that the select input holds one option for each
    language and the presence of a submit button.
    """
    conjugation_game = Game.objects.get(pk=3)
    expected_options = {"Choose a language": True}

    for language in languages:
        expected_options[language.language_name] = True

    selenium_driver.get(CONJUGATION_GAME_SETUP_URL)

    css_selector_select_options = (By.ID, "{}Item".format(languages[0].language_name))

    instructions = find_element(selenium_driver, CSS_SELECTOR_INSTRUCTIONS)
    form_select = find_element(selenium_driver, CSS_SELECTOR_FORM_SELECT)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    assert instructions.text == conjugation_game.instructions
    assert submit_button.text == "Start"

    form_select.click()

    find_element(selenium_driver, css_selector_select_options)

    select_options = selenium_driver.find_elements(By.CSS_SELECTOR, "main form .form-select option")

    assert len(select_options) == len(languages) + 1
    # Check if all the expected options are present among the select options
    for select_option in select_options:
        del expected_options[select_option.text]

    assert len(expected_options) == 0


@pytest.mark.django_db
def test_conjugation_game_setup_form_submission_error(live_server, selenium_driver, languages):
    """
    Tests an invalid submission of the conjugation game setup form, that is, that after the submission an alert toast
    with an error message is displayed.
    """
    selenium_driver.get(CONJUGATION_GAME_SETUP_URL)

    css_selector_alert_toast = (By.CSS_SELECTOR, "main .toast-container .toast")

    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)
    submit_button.click()

    alert_toast = find_element(selenium_driver, css_selector_alert_toast)

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == "You must choose a language."


@pytest.mark.django_db
def test_conjugation_game_setup_form_submission(live_server, selenium_driver, languages, verbs, conjugations):
    """
    Tests a valid submission of the conjugation game form, which should display a verb and a tense, representing a
    conjugation, the pronouns of the selected language, and inputs for the conjugation of the displayed verb.
    """
    random_language = random.choice(languages)

    selenium_driver.get(CONJUGATION_GAME_SETUP_URL)

    css_selector_select_option = (By.ID, "{}Item".format(random_language.language_name))

    form_select = find_element(selenium_driver, CSS_SELECTOR_FORM_SELECT)

    form_select.click()

    select_option = find_element(selenium_driver, css_selector_select_option)

    select_option.click()

    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    submit_button.click()

    css_selector_form_label = (By.CSS_SELECTOR, "main form .form-label")
    css_selector_form_input = (By.CSS_SELECTOR, "main form .form-control")

    find_element(selenium_driver, css_selector_form_label)
    find_element(selenium_driver, css_selector_form_input)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    form_labels = selenium_driver.find_elements(css_selector_form_label[0], css_selector_form_label[1])
    form_inputs = selenium_driver.find_elements(css_selector_form_input[0], css_selector_form_input[1])

    assert len(form_labels) == 7
    assert len(form_inputs) == 7

    assert form_labels[0].text == ""
    verb, tense = form_inputs[0].get_attribute("placeholder").split(" - ")
    assert Conjugation.objects.filter(
        word__word_name=verb,
        tense=tense
    ).exists()

    assert form_labels[1].text == random_language.personal_pronoun_1
    assert form_labels[2].text == random_language.personal_pronoun_2
    assert form_labels[3].text == random_language.personal_pronoun_3
    assert form_labels[4].text == random_language.personal_pronoun_4
    assert form_labels[5].text == random_language.personal_pronoun_5
    assert form_labels[6].text == random_language.personal_pronoun_6

    assert submit_button.text == "Verify answer"
