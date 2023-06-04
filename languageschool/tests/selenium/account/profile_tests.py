import random

import pytest
from selenium.webdriver.common.by import By

from languageschool.models import User
from languageschool.tests.selenium.utils import find_element, authenticate_user, assert_is_login_page, \
    assert_is_profile_page, assert_profile_language_filter, assert_profile_scores, CSS_SELECTOR_DELETE_ACCOUNT_BUTTON, \
    CSS_SELECTOR_EDIT_ACCOUNT_BUTTON, CSS_SELECTOR_UPDATE_PICTURE_BUTTON
from languageschool.tests.utils import attribute_user_badges
from pajelingo.settings import FRONT_END_URL

PROFILE_URL = FRONT_END_URL + "/profile"
CSS_SELECTOR_FORM_INPUTS = (By.CSS_SELECTOR, "main form .form-control")
CSS_SELECTOR_UPDATE_ACCOUNT_FORM_SUBMIT_BUTTON = (By.CSS_SELECTOR, "main form .btn-info")
CSS_SELECTOR_CREDENTIALS = (By.CSS_SELECTOR, "main section .col-lg-9 p")
CSS_SELECTOR_DIALOG_TILE = (By.CSS_SELECTOR, "body .modal .modal-header")
CSS_SELECTOR_DIALOG_BODY = (By.CSS_SELECTOR, "body .modal .modal-body")
CSS_SELECTOR_DIALOG_PROFILE_PICTURE = (By.CSS_SELECTOR, "body .modal .modal-body ul")
CSS_SELECTOR_DIALOG_CANCEL_BUTTON = (By.CSS_SELECTOR, "body .modal .modal-footer .btn-secondary")
CSS_SELECTOR_DIALOG_DANGER_BUTTON = (By.CSS_SELECTOR, "body .modal .modal-footer .btn-danger")
CSS_SELECTOR_DIALOG_SUCCESS_BUTTON = (By.CSS_SELECTOR, "body .modal .modal-footer .btn-success")
CSS_SELECTOR_ALERT_TOAST = (By.CSS_SELECTOR, "main .toast-container .toast")


def assert_is_update_account_page(selenium_driver):
    find_element(selenium_driver, CSS_SELECTOR_FORM_INPUTS)
    submit_button = find_element(selenium_driver, CSS_SELECTOR_UPDATE_ACCOUNT_FORM_SUBMIT_BUTTON)

    form_inputs = selenium_driver.find_elements(CSS_SELECTOR_FORM_INPUTS[0], CSS_SELECTOR_FORM_INPUTS[1])

    assert len(form_inputs) == 5
    assert submit_button.text == "Update"


@pytest.mark.django_db
def test_profile_requires_authentication(live_server, selenium_driver):
    """
    Tests that an unauthenticated user is redirected to the login page when accessing the profile page.
    """
    selenium_driver.get(PROFILE_URL)
    assert_is_login_page(selenium_driver)


@pytest.mark.django_db
def test_profile(live_server, selenium_driver, account):
    """
    Tests that the content of the profile page is displayed as expected, that is, that the username and email
    credentials as well as the "update profile picture", "edit account" and "delete account" button are displayed.
    """
    user, password = account()[0]
    attribute_user_badges()

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    assert_is_profile_page(selenium_driver, user, is_auth_user=True)


@pytest.mark.django_db
def test_profile_delete_account(live_server, selenium_driver, account):
    """
    Tests that deleting the profile works as expected, that is, a dialog is opened asking for confirmation and when
    users confirm, their account is deleted.
    """
    user, password = account()[0]

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    delete_account_button = find_element(selenium_driver, CSS_SELECTOR_DELETE_ACCOUNT_BUTTON)
    delete_account_button.click()

    delete_dialog_title = find_element(selenium_driver, CSS_SELECTOR_DIALOG_TILE)
    delete_dialog_body = find_element(selenium_driver, CSS_SELECTOR_DIALOG_BODY)
    delete_dialog_cancel_button = find_element(selenium_driver, CSS_SELECTOR_DIALOG_CANCEL_BUTTON)
    delete_dialog_delete_button = find_element(selenium_driver, CSS_SELECTOR_DIALOG_DANGER_BUTTON)

    assert delete_dialog_title.text == "Are you sure?"
    assert delete_dialog_body.text == "Are you sure that you want to delete your profile? All information such as " \
                                      "scores in the games is going to be permanently lost!"
    assert delete_dialog_cancel_button.text == "Cancel"
    assert delete_dialog_delete_button.text == "Yes, I want to delete my profile"

    delete_dialog_delete_button.click()

    assert_is_login_page(selenium_driver)
    assert not User.objects.filter(
        username=user.username,
        email=user.email
    ).exists()


