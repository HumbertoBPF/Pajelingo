import random

import pytest
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By

from languageschool.models import Conjugation, Badge, Score
from languageschool.tests.selenium.utils import wait_attribute_to_be_non_empty, authenticate_user, find_by_test_id
from languageschool.tests.utils import achieve_explorer_badge
from pajelingo.settings import FRONT_END_URL

TEST_ID_VERB_AND_TENSE = "verb-and-tense"
TEST_ID_CONJUGATION_1 = "conjugation-1"
TEST_ID_CONJUGATION_2 = "conjugation-2"
TEST_ID_CONJUGATION_3 = "conjugation-3"
TEST_ID_CONJUGATION_4 = "conjugation-4"
TEST_ID_CONJUGATION_5 = "conjugation-5"
TEST_ID_CONJUGATION_6 = "conjugation-6"
TEST_ID_SUBMIT_BUTTON = "submit-answer-button"
TEST_ID_FEEDBACK_ALERT = "feedback-alert"

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
def test_conjugation_game_correct_answer_non_authenticated_user(live_server, selenium_driver, languages, conjugations):
    """
    Tests the feedback provided for unauthenticated users when they play the conjugation game in case of a correct and
    of an incorrect answer.
    """
    random_language = random.choice(languages)
    selenium_driver.get(FRONT_END_URL + "/conjugation-game/play?language={}".format(random_language.language_name))

    verb_and_tense = find_by_test_id(selenium_driver, TEST_ID_VERB_AND_TENSE).find_element(By.CSS_SELECTOR, "input")

    verb, tense = get_conjugation(verb_and_tense)

    conjugation = Conjugation.objects.filter(
        word__word_name=verb,
        word__language__language_name=random_language.language_name,
        tense=tense
    ).first()

    conjugation_1_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_1).find_element(By.CSS_SELECTOR, "input")
    conjugation_1_input.send_keys(conjugation.conjugation_1)

    conjugation_2_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_2).find_element(By.CSS_SELECTOR, "input")
    conjugation_2_input.send_keys(conjugation.conjugation_2)

    conjugation_3_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_3).find_element(By.CSS_SELECTOR, "input")
    conjugation_3_input.send_keys(conjugation.conjugation_3)

    conjugation_4_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_4).find_element(By.CSS_SELECTOR, "input")
    conjugation_4_input.send_keys(conjugation.conjugation_4)

    conjugation_5_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_5).find_element(By.CSS_SELECTOR, "input")
    conjugation_5_input.send_keys(conjugation.conjugation_5)

    conjugation_6_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_6).find_element(By.CSS_SELECTOR, "input")
    conjugation_6_input.send_keys(conjugation.conjugation_6)

    submit_button = find_by_test_id(selenium_driver, TEST_ID_SUBMIT_BUTTON)
    submit_button.click()

    feedback_alert = find_by_test_id(selenium_driver, TEST_ID_FEEDBACK_ALERT)

    correct_answer = f"{random_language.personal_pronoun_1} {conjugation.conjugation_1}\n" \
                     f"{random_language.personal_pronoun_2} {conjugation.conjugation_2}\n" \
                     f"{random_language.personal_pronoun_3} {conjugation.conjugation_3}\n" \
                     f"{random_language.personal_pronoun_4} {conjugation.conjugation_4}\n" \
                     f"{random_language.personal_pronoun_5} {conjugation.conjugation_5}\n" \
                     f"{random_language.personal_pronoun_6} {conjugation.conjugation_6}"

    assert feedback_alert.text == f"Correct answer :)\n{correct_answer}"


