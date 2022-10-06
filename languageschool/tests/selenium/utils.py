from django.urls import reverse
from selenium.webdriver.common.by import By

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
    selenium_driver.get(live_server.url + reverse("account-login"))

    selenium_driver.find_element(By.ID, "inputUsername").send_keys(username)
    selenium_driver.find_element(By.ID, "inputPassword").send_keys(password)
    selenium_driver.find_element(By.ID, "submitLoginFormButton").click()


def assert_menu(selenium_driver, is_authenticated):
    home_link_items = selenium_driver.find_elements(By.ID, "homeLink")
    game_dropdown_items = selenium_driver.find_elements(By.ID, "gameDropdownItem")
    account_dropdown_items = selenium_driver.find_elements(By.ID, "accountDropdownItem")

    assert len(home_link_items) == 1
    assert len(game_dropdown_items) == 1
    assert len(account_dropdown_items) == 1

    article_game_link_items = selenium_driver.find_elements(By.ID, "articleGameLink")
    conjugation_game_link_items = selenium_driver.find_elements(By.ID, "conjugationGameLink")
    vocabulary_game_link_items = selenium_driver.find_elements(By.ID, "vocabularyGameLink")

    assert len(article_game_link_items) == 1
    assert len(conjugation_game_link_items) == 1
    assert len(vocabulary_game_link_items) == 1

    if is_authenticated:
        profile_link_items = selenium_driver.find_elements(By.ID, "profileLink")
        logout_link_items = selenium_driver.find_elements(By.ID, "logoutLink")
        assert len(profile_link_items) == 1
        assert len(logout_link_items) == 1
    else:
        sign_in_link_items = selenium_driver.find_elements(By.ID, "signInLink")
        login_link_items = selenium_driver.find_elements(By.ID, "loginLink")
        assert len(sign_in_link_items) == 1
        assert len(login_link_items) == 1


def get_form_error_message(selenium_driver, field):
    if field == "alert-danger":
        return selenium_driver.find_element(By.CLASS_NAME, "alert-danger").text

    field = selenium_driver.find_element(By.ID, field)
    return selenium_driver.execute_script("return arguments[0].validationMessage;", field)


def submit_form_user(selenium_driver, email, username, password, confirmation_password):
    selenium_driver.find_element(By.ID, "inputEmail").clear()
    selenium_driver.find_element(By.ID, "inputEmail").send_keys(email)
    selenium_driver.find_element(By.ID, "inputUsername").clear()
    selenium_driver.find_element(By.ID, "inputUsername").send_keys(username)
    selenium_driver.find_element(By.ID, "inputPassword").clear()
    selenium_driver.find_element(By.ID, "inputPassword").send_keys(password)
    selenium_driver.find_element(By.ID, "inputPasswordConf").clear()
    selenium_driver.find_element(By.ID, "inputPasswordConf").send_keys(confirmation_password)
    selenium_driver.find_element(By.ID, "submitButtonSignup").click()