@pytest.mark.django_db
def test_profile_update_account_redirect(live_server, selenium_driver, account):
    """
    Tests that when users click on the "update account" button, they are redirected to a page with the update account
    form.
    """
    user, password = account()[0]

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    edit_account_button = find_element(selenium_driver, CSS_SELECTOR_EDIT_ACCOUNT_BUTTON)
    edit_account_button.click()

    assert_is_update_account_page(selenium_driver)


@pytest.mark.django_db
def test_profile_update_profile_picture(live_server, selenium_driver, account):
    """
    Tests the update profile picture flow, that is, users must click on the "update profile picture" button, then
    a modal is opened asking for an image file. When an image file is provided and the users click on the "update"
    button, the users are redirected back to the profile page after having their profile picture updated.
    """
    user, password = account()[0]
    attribute_user_badges()

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    update_picture_button = find_element(selenium_driver, CSS_SELECTOR_UPDATE_PICTURE_BUTTON)
    update_picture_button.click()

    profile_picture_dialog_title = find_element(selenium_driver, CSS_SELECTOR_DIALOG_TILE)
    profile_picture_dialog_cancel_button = find_element(selenium_driver, CSS_SELECTOR_DIALOG_CANCEL_BUTTON)
    profile_picture_dialog_success_button = find_element(selenium_driver, CSS_SELECTOR_DIALOG_SUCCESS_BUTTON)

    assert profile_picture_dialog_title.text == "Update profile picture"
    assert profile_picture_dialog_cancel_button.text == "Cancel"
    assert profile_picture_dialog_success_button.text == "Update"

    profile_picture_dialog_success_button.click()

    assert_is_profile_page(selenium_driver, user, is_auth_user=True)


@pytest.mark.parametrize(
    "filename", [
        "C:\\Users\\Humberto\\Desktop\\Humberto\\Study\\WebDev\\Pajelingo\\requirements.txt",
        "C:\\Users\\Humberto\\Desktop\\Humberto\\Study\\WebDev\\Pajelingo\\languageschool\\views.py"
    ]
)
@pytest.mark.django_db
def test_profile_update_profile_picture_error_file_format(live_server, selenium_driver, account, filename):
    """
    Checks that the format of the uploaded profile picture file is validated, that is, if it is not an image, an error
    message is displayed below the modal's input.
    """
    user, password = account()[0]

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    update_picture_button = find_element(selenium_driver, CSS_SELECTOR_UPDATE_PICTURE_BUTTON)
    update_picture_button.click()

    profile_picture_dialog_title = find_element(selenium_driver, CSS_SELECTOR_DIALOG_TILE)
    profile_picture_dialog_body = find_element(selenium_driver, CSS_SELECTOR_DIALOG_BODY)
    profile_picture_dialog_cancel_button = find_element(selenium_driver, CSS_SELECTOR_DIALOG_CANCEL_BUTTON)
    profile_picture_dialog_success_button = find_element(selenium_driver, CSS_SELECTOR_DIALOG_SUCCESS_BUTTON)

    assert profile_picture_dialog_title.text == "Update profile picture"
    assert profile_picture_dialog_cancel_button.text == "Cancel"
    assert profile_picture_dialog_success_button.text == "Update"

    file_input = profile_picture_dialog_body.find_element(By.CSS_SELECTOR, "input")
    file_input.send_keys(filename)

    warning_file_not_image = find_element(selenium_driver, CSS_SELECTOR_DIALOG_PROFILE_PICTURE)
    assert warning_file_not_image.text == "The selected file is not an image"

    profile_picture_dialog_success_button.click()

    alert_toast = find_element(selenium_driver, CSS_SELECTOR_ALERT_TOAST)

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "An error occurred when processing the request. Please try again."


@pytest.mark.django_db
def test_profile_user_scores(live_server, selenium_driver, account, languages, score):
    """
    Tests that the expected user scores are displayed on the profile page.
    """
    user, password = account()[0]
    random_language = random.choice(languages)
    score([user], languages)

    authenticate_user(selenium_driver, user.username, password)

    selenium_driver.get(PROFILE_URL)

    assert_profile_language_filter(selenium_driver, languages)
    assert_profile_scores(selenium_driver, user, random_language)
