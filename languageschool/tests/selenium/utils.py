import time

from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from languageschool.models import Score
from pajelingo.settings import FRONT_END_URL

# Pagination component CSS selectors
CSS_SELECTOR_PAGINATION = (By.CSS_SELECTOR, "main .pagination")
CSS_SELECTOR_ACTIVE_PAGE_BUTTON = (By.CSS_SELECTOR, "main .pagination .active .page-link")
# Profile page buttons
TEST_ID_UPDATE_PICTURE_BUTTON = "update-picture-button"
TEST_ID_EDIT_ACCOUNT_BUTTON = "update-item"
TEST_ID_DELETE_ACCOUNT_BUTTON = "delete-item"
TEST_ID_FAVORITE_WORDS_BUTTON = "favorite-item"

TEST_ID_EMAIL_INPUT = "email-input"
TEST_ID_USERNAME_INPUT = "username-input"
TEST_ID_BIO_INPUT = "bio-input"
TEST_ID_PASSWORD_INPUT = "password-input"
TEST_ID_CONFIRM_PASSWORD_INPUT = "password-confirmation-input"
TEST_ID_SUBMIT_BUTTON = "submit-button"
TEST_ID_LOGIN_BUTTON = "login-button"
TEST_ID_CAROUSEL = "carousel"

def find_by_test_id(selenium_driver, test_id):
    return find_element(selenium_driver, (By.CSS_SELECTOR, f"[data-testid=\"{test_id}\"]"))

def find_element(selenium_driver, locator):
    """
    Tries to find an element matching the specified locator.

    :param selenium_driver: Selenium web driver
    :param locator: locator to be matched
    :type locator: tuple

    :return: the element object matching the specified locator. If no element matching the locator could be found, a timeout exception is raised.
    """
    wait = WebDriverWait(selenium_driver, 10)
    return wait.until(ec.visibility_of_element_located(locator))

def wait_for_redirect(selenium_driver, url):
    """
    Expects a redirect to the specified url.

    :param selenium_driver: Selenium web driver
    :param url: expected url
    :type url: str
    """
    wait = WebDriverWait(selenium_driver, 10)
    wait.until(ec.url_to_be(url))

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
    wait.until(ec.text_to_be_present_in_element(locator, text))


def scroll_to_element(selenium_driver, element):
    """
    Scrolls the view to the specified element.

    :param selenium_driver: Selenium Web Driver
    :param element: element that we want to scroll to
    """
    selenium_driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(3)


def wait_number_of_elements_to_be(selenium_driver, locator, number):
    """
    Waits until the number of elements matching the specified locator to be equal to the number specified.

    :param selenium_driver: Selenium web driver
    :param locator: locator to be matched
    :type locator: tuple
    :param number: expected number of matched elements
    :type number: int
    """
    wait = WebDriverWait(selenium_driver, 10)
    wait.until(lambda browser: len(browser.find_elements(locator[0], locator[1])) == number)


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
    css_selector_games_dropdown = (By.CSS_SELECTOR, "header .dropdown .show .dropdown-item")
    css_selector_sign_up_button = (By.CSS_SELECTOR, "header .btn-success")
    css_selector_sign_in_button = (By.CSS_SELECTOR, "header .btn-primary")
    css_selector_username = (By.CSS_SELECTOR, "header .btn-account-options span")

    wait_number_of_elements_to_be(selenium_driver, css_selector_menu_items, 3)
    menu_items = selenium_driver.find_elements(css_selector_menu_items[0], css_selector_menu_items[1])

    assert menu_items[0].text == "Search"
    assert menu_items[1].text == "Games"
    assert menu_items[2].text == "About us"

    menu_items[0].click()

    wait_number_of_elements_to_be(selenium_driver, css_selector_games_dropdown, 2)
    dropdown_items = selenium_driver.find_elements(css_selector_games_dropdown[0], css_selector_games_dropdown[1])

    assert len(dropdown_items) == 2
    assert dropdown_items[0].text == "Dictionary"
    assert dropdown_items[1].text == "Account"

    menu_items[1].click()

    wait_number_of_elements_to_be(selenium_driver, css_selector_games_dropdown, 2)
    dropdown_items = selenium_driver.find_elements(css_selector_games_dropdown[0], css_selector_games_dropdown[1])

    assert len(dropdown_items) == 2
    assert dropdown_items[0].text == "Play"
    assert dropdown_items[1].text == "Rankings"

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
    selenium_driver.get(f"{FRONT_END_URL}/login")

    username_input = find_by_test_id(selenium_driver, TEST_ID_USERNAME_INPUT).find_element(By.CSS_SELECTOR, "input")
    username_input.send_keys(username)

    password_input = find_by_test_id(selenium_driver, TEST_ID_PASSWORD_INPUT).find_element(By.CSS_SELECTOR, "input")
    password_input.send_keys(password)

    submit_button = find_by_test_id(selenium_driver, TEST_ID_LOGIN_BUTTON)
    submit_button.click()

    find_by_test_id(selenium_driver, TEST_ID_CAROUSEL)


