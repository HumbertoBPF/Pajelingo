import random

import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import Conjugation
from languageschool.tests.selenium.utils import find_element, wait_attribute_to_be_non_empty, authenticate_user, \
    wait_number_of_elements_to_be
from pajelingo.settings import FRONT_END_URL

CSS_SELECTOR_FORM_LABEL = (By.CSS_SELECTOR, "main form .form-label")
CSS_SELECTOR_FORM_INPUT = (By.CSS_SELECTOR, "main form .form-control")
CSS_SELECTOR_SUBMIT_BUTTON = (By.CSS_SELECTOR, "main form .btn-success")

def get_conjugation(form_input):
    verb, tense = wait_attribute_to_be_non_empty(form_input, "placeholder", 10).split(" - ")

    counter = 0

    while (verb == "") or (tense == ""):
        verb, tense = wait_attribute_to_be_non_empty(form_input, "placeholder", 10).split(" - ")
        counter += 1

        if counter > 1000:
            break

    return verb, tense


@pytest.mark.django_db
def test_conjugation_game_play_form_rendering(live_server, selenium_driver, conjugation_game, languages, conjugations):
    """
    Tests the rendering of the form that the player sees during the gameplay. The form must contain an input with the
    verb and the verbal tense. Besides, there must be 6 inputs where the user is going to type the conjugations and a
    button to submit the answer.
    """
    random_language = random.choice(languages)
    selenium_driver.get(FRONT_END_URL + "/conjugation-game/play?language={}".format(random_language.language_name))

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_LABEL, 7)
    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_INPUT, 7)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    form_labels = selenium_driver.find_elements(CSS_SELECTOR_FORM_LABEL[0], CSS_SELECTOR_FORM_LABEL[1])
    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUT[0], CSS_SELECTOR_FORM_INPUT[1])

    verb, tense = get_conjugation(form_inputs[0])

    assert Conjugation.objects.filter(
        word__word_name=verb,
        word__language__language_name=random_language.language_name,
        tense=tense
    ).exists()

    assert len(form_labels) == 7
    assert len(form_inputs) == 7

    assert form_labels[1].text == random_language.personal_pronoun_1
    assert form_labels[2].text == random_language.personal_pronoun_2
    assert form_labels[3].text == random_language.personal_pronoun_3
    assert form_labels[4].text == random_language.personal_pronoun_4
    assert form_labels[5].text == random_language.personal_pronoun_5
    assert form_labels[6].text == random_language.personal_pronoun_6

    assert submit_button.text == "Verify answer"


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_conjugation_game_play_non_authenticated_user(live_server, selenium_driver, conjugation_game, languages,
                                                      conjugations, is_correct):
    """
    Tests the feedback provided for unauthenticated users when they play the conjugation game in case of a correct and
    of an incorrect answer.
    """
    random_language = random.choice(languages)
    selenium_driver.get(FRONT_END_URL + "/conjugation-game/play?language={}".format(random_language.language_name))

    css_selector_alert = (By.CSS_SELECTOR, "main .alert-{}".format("success" if is_correct else "danger"))

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_LABEL, 7)
    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_INPUT, 7)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUT[0], CSS_SELECTOR_FORM_INPUT[1])

    verb, tense = get_conjugation(form_inputs[0])

    conjugation = Conjugation.objects.filter(
        word__word_name=verb,
        word__language__language_name=random_language.language_name,
        tense=tense
    ).first()

    form_inputs[1].send_keys(conjugation.conjugation_1 if is_correct else get_random_string(8))
    form_inputs[2].send_keys(conjugation.conjugation_2 if is_correct else get_random_string(8))
    form_inputs[3].send_keys(conjugation.conjugation_3 if is_correct else get_random_string(8))
    form_inputs[4].send_keys(conjugation.conjugation_4 if is_correct else get_random_string(8))
    form_inputs[5].send_keys(conjugation.conjugation_5 if is_correct else get_random_string(8))
    form_inputs[6].send_keys(conjugation.conjugation_6 if is_correct else get_random_string(8))

    submit_button.click()

    feedback_alert = find_element(selenium_driver, css_selector_alert)

    expected_feedback = "{}\n" \
                        "{} {}\n" \
                        "{} {}\n" \
                        "{} {}\n" \
                        "{} {}\n" \
                        "{} {}\n" \
                        "{} {}".format("Correct answer :)" if is_correct else "Wrong answer",
                                       random_language.personal_pronoun_1, conjugation.conjugation_1,
                                       random_language.personal_pronoun_2, conjugation.conjugation_2,
                                       random_language.personal_pronoun_3, conjugation.conjugation_3,
                                       random_language.personal_pronoun_4, conjugation.conjugation_4,
                                       random_language.personal_pronoun_5, conjugation.conjugation_5,
                                       random_language.personal_pronoun_6, conjugation.conjugation_6)

    assert feedback_alert.text == expected_feedback


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_conjugation_game_play_authenticated_user(live_server, selenium_driver, account, conjugation_game, languages,
                                                  conjugations, is_correct):
    """
    Tests the feedback provided for authenticated users when they play the conjugation game in case of a correct and
    of an incorrect answer.
    """
    user, password = account()[0]
    authenticate_user(selenium_driver, user.username, password)

    random_language = random.choice(languages)
    selenium_driver.get(FRONT_END_URL + "/conjugation-game/play?language={}".format(random_language.language_name))

    css_selector_alert = (By.CSS_SELECTOR, "main .alert-{}".format("success" if is_correct else "danger"))

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_LABEL, 7)
    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_INPUT, 7)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUT[0], CSS_SELECTOR_FORM_INPUT[1])

    verb, tense = get_conjugation(form_inputs[0])

    conjugation = Conjugation.objects.filter(
        word__word_name=verb,
        word__language__language_name=random_language.language_name,
        tense=tense
    ).first()

    form_inputs[1].send_keys(conjugation.conjugation_1 if is_correct else get_random_string(8))
    form_inputs[2].send_keys(conjugation.conjugation_2 if is_correct else get_random_string(8))
    form_inputs[3].send_keys(conjugation.conjugation_3 if is_correct else get_random_string(8))
    form_inputs[4].send_keys(conjugation.conjugation_4 if is_correct else get_random_string(8))
    form_inputs[5].send_keys(conjugation.conjugation_5 if is_correct else get_random_string(8))
    form_inputs[6].send_keys(conjugation.conjugation_6 if is_correct else get_random_string(8))

    submit_button.click()

    feedback_alert = find_element(selenium_driver, css_selector_alert)

    expected_feedback = "{}\n" \
                        "{} {}\n" \
                        "{} {}\n" \
                        "{} {}\n" \
                        "{} {}\n" \
                        "{} {}\n" \
                        "{} {}" \
                        "{}".format("Correct answer :)" if is_correct else "Wrong answer",
                                    random_language.personal_pronoun_1, conjugation.conjugation_1,
                                    random_language.personal_pronoun_2, conjugation.conjugation_2,
                                    random_language.personal_pronoun_3, conjugation.conjugation_3,
                                    random_language.personal_pronoun_4, conjugation.conjugation_4,
                                    random_language.personal_pronoun_5, conjugation.conjugation_5,
                                    random_language.personal_pronoun_6, conjugation.conjugation_6,
                                    "\nYour score is 1" if is_correct else "")

    assert feedback_alert.text == expected_feedback
