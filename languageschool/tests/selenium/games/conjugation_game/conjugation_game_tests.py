import random

import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import Conjugation, Badge, Score
from languageschool.tests.selenium.utils import find_element, wait_attribute_to_be_non_empty, authenticate_user, \
    wait_number_of_elements_to_be
from languageschool.tests.utils import achieve_explorer_badge
from pajelingo.settings import FRONT_END_URL

CSS_SELECTOR_FORM_LABEL = (By.CSS_SELECTOR, "main form .form-label")
CSS_SELECTOR_FORM_INPUT = (By.CSS_SELECTOR, "main form .form-control")
CSS_SELECTOR_SUBMIT_BUTTON = (By.CSS_SELECTOR, "main form .btn-success")
CSS_SELECTOR_BADGE_NOTIFICATION_HEADER = (By.CSS_SELECTOR, "main .toast-container .toast-header")
CSS_SELECTOR_BADGE_NOTIFICATION_BODY = (By.CSS_SELECTOR, "main .toast-container .toast-body")

def get_conjugation(form_input):
    verb, tense = wait_attribute_to_be_non_empty(form_input, "placeholder", 10).split(" - ")

    counter = 0

    while (verb == "") or (tense == ""):
        verb, tense = wait_attribute_to_be_non_empty(form_input, "placeholder", 10).split(" - ")
        counter += 1

        if counter > 1000:
            break

    return verb, tense


def submit_answer(selenium_driver, conjugation_1, conjugation_2, conjugation_3, conjugation_4, conjugation_5,
                  conjugation_6):
    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_LABEL, 7)
    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_INPUT, 7)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_SUBMIT_BUTTON)

    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUT[0], CSS_SELECTOR_FORM_INPUT[1])

    form_inputs[1].send_keys(conjugation_1)
    form_inputs[2].send_keys(conjugation_2)
    form_inputs[3].send_keys(conjugation_3)
    form_inputs[4].send_keys(conjugation_4)
    form_inputs[5].send_keys(conjugation_5)
    form_inputs[6].send_keys(conjugation_6)

    submit_button.click()


@pytest.mark.django_db
def test_conjugation_game_play_form_rendering(live_server, selenium_driver, languages, conjugations):
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
def test_conjugation_game_play_non_authenticated_user(live_server, selenium_driver, languages, conjugations, is_correct):
    """
    Tests the feedback provided for unauthenticated users when they play the conjugation game in case of a correct and
    of an incorrect answer.
    """
    random_language = random.choice(languages)
    selenium_driver.get(FRONT_END_URL + "/conjugation-game/play?language={}".format(random_language.language_name))

    css_selector_alert = (By.CSS_SELECTOR, "main .alert-{}".format("success" if is_correct else "danger"))

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_INPUT, 7)
    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUT[0], CSS_SELECTOR_FORM_INPUT[1])

    verb, tense = get_conjugation(form_inputs[0])

    conjugation = Conjugation.objects.filter(
        word__word_name=verb,
        word__language__language_name=random_language.language_name,
        tense=tense
    ).first()

    conjugation_1 = (conjugation.conjugation_1 if is_correct else get_random_string(8))
    conjugation_2 = (conjugation.conjugation_2 if is_correct else get_random_string(8))
    conjugation_3 = (conjugation.conjugation_3 if is_correct else get_random_string(8))
    conjugation_4 = (conjugation.conjugation_4 if is_correct else get_random_string(8))
    conjugation_5 = (conjugation.conjugation_5 if is_correct else get_random_string(8))
    conjugation_6 = (conjugation.conjugation_6 if is_correct else get_random_string(8))

    submit_answer(selenium_driver, conjugation_1, conjugation_2, conjugation_3, conjugation_4, conjugation_5,
                  conjugation_6)

    feedback_alert = find_element(selenium_driver, css_selector_alert)

    correct_answer = f"{random_language.personal_pronoun_1} {conjugation.conjugation_1}\n" \
                     f"{random_language.personal_pronoun_2} {conjugation.conjugation_2}\n" \
                     f"{random_language.personal_pronoun_3} {conjugation.conjugation_3}\n" \
                     f"{random_language.personal_pronoun_4} {conjugation.conjugation_4}\n" \
                     f"{random_language.personal_pronoun_5} {conjugation.conjugation_5}\n" \
                     f"{random_language.personal_pronoun_6} {conjugation.conjugation_6}"

    if is_correct:
        expected_feedback = f"Correct answer :)\n{correct_answer}"
    else:
        expected_feedback = f"Wrong answer\n{correct_answer}"

    assert feedback_alert.text == expected_feedback