@pytest.mark.django_db
def test_conjugation_game_incorrect_answer_non_authenticated_user(live_server, selenium_driver, languages, conjugations):
    """
    Tests the feedback provided for unauthenticated users when they play the conjugation game in case of a correct and
    of an incorrect answer.
    """
    random_language = random.choice(languages)
    selenium_driver.get(FRONT_END_URL + "/conjugation-game/play?language={}".format(random_language.language_name))

    verb_and_tense = find_by_test_id(selenium_driver, TEST_ID_VERB_AND_TENSE).find_element(By.CSS_SELECTOR, "input")

    verb, tense = get_conjugation(verb_and_tense)

    conjugation = Conjugation.objects.filter(
        word__word_name=verb,
        word__language__language_name=random_language.language_name,
        tense=tense
    ).first()

    conjugation_1_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_1).find_element(By.CSS_SELECTOR, "input")
    conjugation_1_input.send_keys(get_random_string(8))

    conjugation_2_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_2).find_element(By.CSS_SELECTOR, "input")
    conjugation_2_input.send_keys(get_random_string(8))

    conjugation_3_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_3).find_element(By.CSS_SELECTOR, "input")
    conjugation_3_input.send_keys(get_random_string(8))

    conjugation_4_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_4).find_element(By.CSS_SELECTOR, "input")
    conjugation_4_input.send_keys(get_random_string(8))

    conjugation_5_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_5).find_element(By.CSS_SELECTOR, "input")
    conjugation_5_input.send_keys(get_random_string(8))

    conjugation_6_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_6).find_element(By.CSS_SELECTOR, "input")
    conjugation_6_input.send_keys(get_random_string(8))

    submit_button = find_by_test_id(selenium_driver, TEST_ID_SUBMIT_BUTTON)
    submit_button.click()

    feedback_alert = find_by_test_id(selenium_driver, TEST_ID_FEEDBACK_ALERT)

    correct_answer = f"{random_language.personal_pronoun_1} {conjugation.conjugation_1}\n" \
                     f"{random_language.personal_pronoun_2} {conjugation.conjugation_2}\n" \
                     f"{random_language.personal_pronoun_3} {conjugation.conjugation_3}\n" \
                     f"{random_language.personal_pronoun_4} {conjugation.conjugation_4}\n" \
                     f"{random_language.personal_pronoun_5} {conjugation.conjugation_5}\n" \
                     f"{random_language.personal_pronoun_6} {conjugation.conjugation_6}"

    assert feedback_alert.text == f"Wrong answer\n{correct_answer}"


@pytest.mark.django_db
def test_conjugation_game_correct_answer_authenticated_user(live_server, selenium_driver, account,
                                                            languages, conjugations):
    """
    Tests the feedback provided for authenticated users when they play the conjugation game in case of a correct and
    of an incorrect answer.
    """
    user, password = account()[0]
    achieve_explorer_badge(user)
    authenticate_user(selenium_driver, user.username, password)

    random_language = random.choice(languages)

    initial_score = Score.objects.filter(
        user=user,
        language=random_language,
        game__id=3
    ).first()
    expected_score = 1 if (initial_score is None) else initial_score.score + 1

    selenium_driver.get(FRONT_END_URL + "/conjugation-game/play?language={}".format(random_language.language_name))

    verb_and_tense = find_by_test_id(selenium_driver, TEST_ID_VERB_AND_TENSE).find_element(By.CSS_SELECTOR, "input")

    verb, tense = get_conjugation(verb_and_tense)

    conjugation = Conjugation.objects.filter(
        word__word_name=verb,
        word__language__language_name=random_language.language_name,
        tense=tense
    ).first()

    conjugation_1_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_1).find_element(By.CSS_SELECTOR, "input")
    conjugation_1_input.send_keys(conjugation.conjugation_1)

    conjugation_2_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_2).find_element(By.CSS_SELECTOR, "input")
    conjugation_2_input.send_keys(conjugation.conjugation_2)

    conjugation_3_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_3).find_element(By.CSS_SELECTOR, "input")
    conjugation_3_input.send_keys(conjugation.conjugation_3)

    conjugation_4_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_4).find_element(By.CSS_SELECTOR, "input")
    conjugation_4_input.send_keys(conjugation.conjugation_4)

    conjugation_5_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_5).find_element(By.CSS_SELECTOR, "input")
    conjugation_5_input.send_keys(conjugation.conjugation_5)

    conjugation_6_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_6).find_element(By.CSS_SELECTOR, "input")
    conjugation_6_input.send_keys(conjugation.conjugation_6)

    submit_button = find_by_test_id(selenium_driver, TEST_ID_SUBMIT_BUTTON)
    submit_button.click()

    feedback_alert = find_by_test_id(selenium_driver, TEST_ID_FEEDBACK_ALERT)

    correct_answer = f"{random_language.personal_pronoun_1} {conjugation.conjugation_1}\n" \
                     f"{random_language.personal_pronoun_2} {conjugation.conjugation_2}\n" \
                     f"{random_language.personal_pronoun_3} {conjugation.conjugation_3}\n" \
                     f"{random_language.personal_pronoun_4} {conjugation.conjugation_4}\n" \
                     f"{random_language.personal_pronoun_5} {conjugation.conjugation_5}\n" \
                     f"{random_language.personal_pronoun_6} {conjugation.conjugation_6}"

    assert feedback_alert.text == f"Correct answer :)\n{correct_answer}\nYour score is {expected_score}"

    badge_explorer = Badge.objects.get(id=1)

    badge_notification = find_by_test_id(selenium_driver, f"notification-badge-{badge_explorer.id}")

    badge_notification_header = badge_notification.find_element(By.CSS_SELECTOR, ".toast-header")
    badge_notification_body = badge_notification.find_element(By.CSS_SELECTOR, ".toast-body")

    assert badge_notification_header.text == f"New achievement: {badge_explorer.name}"
    assert badge_notification_body.text == badge_explorer.description


