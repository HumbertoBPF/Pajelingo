import random

import pytest
from selenium.webdriver.common.by import By

from languageschool.models import Word
from languageschool.tests.selenium.utils import find_element
from pajelingo.settings import FRONT_END_URL


@pytest.mark.django_db
def test_article_game_setup_form(live_server, selenium_driver, languages):
    """
    Tests the rendering of the article game setup form, that is, that the select input holds one option for each
    language and the presence of a submit button.
    """
    expected_options = {"Choose a language": True}

    for language in languages:
        expected_options[language.language_name] = True

    selenium_driver.get(FRONT_END_URL + "/article-game/setup")

    css_selector_form_select = (By.CSS_SELECTOR, "main form .form-select")
    css_selector_select_options = (By.ID, "{}Item".format(languages[0].language_name))
    css_selector_submit_button = (By.CSS_SELECTOR, "main form .btn-success")

    form_select = find_element(selenium_driver, css_selector_form_select)
    submit_button = find_element(selenium_driver, css_selector_submit_button)

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
def test_article_game_form_submission_error(live_server, selenium_driver, languages):
    """
    Tests an invalid submission of the article game setup form, that is, that after the submission an alert toast with
    an error message is displayed.
    """
    selenium_driver.get(FRONT_END_URL + "/article-game/setup")

    css_selector_submit_button = (By.CSS_SELECTOR, "main form .btn-success")
    css_selector_alert_toast = (By.CSS_SELECTOR, "main .toast-container .toast")

    submit_button = find_element(selenium_driver, css_selector_submit_button)
    submit_button.click()

    alert_toast = find_element(selenium_driver, css_selector_alert_toast)

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == "You must choose a language."


@pytest.mark.django_db
def test_article_game_form_submission(live_server, selenium_driver, languages, words):
    """
    Tests a valid submission of the article game form, which should display a word in the selected language, an input
    for the answer and a submission button to verify the answer.
    """
    random_language = random.choice(languages).language_name

    selenium_driver.get(FRONT_END_URL + "/article-game/setup")

    css_selector_form_select = (By.CSS_SELECTOR, "main form .form-select")
    css_selector_select_option = (By.ID, "{}Item".format(random_language))
    css_selector_submit_button = (By.CSS_SELECTOR, "main form .btn-success")

    form_select = find_element(selenium_driver, css_selector_form_select)

    form_select.click()

    select_option = find_element(selenium_driver, css_selector_select_option)

    select_option.click()

    submit_button = find_element(selenium_driver, css_selector_submit_button)

    submit_button.click()

    css_selector_form_inputs = (By.CSS_SELECTOR, "main form .form-control")
    css_selector_submit_button = (By.CSS_SELECTOR, "main form .btn-success")

    find_element(selenium_driver, css_selector_form_inputs)

    form_inputs = selenium_driver.find_elements(css_selector_form_inputs[0], css_selector_form_inputs[1])
    submit_button = find_element(selenium_driver, css_selector_submit_button)

    word = form_inputs[1].get_attribute("placeholder")

    assert form_inputs[0].get_attribute("placeholder") == "Article"
    assert Word.objects.filter(
        word_name=word,
        language__language_name=random_language
    ).exists()
    assert submit_button.text == "Verify answer"