@pytest.mark.parametrize("is_correct", [True, False])
@pytest.mark.django_db
def test_conjugation_game_play_authenticated_user(live_server, selenium_driver, account, languages,
                                                  conjugations, is_correct):
    """
    Tests the feedback provided for authenticated users when they play the conjugation game in case of a correct and
    of an incorrect answer.
    """
    user, password = account()[0]
    achieve_explorer_badge(user)
    authenticate_user(selenium_driver, user.username, password)

    conjugation_game_id = 3
    random_language = random.choice(languages)

    initial_score = Score.objects.filter(
        user=user,
        language=random_language,
        game__id=conjugation_game_id
    ).first()
    expected_score = 1 if (initial_score is None) else initial_score.score + 1

    selenium_driver.get(FRONT_END_URL + "/conjugation-game/play?language={}".format(random_language.language_name))

    css_selector_alert = (By.CSS_SELECTOR, "main .alert-{}".format("success" if is_correct else "danger"))

    wait_number_of_elements_to_be(selenium_driver, CSS_SELECTOR_FORM_INPUT, 7)
    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUT[0], CSS_SELECTOR_FORM_INPUT[1])

    verb, tense = get_conjugation(form_inputs[0])

    conjugation = Conjugation.objects.filter(
        word__word_name=verb,
        word__language__language_name=random_language.language_name,
        tense=tense
    ).first()

    conjugation_1 = (conjugation.conjugation_1 if is_correct else get_random_string(8))
    conjugation_2 = (conjugation.conjugation_2 if is_correct else get_random_string(8))
    conjugation_3 = (conjugation.conjugation_3 if is_correct else get_random_string(8))
    conjugation_4 = (conjugation.conjugation_4 if is_correct else get_random_string(8))
    conjugation_5 = (conjugation.conjugation_5 if is_correct else get_random_string(8))
    conjugation_6 = (conjugation.conjugation_6 if is_correct else get_random_string(8))

    submit_answer(selenium_driver, conjugation_1, conjugation_2, conjugation_3, conjugation_4, conjugation_5,
                  conjugation_6)

    feedback_alert = find_element(selenium_driver, css_selector_alert)

    correct_answer = f"{random_language.personal_pronoun_1} {conjugation.conjugation_1}\n" \
                     f"{random_language.personal_pronoun_2} {conjugation.conjugation_2}\n" \
                     f"{random_language.personal_pronoun_3} {conjugation.conjugation_3}\n" \
                     f"{random_language.personal_pronoun_4} {conjugation.conjugation_4}\n" \
                     f"{random_language.personal_pronoun_5} {conjugation.conjugation_5}\n" \
                     f"{random_language.personal_pronoun_6} {conjugation.conjugation_6}"

    if is_correct:
        expected_feedback = f"Correct answer :)\n{correct_answer}\nYour score is {expected_score}"
    else:
        expected_feedback = f"Wrong answer\n{correct_answer}"

    assert feedback_alert.text == expected_feedback

    if is_correct:
        badge_explorer = Badge.objects.get(id=1)

        badge_notification_header = find_element(selenium_driver, CSS_SELECTOR_BADGE_NOTIFICATION_HEADER)
        badge_notification_body = find_element(selenium_driver, CSS_SELECTOR_BADGE_NOTIFICATION_BODY)

        assert badge_notification_header.text == f"New achievement: {badge_explorer.name}"
        assert badge_notification_body.text == badge_explorer.description