def signup_user(selenium_driver, email, username, bio, password):
    selenium_driver.get(f"{FRONT_END_URL}/signup")
    submit_user_form(selenium_driver, email, username, bio, password, True)

    css_selector_alert_success = (By.CSS_SELECTOR, "main .alert-success")
    find_element(selenium_driver, css_selector_alert_success)


def assert_public_account_data(selenium_driver, user):
    css_selector_username_credential = (By.CSS_SELECTOR, "[data-testid=\"username-data\"]")
    css_selector_bio_credential = (By.CSS_SELECTOR, "[data-testid=\"bio-data\"]")
    css_selector_badges = (By.CSS_SELECTOR, "main > .row .row:nth-of-type(2) > .col > button")

    wait_text_to_be_present(selenium_driver, css_selector_username_credential, f"Username: {user.username}")
    wait_text_to_be_present(selenium_driver, css_selector_bio_credential, f"Bio: {user.bio}")

    badges = selenium_driver.find_elements(css_selector_badges[0], css_selector_badges[1])

    assert len(badges) == user.badges.count()

    for badge in badges:
        badge_name = badge.text
        assert user.badges.filter(name=badge_name).exists()


def assert_private_account_data(selenium_driver, user):
    css_selector_email_credential = (By.CSS_SELECTOR, (By.CSS_SELECTOR, "[data-testid=\"email-data\"]"))
    wait_text_to_be_present(selenium_driver, css_selector_email_credential, f"Email: {user.email}")

    update_picture_button = find_by_test_id(selenium_driver, TEST_ID_UPDATE_PICTURE_BUTTON)
    assert update_picture_button.text == "Update picture"

    edit_account_button = find_by_test_id(selenium_driver, TEST_ID_EDIT_ACCOUNT_BUTTON)
    assert edit_account_button.text == "Edit account"

    delete_account_button = find_by_test_id(selenium_driver, TEST_ID_DELETE_ACCOUNT_BUTTON)
    assert delete_account_button.text == "Delete account"

    favorite_words_button = find_by_test_id(selenium_driver, TEST_ID_FAVORITE_WORDS_BUTTON)
    assert favorite_words_button.text == "Favorite words"


def assert_pagination(selenium_driver, current_page, number_pages):
    pagination = find_element(selenium_driver, CSS_SELECTOR_PAGINATION)

    page_buttons = pagination.find_elements(By.CSS_SELECTOR, ".page-link")
    active_page_button = find_element(selenium_driver, CSS_SELECTOR_ACTIVE_PAGE_BUTTON)
    first_page_button = page_buttons[0 if (current_page == 1) else 1]
    last_page_button = page_buttons[-1 if (current_page == number_pages) else -2]

    expected_text_first_page_button = "1\n(current)" if (current_page == 1) else "1"
    expected_text_last_page_button = "{}\n(current)".format(number_pages) \
        if (current_page == number_pages) else str(number_pages)

    if current_page != 1:
        assert page_buttons[0].text == "‹\nPrevious"

    assert active_page_button.text == "{}\n(current)".format(current_page)
    assert first_page_button.text == expected_text_first_page_button
    assert last_page_button.text == expected_text_last_page_button

    if current_page != number_pages:
        assert page_buttons[-1].text == "›\nNext"


