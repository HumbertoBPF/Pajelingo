from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import assert_menu, find_element
from pajelingo.settings import FRONT_END_URL

ABOUT_US_URL = FRONT_END_URL + "/about-us"


def test_about_us_page(live_server, selenium_driver):
    """
    Checks the about us page, verifying the content of all cards displayed.
    """
    selenium_driver.get(ABOUT_US_URL)

    assert_menu(selenium_driver)

    css_selector_about_us_cards = (By.CSS_SELECTOR, "main .card .card-body .card-text")

    find_element(selenium_driver, css_selector_about_us_cards)

    about_us_items = selenium_driver.find_elements(css_selector_about_us_cards[0], css_selector_about_us_cards[1])

    assert len(about_us_items) == 5
    assert about_us_items[0].text == "Welcome to Pajelingo!"
    assert about_us_items[1].text == "Here you find help to learn foreign languages :)"
    assert about_us_items[2].text == "Use the search tool to expand your vocabulary! In order to keep your imersion" \
                                     " in your target language, we provide meanings instead of translations :)"
    assert about_us_items[3].text == "We have several games that you can play to practice different competences of " \
                                     "your target language!"
    assert about_us_items[4].text == "No registration is needed to access the search tool neither to play our games! " \
                                     "However, by signing up, you can participate in our games rankings and compete " \
                                     "with other players."
