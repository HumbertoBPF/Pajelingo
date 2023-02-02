import random
import time
from urllib.parse import urlencode

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.crypto import get_random_string
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from languageschool.models import AppUser, Language
from languageschool.tests.selenium.utils import assert_menu, authenticate, submit_user_form, submit_login_form, \
    fill_user_form, get_form_error
from languageschool.tests.utils import get_valid_password, get_random_email, get_random_username, \
    get_password_without_letters, get_password_without_digits, get_password_without_special_characters, \
    get_too_long_password, get_too_short_password, get_too_short_username
from pajelingo.validators.auth_password_validators import ERROR_LENGTH_PASSWORD, ERROR_LETTER_PASSWORD, \
    ERROR_DIGIT_PASSWORD, ERROR_SPECIAL_CHARACTER_PASSWORD, ALL_PASSWORD_ERRORS
from pajelingo.validators.validators import ERROR_NOT_CONFIRMED_PASSWORD, \
    ERROR_NOT_AVAILABLE_EMAIL, ERROR_NOT_AVAILABLE_USERNAME, ERROR_IMAGE_FILE_FORMAT, ERROR_USERNAME_FORMAT, \
    ERROR_EMAIL_FORMAT, ERROR_REQUIRED_FIELD, ERROR_USERNAME_LENGTH


