from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import find_element, wait_text_to_be_present, assert_menu
from pajelingo.settings import FRONT_END_URL

DASHBOARD_URL = FRONT_END_URL + "/dashboard"
CSS_SELECTOR_PREVIOUS_BUTTON = (By.CSS_SELECTOR, "main .justify-content-center .carousel .carousel-control-prev")
CSS_SELECTOR_NEXT_BUTTON = (By.CSS_SELECTOR, "main .justify-content-center .carousel .carousel-control-next")
CSS_SELECTOR_ITEM_TITLE = (By.CSS_SELECTOR, "main .justify-content-center .active .carousel-caption h5")
CSS_SELECTOR_ITEM_DESCRIPTION = (By.CSS_SELECTOR, "main .justify-content-center .active .carousel-caption p")


def test_dashboard_onwards(live_server, selenium_driver):
    """
    Checks the carousel items on the dashboard browsing onwards, that is, 1 -> 2 -> 3.
    """
    selenium_driver.get(DASHBOARD_URL)

    assert_menu(selenium_driver)

    carousel_next_button = find_element(selenium_driver, CSS_SELECTOR_NEXT_BUTTON)
    carousel_item_title = find_element(selenium_driver, CSS_SELECTOR_ITEM_TITLE)
    carousel_item_description = find_element(selenium_driver, CSS_SELECTOR_ITEM_DESCRIPTION)

    assert carousel_item_title.text == "Vocabulary training"
    assert carousel_item_description.text == "Practice your vocabulary!"

    carousel_next_button.click()

    wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ITEM_TITLE, "Guess the article")
    wait_text_to_be_present\
        (selenium_driver, CSS_SELECTOR_ITEM_DESCRIPTION, "Guess the article that matches the showed word!")

    carousel_next_button.click()

    wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ITEM_TITLE, "Conjugation game")
    wait_text_to_be_present\
        (selenium_driver, CSS_SELECTOR_ITEM_DESCRIPTION, "Can you guess all the conjugations in any tense and mode?")


def test_dashboard_backwards(live_server, selenium_driver):
    """
    Checks the carousel items on the dashboard browsing backwards, that is, 1 -> 3 -> 2.
    """
    selenium_driver.get(DASHBOARD_URL)

    assert_menu(selenium_driver)

    carousel_previous_button = find_element(selenium_driver, CSS_SELECTOR_PREVIOUS_BUTTON)
    carousel_item_title = find_element(selenium_driver, CSS_SELECTOR_ITEM_TITLE)
    carousel_item_description = find_element(selenium_driver, CSS_SELECTOR_ITEM_DESCRIPTION)

    assert carousel_item_title.text == "Vocabulary training"
    assert carousel_item_description.text == "Practice your vocabulary!"

    carousel_previous_button.click()

    wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ITEM_TITLE, "Conjugation game")
    wait_text_to_be_present \
        (selenium_driver, CSS_SELECTOR_ITEM_DESCRIPTION, "Can you guess all the conjugations in any tense and mode?")

    carousel_previous_button.click()

    wait_text_to_be_present(selenium_driver, CSS_SELECTOR_ITEM_TITLE, "Guess the article")
    wait_text_to_be_present \
        (selenium_driver, CSS_SELECTOR_ITEM_DESCRIPTION, "Guess the article that matches the showed word!")
