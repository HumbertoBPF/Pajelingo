from selenium.webdriver.common.by import By

from languageschool.tests.selenium.utils import find_element, wait_text_to_be_present, assert_menu
from pajelingo.settings import FRONT_END_URL


def test_dashboard_onwards(live_server, selenium_driver):
    """
    Checks the carousel items on the dashboard browsing onwards, that is, 1 -> 2 -> 3.
    """
    selenium_driver.get(FRONT_END_URL + "/dashboard")

    assert_menu(selenium_driver)

    next_button_locator = (By.CSS_SELECTOR, "main .justify-content-center .carousel .carousel-control-next")
    item_title_locator = (By.CSS_SELECTOR, "main .justify-content-center .active .carousel-caption h5")
    item_description_locator = (By.CSS_SELECTOR, "main .justify-content-center .active .carousel-caption p")

    carousel_next_button = find_element(selenium_driver, next_button_locator)
    carousel_item_title = find_element(selenium_driver, item_title_locator)
    carousel_item_description = find_element(selenium_driver, item_description_locator)

    assert carousel_item_title.text == "Vocabulary training"
    assert carousel_item_description.text == "Practice your vocabulary!"

    carousel_next_button.click()

    wait_text_to_be_present(selenium_driver, item_title_locator, "Guess the article")
    wait_text_to_be_present\
        (selenium_driver, item_description_locator, "Guess the article that matches the showed word!")

    carousel_next_button.click()

    wait_text_to_be_present(selenium_driver, item_title_locator, "Conjugation game")
    wait_text_to_be_present\
        (selenium_driver, item_description_locator, "Can you guess all the conjugations in any tense and mode?")


def test_dashboard_backwards(live_server, selenium_driver):
    """
    Checks the carousel items on the dashboard browsing backwards, that is, 1 -> 3 -> 2.
    """
    selenium_driver.get(FRONT_END_URL + "/dashboard")

    assert_menu(selenium_driver)

    previous_button_locator = (By.CSS_SELECTOR, "main .justify-content-center .carousel .carousel-control-prev")
    item_title_locator = (By.CSS_SELECTOR, "main .justify-content-center .active .carousel-caption h5")
    item_description_locator = (By.CSS_SELECTOR, "main .justify-content-center .active .carousel-caption p")

    carousel_previous_button = find_element(selenium_driver, previous_button_locator)
    carousel_item_title = find_element(selenium_driver, item_title_locator)
    carousel_item_description = find_element(selenium_driver, item_description_locator)

    assert carousel_item_title.text == "Vocabulary training"
    assert carousel_item_description.text == "Practice your vocabulary!"

    carousel_previous_button.click()

    wait_text_to_be_present(selenium_driver, item_title_locator, "Conjugation game")
    wait_text_to_be_present \
        (selenium_driver, item_description_locator, "Can you guess all the conjugations in any tense and mode?")

    carousel_previous_button.click()

    wait_text_to_be_present(selenium_driver, item_title_locator, "Guess the article")
    wait_text_to_be_present \
        (selenium_driver, item_description_locator, "Guess the article that matches the showed word!")