from django.urls import reverse
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User

WARNING_REQUIRED_EMAIL_FIREFOX_HTML = "Please enter an email address."
WARNING_REQUIRED_FIELD_HTML = "Please fill out this field."
WARNING_EMAIL_WITH_SPACE_HTML = "A part followed by '@' should not contain the symbol ' '."


def authenticate(live_server, selenium_driver, username, password):
    """
    Authenticates the specified user.

    :param live_server: Pytest live_server fixture
    :param selenium_driver: Selenium web driver
    :param username: username input
    :type username: str
    :param password: password input
    :type password: str
    """
    selenium_driver.get(live_server.url + reverse("login"))
    input_login_credentials(selenium_driver, username, password)


def input_login_credentials(selenium_driver, username, password):
    inputs = selenium_driver.find_elements(By.CSS_SELECTOR, "form .form-control")
    username_input = inputs[0]
    password_input = inputs[1]

    username_input.send_keys(username)
    password_input.send_keys(password)
    selenium_driver.find_element(By.CSS_SELECTOR, "form div .btn-success").click()

def assert_menu(selenium_driver, user=None):
    """
    Asserts that the top screen menu is properly displayed. The content to be displayed depends on whether the user is
    authenticated or not.

    :param selenium_driver: Selenium's web driver
    :param user: user that is authenticated
    :type user: User
    """
    search_tool_items = selenium_driver.find_elements(By.ID, "searchToolLink")
    game_dropdown_items = selenium_driver.find_elements(By.ID, "gameDropdownItem")
    account_dropdown_items = selenium_driver.find_elements(By.ID, "accountDropdownItem")
    about_us_items = selenium_driver.find_elements(By.ID, "aboutUsLink")

    assert len(search_tool_items) == 1
    assert len(game_dropdown_items) == 1
    assert len(account_dropdown_items) == 1
    assert len(about_us_items) == 1

    article_game_link_items = selenium_driver.find_elements(By.ID, "articleGameLink")
    conjugation_game_link_items = selenium_driver.find_elements(By.ID, "conjugationGameLink")
    vocabulary_game_link_items = selenium_driver.find_elements(By.ID, "vocabularyGameLink")

    assert len(article_game_link_items) == 1
    assert len(conjugation_game_link_items) == 1
    assert len(vocabulary_game_link_items) == 1

    greetings = selenium_driver.find_elements(By.ID, "greeting")

    profile_link_items = selenium_driver.find_elements(By.ID, "profileLink")
    logout_link_items = selenium_driver.find_elements(By.ID, "logoutLink")
    sign_in_link_items = selenium_driver.find_elements(By.ID, "signInLink")
    login_link_items = selenium_driver.find_elements(By.ID, "loginLink")

    if user is not None:
        assert len(profile_link_items) == 1
        assert len(logout_link_items) == 1
        assert len(sign_in_link_items) == 0
        assert len(login_link_items) == 0
        assert len(greetings) == 1
        assert greetings[0].text == "Hello, {}".format(user.username)
    else:
        assert len(profile_link_items) == 0
        assert len(logout_link_items) == 0
        assert len(sign_in_link_items) == 1
        assert len(login_link_items) == 1
        assert len(greetings) == 0


def get_form_error_message(selenium_driver, selector):
    """
    Gets the error message referring to an HTML field. This message can be a Django message displayed in a tag with the
    alert-danger class or as a popup in the HTML input field.

    :param selenium_driver selenium_driver: Selenium web driver
    :param selector: CSS selector for the concerned field

    :return: error message.
    """
    if selector == "form-error":
        return selenium_driver.find_element(By.CSS_SELECTOR, "form .form-error").text

    selector = selenium_driver.find_element(By.CSS_SELECTOR, selector)
    return selenium_driver.execute_script("return arguments[0].validationMessage;", selector)


def submit_form_user(selenium_driver, email, username, password, confirmation_password):
    """
    Fills and submits the user form (displayed on the signup page and on the update account page).

    :param selenium_driver: Selenium web driver
    :param email: email to be input
    :type email: str
    :param username: username to be input
    :type username: str
    :param password: password to be input
    :type password: str
    :param confirmation_password: password confirmation to be input
    :type confirmation_password: str
    """
    inputs = selenium_driver.find_elements(By.CSS_SELECTOR, "form .form-control")
    inputs_email = inputs[0]
    inputs_username = inputs[1]
    inputs_password = inputs[2]
    inputs_password_confirmation = inputs[3]

    inputs_email.clear()
    inputs_email.send_keys(email)
    inputs_username.clear()
    inputs_username.send_keys(username)
    inputs_password.clear()
    inputs_password.send_keys(password)
    inputs_password_confirmation.clear()
    inputs_password_confirmation.send_keys(confirmation_password)

    selenium_driver.find_element(By.CSS_SELECTOR, "form div .btn").click()
