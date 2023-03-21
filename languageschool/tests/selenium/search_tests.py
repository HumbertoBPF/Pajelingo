import pytest
from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import assert_menu, find_element
from pajelingo.settings import FRONT_END_URL


@pytest.mark.django_db
def test_search_form(live_server, selenium_driver, languages):
    """
    Tests that the search form is displayed with a search text input, all the languages as options in the checkbox
    group, and the submit button.
    """
    selenium_driver.get(FRONT_END_URL + "/search")

    assert_menu(selenium_driver)

    css_selector_search_form_input = (By.CSS_SELECTOR, "main form .form-floating .form-control")
    css_selector_form_check = (By.CSS_SELECTOR, "main form .form-check")
    css_selector_submit_button = (By.CSS_SELECTOR, "main form .btn-success")

    search_form_input = find_element(selenium_driver, css_selector_search_form_input)
    find_element(selenium_driver, css_selector_form_check)
    search_form_checkboxes = selenium_driver.find_elements(css_selector_form_check[0], css_selector_form_check[1])
    search_form_submit_button = find_element(selenium_driver, css_selector_submit_button)

    assert search_form_input.get_attribute("placeholder") == "Search for..."
    assert len(search_form_checkboxes) == len(languages)

    for i in range(len(languages)):
        assert search_form_checkboxes[i].find_element(By.CSS_SELECTOR, "label").text == languages[i].language_name
        assert search_form_checkboxes[i].find_element(By.CSS_SELECTOR, "input")\
                   .get_attribute("value") == languages[i].language_name

    assert search_form_submit_button.text == "Search"