class TestsProfileSelenium:
    def update_account_validation(self, live_server, selenium_driver, account, email, username, password,
                                  is_password_confirmed, field_index, error_message, is_server_side):
        user, user_password = account()[0]
        authenticate(live_server, selenium_driver, user.username, user_password)
        selenium_driver.get(live_server.url + reverse("update-user"))

        confirmation_password = password if is_password_confirmed else get_valid_password()

        if is_server_side:
            submit_user_form(selenium_driver, email, username, password, confirmation_password)
        else:
            fill_user_form(selenium_driver, email, username, password, confirmation_password)

        assert get_form_error(selenium_driver, field_index) == error_message
        assert not User.objects.filter(id=user.id, username=username, email=email).exists()
        assert not AppUser.objects.filter(user__id=user.id, user__username=username, user__email=email).exists()
        assert_menu(selenium_driver, user=user)

    @pytest.mark.django_db
    def test_profile_access_requires_authentication(self, live_server, selenium_driver, account):
        """
        Checks that users cannot access their profile without authentication
        """
        user, password = account()[0]
        # Checks that the login form is displayed when trying to access the URL
        url = reverse("profile")
        selenium_driver.get(live_server.url + url)
        assert selenium_driver.current_url == "{}{}?next={}".format(live_server.url, reverse("login"), url)
        assert_menu(selenium_driver)
        # Logs in and check if user is redirected
        submit_login_form(selenium_driver, user.username, password)

        assert selenium_driver.current_url == live_server.url + url
        assert_menu(selenium_driver, user=user)

    @pytest.mark.django_db
    def test_profile_access_with_authenticated_user_without_scores(self, live_server, selenium_driver, account,
                                                                   languages):
        """
        Checks that the credentials of users (username and email) are correctly rendered on their profile page
        """
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("profile"))

        username = selenium_driver.find_element(By.ID, "username")
        email = selenium_driver.find_element(By.ID, "email")
        default_picture_filename = selenium_driver.find_element(By.ID, "defaultPicture").get_attribute("src")
        warning_no_scores = selenium_driver.find_element(By.ID, "warningNoScores")

        assert default_picture_filename == live_server.url + "/static/images/profile.jpg"
        assert username.text == "Username: {}".format(user.username)
        assert email.text == "Email: {}".format(user.email)
        assert warning_no_scores.text == "It seems that you haven't played games in this language yet..."
        assert_menu(selenium_driver, user=user)

    @pytest.mark.django_db
    @pytest.mark.parametrize("has_language_filter", [True, False])
    def test_profile_access_with_authenticated_user_with_scores(self, live_server, selenium_driver, account, score,
                                                                games, languages, has_language_filter):
        """
        Checks that the scores of users are correctly rendered in their profile page
        """
        user, password = account()[0]
        scores = score(users=[user], games=games, languages=languages)
        authenticate(live_server, selenium_driver, user.username, password)

        selected_language = random.choice(list(languages)) if has_language_filter else Language.objects.first()
        scores = scores.filter(language=selected_language).order_by('game')

        url = live_server.url + reverse("profile")
        if has_language_filter is not None:
            query_string = urlencode({'language': selected_language.language_name})
            url = '{}?{}'.format(url, query_string)

        selenium_driver.get(url)

        username = selenium_driver.find_element(By.ID, "username")
        email = selenium_driver.find_element(By.ID, "email")
        default_picture_filename = selenium_driver.find_element(By.ID, "defaultPicture").get_attribute("src")
        header_score_tables = selenium_driver.find_element(By.TAG_NAME, "thead").find_element(By.TAG_NAME, "tr")
        dropdown_button = selenium_driver.find_element(By.ID, "dropdownButtonFilter")
        row_scores = selenium_driver.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

        assert default_picture_filename == live_server.url + "/static/images/profile.jpg"
        assert username.text == "Username: {}".format(user.username)
        assert email.text == "Email: {}".format(user.email)
        assert dropdown_button.text == selected_language.language_name
        assert header_score_tables.text == "{} {}".format("Game", "Score")

        for i in range(len(row_scores)):
            score = scores[i]
            assert row_scores[i].text == "{} {}".format(score.game.game_name, score.score)

        assert len(scores) == len(row_scores)
        assert_menu(selenium_driver, user=user)

    @pytest.mark.django_db
    def test_update_account_form_requires_authentication(self, live_server, selenium_driver, account):
        """
        Checks that the page with the update account form requires authentication
        """
        user, password = account()[0]
        # Checks that the login form is displayed when trying to access the URL
        url = reverse("update-user")
        selenium_driver.get(live_server.url + url)
        assert selenium_driver.current_url == "{}{}?next={}".format(live_server.url, reverse("login"), url)
        assert_menu(selenium_driver)
        # Logs in and check if user is redirected
        submit_login_form(selenium_driver, user.username, password)

        assert selenium_driver.current_url == live_server.url + url
        assert_menu(selenium_driver, user=user)

    @pytest.mark.django_db
    def test_update_account_form_rendering(self, live_server, selenium_driver, account):
        """
        Checks that the update account form renders correctly
        """
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("update-user"))

        inputs = selenium_driver.find_elements(By.CSS_SELECTOR, "form .form-control")
        inputs_email = inputs[0]
        inputs_username = inputs[1]
        inputs_password = inputs[2]
        inputs_password_confirmation = inputs[3]
        submits_button = selenium_driver.find_elements(By.CSS_SELECTOR, "form div .btn-info")

        assert len(inputs) == 4
        assert inputs_email.get_attribute("placeholder") == "Email address"
        assert inputs_username.get_attribute("placeholder") == "Username"
        assert inputs_password.get_attribute("placeholder") == "Password"
        assert inputs_password_confirmation.get_attribute("placeholder") == "Confirm your password"
        assert len(submits_button) == 1
        assert_menu(selenium_driver, user=user)

    @pytest.mark.parametrize(
        "email, username, password, is_password_confirmed, field_index, error_message", [
            (get_random_email(), get_too_short_username(), get_valid_password(), True, 2, ERROR_USERNAME_LENGTH),
            (get_random_email(), get_random_username(), "", True, 3, ALL_PASSWORD_ERRORS),
            (get_random_email(), "", get_valid_password(), True, 2,
             "{}\n{}".format(ERROR_REQUIRED_FIELD, ERROR_USERNAME_LENGTH)),
            ("", get_random_username(), get_valid_password(), True, 1, ERROR_REQUIRED_FIELD),
            (get_random_string(random.randint(1, 10)) + " " + get_random_email(), get_random_username(),
             get_valid_password(), True, 1, ERROR_EMAIL_FORMAT),
            (get_random_email(), get_random_string(random.randint(1, 10)) + " " + get_random_username(),
             get_valid_password(), True, 2, ERROR_USERNAME_FORMAT),
            (get_random_email(), get_random_username(), get_too_short_password(), True, 3, ERROR_LENGTH_PASSWORD),
            (get_random_email(), get_random_username(), get_too_long_password(), True, 3, ERROR_LENGTH_PASSWORD),
            (get_random_email(), get_random_username(), get_password_without_letters(), True, 3, ERROR_LETTER_PASSWORD),
            (get_random_email(), get_random_username(), get_password_without_digits(), True, 3, ERROR_DIGIT_PASSWORD),
            (get_random_email(), get_random_username(), get_password_without_special_characters(), True,
             3, ERROR_SPECIAL_CHARACTER_PASSWORD),
            (get_random_email(), get_random_username(), get_valid_password(), False, 4, ERROR_NOT_CONFIRMED_PASSWORD)
        ]
    )
    @pytest.mark.django_db
    def test_update_account_client_side_validation(self, live_server, selenium_driver, account, email, username,
                                                   password, is_password_confirmed, field_index, error_message):
        """
        Checks client-side validation errors when submitting the update account form
        """
        self.update_account_validation(live_server, selenium_driver, account, email, username, password,
                                       is_password_confirmed, field_index, error_message, False)

    @pytest.mark.parametrize(
        "email, username, password, is_password_confirmed, field_index, error_message", [
            (get_random_email(), get_too_short_username(), get_valid_password(), True, 2, ERROR_USERNAME_LENGTH),
            (get_random_email(), get_random_username(), "", True, 3, ERROR_REQUIRED_FIELD),
            (get_random_email(), "", get_valid_password(), True, 2, ERROR_REQUIRED_FIELD),
            ("", get_random_username(), get_valid_password(), True, 1, ERROR_REQUIRED_FIELD),
            (get_random_string(random.randint(1, 10)) + " " + get_random_email(), get_random_username(),
             get_valid_password(), True, 1, ERROR_EMAIL_FORMAT),
            (get_random_email(), get_random_string(random.randint(1, 10)) + " " + get_random_username(),
             get_valid_password(), True, 2, ERROR_USERNAME_FORMAT),
            (get_random_email(), get_random_username(), get_too_short_password(), True, 3, ERROR_LENGTH_PASSWORD),
            (get_random_email(), get_random_username(), get_too_long_password(), True, 3, ERROR_LENGTH_PASSWORD),
            (get_random_email(), get_random_username(), get_password_without_letters(), True, 3, ERROR_LETTER_PASSWORD),
            (get_random_email(), get_random_username(), get_password_without_digits(), True, 3, ERROR_DIGIT_PASSWORD),
            (get_random_email(), get_random_username(), get_password_without_special_characters(), True,
             3, ERROR_SPECIAL_CHARACTER_PASSWORD),
            (get_random_email(), get_random_username(), get_valid_password(), False, 4, ERROR_NOT_CONFIRMED_PASSWORD)
        ]
    )
    @pytest.mark.django_db
    def test_update_account_server_side_validation(self, live_server, selenium_driver, account, email, username,
                                                   password, is_password_confirmed, field_index, error_message):
        """
        Checks server-side validation errors when submitting the update account form
        """
        self.update_account_validation(live_server, selenium_driver, account, email, username, password,
                                       is_password_confirmed, field_index, error_message, True)

    @pytest.mark.parametrize(
        "is_repeated_email, is_repeated_username", [
            (True, False),
            (False, True),
            (True, True)
        ]
    )
    @pytest.mark.django_db
    def test_update_account_with_non_available_credentials(self, live_server, selenium_driver, account, is_repeated_email, is_repeated_username):
        """
        Checks that users cannot use other users usernames and emails when updating their accounts
        """
        accounts = account(n=random.randint(2, 10))
        user, password = accounts[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("update-user"))

        repeated_email = random.choice(accounts[1:])[0].email
        repeated_username = random.choice(accounts[1:])[0].username

        email = repeated_email if is_repeated_email else get_random_email()
        username = repeated_username if is_repeated_username else get_random_username()
        password = get_valid_password()

        submit_user_form(selenium_driver, email, username, password, password)

        expected_email_error = ERROR_NOT_AVAILABLE_EMAIL if is_repeated_email else ""
        expected_username_error = ERROR_NOT_AVAILABLE_USERNAME if is_repeated_username else ""

        assert get_form_error(selenium_driver, 1) == expected_email_error
        assert get_form_error(selenium_driver, 2) == expected_username_error

        # Checks that the authenticated user did not have its credentials changed
        assert not User.objects.filter(id=user.id, username=username, email=email).exists()
        assert not AppUser.objects.filter(user__id=user.id, user__username=username, user__email=email).exists()
        assert_menu(selenium_driver, user=user)

    @pytest.mark.parametrize(
        "is_same_email, is_same_username", [
            (True, False),
            (False, True),
            (True, True),
            (False, False)
        ]
    )
    @pytest.mark.django_db
    def test_update_account_with_valid_credentials(self, live_server, selenium_driver, account, is_same_email, is_same_username):
        """
        Checks that users can update their accounts using the current username and email
        """
        accounts = account(n=random.randint(2, 10))
        user, password = accounts[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("update-user"))

        email = user.email if is_same_email else get_random_email()
        username = user.username if is_same_username else get_random_username()
        password = get_valid_password()

        submit_user_form(selenium_driver, email, username, password, password)
        # Checks if the users are redirected to their profile
        assert selenium_driver.current_url == live_server.url + reverse("profile")
        # Checks that the update was successful
        assert User.objects.filter(id=user.id, username=username, email=email).exists()
        assert AppUser.objects.filter(user__id=user.id, user__username=username, user__email=email).exists()

        new_user = User.objects.filter(id=user.id, username=username, email=email).first()
        assert_menu(selenium_driver, user=new_user)

    @pytest.mark.django_db
    def test_delete_account_dialog_rendering(self, live_server, selenium_driver, account):
        """
        Checks that a dialog to confirm deletion is shown when users try to delete their accounts.
        """
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("profile"))

        selenium_driver.find_element(By.CSS_SELECTOR, ".btn-danger").click()

        modal_header = selenium_driver.find_element(By.CSS_SELECTOR, "#deleteModal .modal-dialog .modal-content .modal-header .modal-title")
        modal_body = selenium_driver.find_element(By.CSS_SELECTOR, "#deleteModal .modal-dialog .modal-content .modal-body")
        confirm_button = selenium_driver.find_element(By.CSS_SELECTOR, "#deleteModal .modal-dialog .modal-content .modal-footer .btn-danger")
        decline_button = selenium_driver.find_element(By.CSS_SELECTOR, "#deleteModal .modal-dialog .modal-content .modal-footer .btn-secondary")
        # Time to render the text
        time.sleep(1)
        assert modal_header.text == "Are you sure?"
        assert modal_body.text == "Are you sure that you want to delete your profile? All information such as scores in the games is going to be permanently lost!"
        assert confirm_button.text == "Yes, I want to delete my profile"
        assert decline_button.text == "Decline"
        # Checks that the user still exists in database
        assert User.objects.filter(id=user.id).exists()
        assert AppUser.objects.filter(user__id=user.id).exists()
        assert_menu(selenium_driver, user=user)

    @pytest.mark.django_db
    def test_delete_account(self, live_server, selenium_driver, account):
        """
        Checks users deletion on profile page
        """
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("profile"))

        selenium_driver.find_element(By.CSS_SELECTOR, ".btn-danger").click()
        # Waits "confirm deletion" button to appear to hit it
        wait = WebDriverWait(selenium_driver, 3)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-dialog .modal-content .modal-footer .btn-danger"))).click()

        assert not User.objects.filter(id=user.id).exists()
        assert not AppUser.objects.filter(user__id=user.id).exists()
        assert_menu(selenium_driver)

    @pytest.mark.django_db
    def test_update_picture_dialog_rendering(self, live_server, selenium_driver, account):
        """
        Checks that a dialog to confirm deletion is shown when users try to delete their accounts.
        """
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("profile"))

        selenium_driver.find_element(By.CSS_SELECTOR, "section div div .btn-info").click()

        modal_header = selenium_driver.find_element(By.CSS_SELECTOR,
                                                    "#updateProfilePictureModal .modal-dialog .modal-content .modal-header .modal-title")
        file_inputs = selenium_driver.find_elements(By.CSS_SELECTOR,
                                                  "#updateProfilePictureModal .modal-dialog .modal-content .modal-body .form-control")
        confirm_button = selenium_driver.find_element(By.CSS_SELECTOR,
                                                      "#updateProfilePictureModal .modal-dialog .modal-content .modal-footer .btn-success")
        decline_button = selenium_driver.find_element(By.CSS_SELECTOR,
                                                      "#updateProfilePictureModal .modal-dialog .modal-content .modal-footer .btn-secondary")
        # Time to render the text
        time.sleep(1)
        assert modal_header.text == "Update profile picture"
        assert len(file_inputs) == 1
        assert confirm_button.text == "Update"
        assert decline_button.text == "Cancel"
        assert_menu(selenium_driver, user=user)

    @pytest.mark.parametrize(
        "filename", [
            "C:\\Users\\Humberto\\Desktop\\Humberto\\Study\\WebDev\\Pajelingo\\pajelingo\\templates\\games\\article_game\\article_game_setup.html",
            "C:\\Users\\Humberto\\Desktop\\Humberto\\Study\\WebDev\\Pajelingo\\languageschool\\views\\games\\conjugation_game.py"
        ]
    )
    @pytest.mark.django_db
    def test_change_profile_pic_invalid_file(self, live_server, selenium_driver, account, filename):
        """
        Checks that an error is raised when trying to upload a file with a wrong format as profile picture.
        """
        user, password = account()[0]
        authenticate(live_server, selenium_driver, user.username, password)
        selenium_driver.get(live_server.url + reverse("profile"))

        selenium_driver.find_element(By.CSS_SELECTOR, "section div div .btn-info").click()

        # Waits the change profile picture modal to be displayed
        wait = WebDriverWait(selenium_driver, 3)
        wait.until(EC.element_to_be_clickable((By.ID, "id_picture"))).send_keys(filename)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-dialog .modal-content .modal-footer .btn-success"))).click()

        # Waits the change profile picture modal to display the error
        time.sleep(3)
        invalid_feedback = selenium_driver.find_element(By.CSS_SELECTOR, "#updateProfilePictureModal .modal-dialog .modal-content .modal-body .invalid-feedback")
        assert invalid_feedback.text == ERROR_IMAGE_FILE_FORMAT

        assert not AppUser.objects.filter(user__id=user.id).first().picture
        assert_menu(selenium_driver, user=user)
