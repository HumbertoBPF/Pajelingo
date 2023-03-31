import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pajelingo.settings import FRONT_END_URL


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


def wait_attribute_to_be_non_empty(element, attribute, timeout):
    """
    Waits until the specified attribute of the matched element is non-empty.

    :param element: concerned element
    :param attribute: attribute of interest
    :type attribute: str
    :param timeout: time until timeout
    :type timeout: float

    :return: the attribute value when it becomes non-empty
    :rtype: str
    """
    initial_time = time.time()

    element_attribute = element.get_attribute(attribute)

    while element_attribute == "":
        element_attribute = element.get_attribute(attribute)
        if (time.time() - initial_time) > timeout:
            raise TimeoutError("Timeout of {} seconds exceeded.".format(timeout))

    return element_attribute

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
    css_selector_username = (By.CSS_SELECTOR, "header .btn-account-options span")

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
    else:
        username = find_element(selenium_driver, css_selector_username)
        assert  username.text == user.username


def authenticate_user(selenium_driver, username, password):
    """
    Tries to authenticate a user with the provided credentials by filling the login form available in the page /login.

    :param selenium_driver: Selenium web driver
    :param username: username credential
    :type username: str
    :param password: password credential
    :type password: str
    """
    selenium_driver.get(FRONT_END_URL + "/login")

    css_selector_username_input = (By.CSS_SELECTOR, "main form #floatingUsername")
    css_selector_password_input = (By.CSS_SELECTOR, "main form #floatingPassword")
    css_selector_submit_button = (By.CSS_SELECTOR, "main form .btn-success")

    username_input = find_element(selenium_driver, css_selector_username_input)
    password_input = find_element(selenium_driver, css_selector_password_input)
    submit_button = find_element(selenium_driver, css_selector_submit_button)

    username_input.send_keys(username)
    password_input.send_keys(password)
    submit_button.click()

    css_selector_carousel = (By.CSS_SELECTOR, "main .carousel")

    find_element(selenium_driver, css_selector_carousel)


def signup_user(selenium_driver, email, username, password):
    css_selector_inputs = (By.CSS_SELECTOR, "main form .form-control")
    css_selector_submit_button = (By.CSS_SELECTOR, "main form .btn-success")
    css_selector_alert_success = (By.CSS_SELECTOR, "main .alert-success")

    selenium_driver.get(FRONT_END_URL + "/signup")

    form_inputs = selenium_driver.find_elements(css_selector_inputs[0], css_selector_inputs[1])
    submit_button = find_element(selenium_driver, css_selector_submit_button)

    form_inputs[0].send_keys(email)
    form_inputs[1].send_keys(username)
    form_inputs[2].send_keys(password)
    form_inputs[3].send_keys(password)

    submit_button.click()

    find_element(selenium_driver, css_selector_alert_success)
