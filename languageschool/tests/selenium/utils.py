from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def find_element(selenium_driver, locator):
    """
    Tries to find an element matching the specified locator.

    :param selenium_driver: Selenium web driver
    :param locator: locator to be matched
    :type locator: tuple

    :return: the element object matching the specified locator. If no element matching the locator could be found, an
    timeout exception is raised.
    """
    wait = WebDriverWait(selenium_driver, 10)
    return wait.until(EC.visibility_of_element_located(locator))

def wait_text_to_be_present(selenium_driver, locator, text):
    """
    Waits until the text populates the element with the specified locator.

    :param selenium_driver: Selenium web driver
    :param locator: locator to be matched
    :type locator: tuple
    :param text: text that it is expected to populate the element matching the specified locator
    :type text: str
    """
    wait = WebDriverWait(selenium_driver, 10)
    wait.until(EC.text_to_be_present_in_element(locator, text))


def assert_menu(selenium_driver, user=None):
    """
    Performs the assertions related to the menu component.

    :param selenium_driver: Selenium web driver
    :param user: authenticated user
    """
    css_selector_menu_items = (By.CSS_SELECTOR, "header .navbar-nav .nav-link")
    css_selector_games_dropdown = (By.CSS_SELECTOR, "header .dropdown .dropdown-item")
    css_selector_sign_up_button = (By.CSS_SELECTOR, "header .btn-success")
    css_selector_sign_in_button = (By.CSS_SELECTOR, "header .btn-primary")

    find_element(selenium_driver, css_selector_menu_items)
    menu_items = selenium_driver.find_elements(css_selector_menu_items[0], css_selector_menu_items[1])

    assert len(menu_items) == 3
    assert menu_items[0].text == "Search tool"
    assert menu_items[1].text == "Games"
    assert menu_items[2].text == "About us"

    menu_items[1].click()

    find_element(selenium_driver, css_selector_games_dropdown)
    dropdown_items = selenium_driver.find_elements(css_selector_games_dropdown[0], css_selector_games_dropdown[1])

    assert len(dropdown_items) == 4
    assert dropdown_items[0].text == "Vocabulary training"
    assert dropdown_items[1].text == "Guess the article"
    assert dropdown_items[2].text == "Conjugation game"
    assert dropdown_items[3].text == "Rankings"

    if user is None:
        sign_up_button = find_element(selenium_driver, css_selector_sign_up_button)
        sign_in_button = find_element(selenium_driver, css_selector_sign_in_button)
        assert sign_up_button.text == "Sign up"
        assert sign_in_button.text == "Sign in"