@pytest.mark.django_db
def test_conjugation_game_incorrect_answer_authenticated_user(live_server, selenium_driver, account,
                                                              languages, conjugations):
    """
    Tests the feedback provided for authenticated users when they play the conjugation game in case of a correct and
    of an incorrect answer.
    """
    user, password = account()[0]
    achieve_explorer_badge(user)
    authenticate_user(selenium_driver, user.username, password)

    random_language = random.choice(languages)

    selenium_driver.get(FRONT_END_URL + "/conjugation-game/play?language={}".format(random_language.language_name))

    verb_and_tense = find_by_test_id(selenium_driver, TEST_ID_VERB_AND_TENSE).find_element(By.CSS_SELECTOR, "input")

    verb, tense = get_conjugation(verb_and_tense)

    conjugation = Conjugation.objects.filter(
        word__word_name=verb,
        word__language__language_name=random_language.language_name,
        tense=tense
    ).first()

    conjugation_1_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_1).find_element(By.CSS_SELECTOR, "input")
    conjugation_1_input.send_keys(get_random_string(8))

    conjugation_2_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_2).find_element(By.CSS_SELECTOR, "input")
    conjugation_2_input.send_keys(get_random_string(8))

    conjugation_3_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_3).find_element(By.CSS_SELECTOR, "input")
    conjugation_3_input.send_keys(get_random_string(8))

    conjugation_4_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_4).find_element(By.CSS_SELECTOR, "input")
    conjugation_4_input.send_keys(get_random_string(8))

    conjugation_5_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_5).find_element(By.CSS_SELECTOR, "input")
    conjugation_5_input.send_keys(get_random_string(8))

    conjugation_6_input = find_by_test_id(selenium_driver, TEST_ID_CONJUGATION_6).find_element(By.CSS_SELECTOR, "input")
    conjugation_6_input.send_keys(get_random_string(8))

    submit_button = find_by_test_id(selenium_driver, TEST_ID_SUBMIT_BUTTON)
    submit_button.click()

    feedback_alert = find_by_test_id(selenium_driver, TEST_ID_FEEDBACK_ALERT)

    correct_answer = f"{random_language.personal_pronoun_1} {conjugation.conjugation_1}\n" \
                     f"{random_language.personal_pronoun_2} {conjugation.conjugation_2}\n" \
                     f"{random_language.personal_pronoun_3} {conjugation.conjugation_3}\n" \
                     f"{random_language.personal_pronoun_4} {conjugation.conjugation_4}\n" \
                     f"{random_language.personal_pronoun_5} {conjugation.conjugation_5}\n" \
                     f"{random_language.personal_pronoun_6} {conjugation.conjugation_6}"

    assert feedback_alert.text == f"Wrong answer\n{correct_answer}"
