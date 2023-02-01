from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse
from selenium.webdriver.common.by import By


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
    submit_login_form(selenium_driver, username, password)


def submit_login_form(selenium_driver, username, password):
    """
    Fills and submits the login form.

    :param selenium_driver: Selenium web driver
    :param username: username to be input
    :type username: str
    :param password: password to be input
    :type password: str
    """
    fill_login_form(selenium_driver, username, password)
    selenium_driver.find_element(By.CSS_SELECTOR, "form div .btn-success").click()


def fill_login_form(selenium_driver, username, password):
    """
    Fills the login form.

    :param selenium_driver: Selenium web driver
    :param username: username to be input
    :type username: str
    :param password: password to be input
    :type password: str
    """
    inputs = selenium_driver.find_elements(By.CSS_SELECTOR, "form .form-control")
    username_input = inputs[0]
    password_input = inputs[1]

    username_input.send_keys(username)
    password_input.send_keys(password)

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


def submit_user_form(selenium_driver, email, username, password, confirmation_password):
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
    fill_user_form(selenium_driver, email, username, password, confirmation_password)
    selenium_driver.find_element(By.CSS_SELECTOR, "form div .btn").click()


def fill_user_form(selenium_driver, email, username, password, confirmation_password):
    """
    Fills the user form (displayed on the signup page and on the update account page).

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
    email_input = inputs[0]
    username_input = inputs[1]
    password_input = inputs[2]
    confirm_password_input = inputs[3]

    email_input.clear()
    email_input.send_keys(email)
    username_input.clear()
    username_input.send_keys(username)
    password_input.clear()
    password_input.send_keys(password)
    confirm_password_input.clear()
    confirm_password_input.send_keys(confirmation_password)

def request_reset_account_via_website(live_server, selenium_driver, email):
    """
    Requests the reset of an account with the specified email on Pajelingo's webpage.

    :param live_server: live server fixture
    :param selenium_driver: Selenium web driver
    :param email: email address to be input
    """
    selenium_driver.get(live_server.url + reverse("login"))

    selenium_driver.find_element(By.ID, "reset_account_link").click()

    selenium_driver.find_element(By.ID, "id_email").send_keys(email)
    selenium_driver.find_element(By.CSS_SELECTOR, "form div .btn-success").click()

def get_reset_account_link():
    """
    Gets the reset account link of the specified user.

    :return: link for resetting account.
    """
    assert len(mail.outbox) == 1
    return "http" + mail.outbox[0].body.split("http")[1].split("\n\nIf you did not ask")[0]


def get_form_error(selenium_driver, field_index):
    """
    Gets the error text of the input at the specified position.

    :param selenium_driver: Selenium Web Driver
    :param field_index: position of the input that we are referring to
    :type field_index: int

    :return: the error text of the matched input.
    """
    css_selector = "form .form-floating:nth-child({}) .invalid-feedback".format(field_index+1)
    return selenium_driver.find_element(By.CSS_SELECTOR, css_selector).text
