import time

from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from languageschool.models import Score, Meaning
from pajelingo.settings import FRONT_END_URL

# Pagination component CSS selectors
CSS_SELECTOR_ACTIVE_PAGE_BUTTON = (By.CSS_SELECTOR, "main .pagination .active .page-link")
CSS_SELECTOR_MEANING_CARD = (By.CSS_SELECTOR, "main .card .card-body .card-text")

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

    username_input = find_by_test_id(selenium_driver, "username-input").find_element(By.CSS_SELECTOR, "input")
    username_input.send_keys(username)

    password_input = find_by_test_id(selenium_driver, "password-input").find_element(By.CSS_SELECTOR, "input")
    password_input.send_keys(password)

    submit_button = find_by_test_id(selenium_driver, "login-button")
    submit_button.click()

    find_by_test_id(selenium_driver, "carousel")


def signup_user(selenium_driver, email, username, bio, password):
    selenium_driver.get(f"{FRONT_END_URL}/signup")
    submit_user_form(selenium_driver, email, username, bio, password, True)

    css_selector_alert_success = (By.CSS_SELECTOR, "main .alert-success")
    find_element(selenium_driver, css_selector_alert_success)


def assert_public_account_data(selenium_driver, user):
    css_selector_username_credential = (By.CSS_SELECTOR, "[data-testid=\"username-data\"]")
    wait_text_to_be_present(selenium_driver, css_selector_username_credential, f"Username: {user.username}")

    css_selector_bio_credential = (By.CSS_SELECTOR, "[data-testid=\"bio-data\"]")
    wait_text_to_be_present(selenium_driver, css_selector_bio_credential, f"Bio: {user.bio}")

    css_selector_badges = (By.CSS_SELECTOR, "main > .row .row:nth-of-type(2) > .col > button")
    badges = selenium_driver.find_elements(css_selector_badges[0], css_selector_badges[1])

    assert len(badges) == user.badges.count()

    for badge in badges:
        badge_name = badge.text
        assert user.badges.filter(name=badge_name).exists()


def assert_private_account_data(selenium_driver, user):
    css_selector_email_credential = (By.CSS_SELECTOR, "[data-testid=\"email-data\"]")
    wait_text_to_be_present(selenium_driver, css_selector_email_credential, f"Email: {user.email}")

    update_picture_button = find_by_test_id(selenium_driver, "update-picture-button")
    assert update_picture_button.text == "Update picture"

    edit_account_button = find_by_test_id(selenium_driver, "update-item")
    assert edit_account_button.text == "Edit account"

    delete_account_button = find_by_test_id(selenium_driver, "delete-item")
    assert delete_account_button.text == "Delete account"

    favorite_words_button = find_by_test_id(selenium_driver, "favorite-item")
    assert favorite_words_button.text == "Favorite words"


def assert_meanings_of_word(selenium_driver, word):
    cards = selenium_driver.find_elements(CSS_SELECTOR_MEANING_CARD[0], CSS_SELECTOR_MEANING_CARD[1])

    nb_cards = len(cards)

    for i in range(nb_cards):
        card = cards[i]

        separator = "Meaning: " if (nb_cards == 1) else f"Meaning number {i + 1}: "
        meaning = card.text.split(separator)[1]

        assert Meaning.objects.filter(
            word=word,
            meaning=meaning
        ).exists()


def get_language_from_word_card(card):
    flag_img = card.find_element(By.CSS_SELECTOR, "img")
    alt_flag_img = flag_img.get_attribute("alt")
    return alt_flag_img.split(" language flag")[0]


def get_word_name_from_card_word(card):
    return card.find_element(By.CSS_SELECTOR, ".card-body .card-text").text


def assert_pagination(selenium_driver, current_page, number_pages):
    if current_page != 1:
        previous_page = find_by_test_id(selenium_driver, "previous-page")
        assert previous_page.text == "‹\nPrevious"

        first_page_button = find_by_test_id(selenium_driver, f"1th-page")
        assert first_page_button.text == "1"

    active_page_button = find_by_test_id(selenium_driver, "current-page")
    assert active_page_button.text == f"{current_page}\n(current)"

    if current_page != number_pages:
        next_page = find_by_test_id(selenium_driver, "next-page")
        assert next_page.text == "›\nNext"

        last_page_button = find_by_test_id(selenium_driver, f"{number_pages}th-page")
        assert last_page_button.text == str(number_pages)


def go_to_next_page(selenium_driver, current_page, number_pages):
    if current_page != number_pages:
        next_page = find_by_test_id(selenium_driver, "next-page")
        selenium_driver.execute_script("arguments[0].click();", next_page)


def assert_profile_scores(selenium_driver, user, language):
    scores_table = find_by_test_id(selenium_driver, "user-scores")

    scores_table_headers = scores_table.find_elements(By.CSS_SELECTOR, "thead tr th")
    score_table_records = scores_table.find_elements(By.CSS_SELECTOR, "tbody tr")

    assert scores_table_headers[0].text == "Game"
    assert scores_table_headers[1].text == "Score"

    for score_table_record in score_table_records:
        columns = score_table_record.find_elements(By.CSS_SELECTOR, "td")

        game_name = columns[0].text
        score = columns[1].text

        assert Score.objects.filter(
            user=user,
            language=language,
            game__game_name=game_name,
            score=score
        ).exists()


def submit_user_form(selenium_driver, email, username, bio, password, confirm_password):
    email_input = find_by_test_id(selenium_driver, "email-input").find_element(By.CSS_SELECTOR, "input")
    email_input.clear()
    email_input.send_keys(email)

    username_input = find_by_test_id(selenium_driver, "username-input").find_element(By.CSS_SELECTOR, "input")
    username_input.clear()
    username_input.send_keys(username)

    bio_input = find_by_test_id(selenium_driver, "bio-input").find_element(By.CSS_SELECTOR, "textarea")
    bio_input.clear()
    bio_input.send_keys(bio)

    password_input = find_by_test_id(selenium_driver, "password-input").find_element(By.CSS_SELECTOR, "input")
    password_input.send_keys(password)

    password_confirmation_input = find_by_test_id(selenium_driver, "password-confirmation-input")\
        .find_element(By.CSS_SELECTOR, "input")
    if confirm_password is None:
        password_confirmation_input.send_keys("")
    else:
        password_confirmation_input.send_keys(password if confirm_password else get_random_string(5) + password)

    submit_button = find_by_test_id(selenium_driver, "submit-button")
    scroll_to_element(selenium_driver, submit_button)
    submit_button.click()
