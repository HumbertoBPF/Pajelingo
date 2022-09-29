from django.urls import reverse
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User


def authenticate(live_server, selenium_driver, user, password):
    """
    Authenticates the specified user.

    :param live_server: Pytest live_server fixture
    :param selenium_driver: Selenium web driver
    :param user: user to be authenticated
    :type user: User
    :param password: password of the user
    :type password: str
    """
    selenium_driver.get(live_server.url + reverse("account-login"))

    selenium_driver.find_element(By.ID, "inputUsername").send_keys(user.username)
    selenium_driver.find_element(By.ID, "inputPassword").send_keys(password)
    selenium_driver.find_element(By.ID, "submitLoginFormButton").click()


def assert_menu(selenium_driver, is_authenticated):
    home_link_items = selenium_driver.find_elements(By.ID, "home-link")
    game_dropdown_items = selenium_driver.find_elements(By.ID, "game-dropdown-item")
    account_dropdown_items = selenium_driver.find_elements(By.ID, "account-dropdown-item")

    assert len(home_link_items) == 1
    assert len(game_dropdown_items) == 1
    assert len(account_dropdown_items) == 1

    article_game_link_items = selenium_driver.find_elements(By.ID, "article-game-link")
    conjugation_game_link_items = selenium_driver.find_elements(By.ID, "conjugation-game-link")
    vocabulary_game_link_items = selenium_driver.find_elements(By.ID, "vocabulary-game-link")

    assert len(article_game_link_items) == 1
    assert len(conjugation_game_link_items) == 1
    assert len(vocabulary_game_link_items) == 1

    if is_authenticated:
        profile_link_items = selenium_driver.find_elements(By.ID, "profile-link")
        logout_link_items = selenium_driver.find_elements(By.ID, "logout-link")
        assert len(profile_link_items) == 1
        assert len(logout_link_items) == 1
    else:
        sign_in_link_items = selenium_driver.find_elements(By.ID, "sign-in-link")
        login_link_items = selenium_driver.find_elements(By.ID, "login-link")
        assert len(sign_in_link_items) == 1
        assert len(login_link_items) == 1