def go_to_next_page(selenium_driver, current_page, number_pages):
    if current_page != number_pages:
        pagination = find_element(selenium_driver, CSS_SELECTOR_PAGINATION)
        page_buttons = pagination.find_elements(By.CSS_SELECTOR, ".page-link")
        selenium_driver.execute_script("arguments[0].click();", page_buttons[-1])


def assert_profile_language_filter(selenium_driver, languages_expected):
    css_selector_select_language_options = (By.CSS_SELECTOR, "main .row .row .col .form-select option")

    wait_number_of_elements_to_be(selenium_driver, css_selector_select_language_options, len(languages_expected))

    select_language_options = selenium_driver.find_elements(css_selector_select_language_options[0],
                                                            css_selector_select_language_options[1])

    assert len(select_language_options) == len(languages_expected)
    # Check that for each language expected, there is a corresponding select option
    language_dict = {}

    for language in languages_expected:
        language_dict[language.language_name] = True

    for language_option in select_language_options:
        del language_dict[language_option.text]

    assert len(language_dict) == 0


def assert_profile_scores(selenium_driver, user, language):
    css_selector_select_language = (By.CSS_SELECTOR, "main .row .row .col .form-select")
    css_selector_scores_table = (By.CSS_SELECTOR, "main .row .row .col .table")

    select_language = find_element(selenium_driver, css_selector_select_language)
    wait_attribute_to_be_non_empty(select_language, "innerHTML", 10)
    select_language.find_element(By.ID, language.language_name).click()

    scores_table = find_element(selenium_driver, css_selector_scores_table)
    scores_table_headers = scores_table.find_elements(By.CSS_SELECTOR, "thead tr th")
    score_table_records = scores_table.find_elements(By.CSS_SELECTOR, "tbody tr")

    assert scores_table_headers[0].text == "Game"
    assert scores_table_headers[1].text == "Score"

    expected_scores = Score.objects.filter(user=user, language=language)

    assert len(score_table_records) == expected_scores.count()

    for score_table_record in score_table_records:
        columns = score_table_record.find_elements(By.CSS_SELECTOR, "td")

        game_name = columns[0].text
        score = columns[1].text

        assert expected_scores.filter(
            game__game_name=game_name,
            score=score
        ).exists()


def submit_user_form(selenium_driver, email, username, bio, password, confirm_password):
    email_input = find_by_test_id(selenium_driver, TEST_ID_EMAIL_INPUT).find_element(By.CSS_SELECTOR, "input")
    email_input.clear()
    email_input.send_keys(email)

    username_input = find_by_test_id(selenium_driver, TEST_ID_USERNAME_INPUT).find_element(By.CSS_SELECTOR, "input")
    username_input.clear()
    username_input.send_keys(username)

    bio_input = find_by_test_id(selenium_driver, TEST_ID_BIO_INPUT).find_element(By.CSS_SELECTOR, "textarea")
    bio_input.clear()
    bio_input.send_keys(bio)

    password_input = find_by_test_id(selenium_driver, TEST_ID_PASSWORD_INPUT).find_element(By.CSS_SELECTOR, "input")
    password_input.send_keys(password)

    password_confirmation_input = find_by_test_id(selenium_driver, TEST_ID_CONFIRM_PASSWORD_INPUT)\
        .find_element(By.CSS_SELECTOR, "input")
    if confirm_password is None:
        password_confirmation_input.send_keys("")
    else:
        password_confirmation_input.send_keys(password if confirm_password else get_random_string(5) + password)

    submit_button = find_by_test_id(selenium_driver, TEST_ID_SUBMIT_BUTTON)
    scroll_to_element(selenium_driver, submit_button)
    submit_button.click()
