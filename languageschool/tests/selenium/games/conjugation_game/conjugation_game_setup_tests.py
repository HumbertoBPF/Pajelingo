import random

import pytest
from selenium.webdriver.common.by import By

from languageschool.models import Conjugation
from languageschool.tests.selenium.utils import find_element, find_by_test_id
from pajelingo.settings import FRONT_END_URL

CONJUGATION_GAME_SETUP_URL = f"{FRONT_END_URL}/conjugation-game/setup"


@pytest.mark.django_db
def test_conjugation_game_setup_form_submission_error(live_server, selenium_driver, languages):
    """
    Tests an invalid submission of the conjugation game setup form, that is, that after the submission an alert toast
    with an error message is displayed.
    """
    selenium_driver.get(CONJUGATION_GAME_SETUP_URL)

    submit_button = find_by_test_id(selenium_driver, "start-button")
    submit_button.click()

    error_toast = find_by_test_id(selenium_driver, "error-toast")

    assert error_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert error_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == "You must choose a language."


@pytest.mark.django_db
def test_conjugation_game_setup_form_submission(live_server, selenium_driver, languages, verbs, conjugations):
    """
    Tests a valid submission of the conjugation game form, which should display a verb and a tense, representing a
    conjugation, the pronouns of the selected language, and inputs for the conjugation of the displayed verb.
    """
    random_language = random.choice(languages)

    selenium_driver.get(CONJUGATION_GAME_SETUP_URL)

    form_select = find_by_test_id(selenium_driver, "select-language")
    form_select.click()

    css_selector_select_option = (By.ID, random_language.language_name)
    select_option = find_element(selenium_driver, css_selector_select_option)
    select_option.click()

    submit_button = find_by_test_id(selenium_driver, "start-button")
    submit_button.click()

    verb_and_tense = find_by_test_id(selenium_driver, "verb-and-tense")
    conjugation_1 = find_by_test_id(selenium_driver, "conjugation-1")
    conjugation_2 = find_by_test_id(selenium_driver, "conjugation-2")
    conjugation_3 = find_by_test_id(selenium_driver, "conjugation-3")
    conjugation_4 = find_by_test_id(selenium_driver, "conjugation-4")
    conjugation_5 = find_by_test_id(selenium_driver, "conjugation-5")
    conjugation_6 = find_by_test_id(selenium_driver, "conjugation-6")

    verb, tense = verb_and_tense.find_element(By.CSS_SELECTOR, "input").get_attribute("placeholder").split(" - ")
    assert Conjugation.objects.filter(
        word__word_name=verb,
        tense=tense
    ).exists()

    assert conjugation_1.find_element(By.CSS_SELECTOR, "label").text == random_language.personal_pronoun_1
    assert conjugation_2.find_element(By.CSS_SELECTOR, "label").text == random_language.personal_pronoun_2
    assert conjugation_3.find_element(By.CSS_SELECTOR, "label").text == random_language.personal_pronoun_3
    assert conjugation_4.find_element(By.CSS_SELECTOR, "label").text == random_language.personal_pronoun_4
    assert conjugation_5.find_element(By.CSS_SELECTOR, "label").text == random_language.personal_pronoun_5
    assert conjugation_6.find_element(By.CSS_SELECTOR, "label").text == random_language.personal_pronoun_6
