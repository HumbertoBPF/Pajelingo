import random

import pytest
from selenium.webdriver.common.by import By

from languageschool.models import Conjugation
from languageschool.tests.selenium.utils import find_element, wait_attribute_to_be_non_empty
from pajelingo.settings import FRONT_END_URL


@pytest.mark.django_db
def test_conjugation_game_play_form_rendering(live_server, selenium_driver, conjugation_game, languages, conjugations):
    random_language = random.choice(languages)
    selenium_driver.get(FRONT_END_URL + "/conjugation-game/play?language={}".format(random_language.language_name))

    css_selector_form_label = (By.CSS_SELECTOR, "main form .form-label")
    css_selector_form_input = (By.CSS_SELECTOR, "main form .form-control")
    css_submit_button = (By.CSS_SELECTOR, "main form .btn-success")

    submit_button = find_element(selenium_driver, css_submit_button)
    form_labels = selenium_driver.find_elements(css_selector_form_label[0], css_selector_form_label[1])
    form_inputs = selenium_driver.find_elements(css_selector_form_input[0], css_selector_form_input[1])

    verb, tense = wait_attribute_to_be_non_empty(form_inputs[0], "placeholder", 10).split(" - ")

    counter = 0

    while (verb == "") or (tense == ""):
        verb, tense = wait_attribute_to_be_non_empty(form_inputs[0], "placeholder", 10).split(" - ")
        counter += 1

        if counter > 1000:
            break

    assert Conjugation.objects.filter(
        word__word_name=verb,
        word__language__language_name=random_language.language_name,
        tense=tense
    ).exists()

    assert form_labels[1].text == random_language.personal_pronoun_1
    assert form_labels[2].text == random_language.personal_pronoun_2
    assert form_labels[3].text == random_language.personal_pronoun_3
    assert form_labels[4].text == random_language.personal_pronoun_4
    assert form_labels[5].text == random_language.personal_pronoun_5
    assert form_labels[6].text == random_language.personal_pronoun_6

    assert len(form_labels) == 7
    assert len(form_inputs) == 7
    assert submit_button.text == "Verify answer"
