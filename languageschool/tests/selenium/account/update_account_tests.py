import pytest
from selenium.webdriver.common.by import By

from languageschool.models import User
from languageschool.tests.selenium.utils import authenticate_user, submit_user_form, wait_for_redirect, \
    find_by_test_id, assert_public_account_data, assert_private_account_data
from languageschool.tests.utils import get_random_username, get_valid_password, get_random_email, \
    get_random_bio, attribute_user_badges
from pajelingo.settings import FRONT_END_URL


@pytest.mark.django_db
def test_update_account_repeated_email(live_server, selenium_driver, account):
    """
    Tests that it is not possible to update the account credentials using other users' username and email.
    """
    accounts = account(n=2)

    user, user_password = accounts[0]
    another_user, _ = accounts[1]

    authenticate_user(selenium_driver, user.username, user_password)

    selenium_driver.get(f"{FRONT_END_URL}/dashboard")

    find_by_test_id(selenium_driver, "profile-dropdown").click()
    find_by_test_id(selenium_driver, "profile-item").click()
    find_by_test_id(selenium_driver, "update-item").click()

    email = another_user.email
    username = get_random_username()
    bio = get_random_bio()
    password = get_valid_password()

    submit_user_form(selenium_driver, email, username, bio, password, True)

    alert_toast = find_by_test_id(selenium_driver, "error-toast")

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "It was not possible to update account. Please check the information provided."


@pytest.mark.django_db
def test_update_account_repeated_username(live_server, selenium_driver, account):
    """
    Tests that it is not possible to update the account credentials using other users' username and email.
    """
    accounts = account(n=2)

    user, user_password = accounts[0]
    another_user, _ = accounts[1]

    authenticate_user(selenium_driver, user.username, user_password)

    selenium_driver.get(f"{FRONT_END_URL}/dashboard")

    find_by_test_id(selenium_driver, "profile-dropdown").click()
    find_by_test_id(selenium_driver, "profile-item").click()
    find_by_test_id(selenium_driver, "update-item").click()

    email = get_random_email()
    username = another_user.username
    bio = get_random_bio()
    password = get_valid_password()

    submit_user_form(selenium_driver, email, username, bio, password, True)

    alert_toast = find_by_test_id(selenium_driver, "error-toast")

    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-header").text == "Error"
    assert alert_toast.find_element(By.CSS_SELECTOR, ".toast-body").text == \
           "It was not possible to update account. Please check the information provided."


@pytest.mark.parametrize("is_same_username", [True, False])
@pytest.mark.parametrize("is_same_email", [True, False])
@pytest.mark.django_db
def test_update_account_same_credentials(live_server, selenium_driver, account, is_same_username, is_same_email):
    """
    Tests that it is allowed to keep the current username and/or email when updating the account credentials.
    """
    user, user_password = account()[0]
    attribute_user_badges()

    authenticate_user(selenium_driver, user.username, user_password)

    selenium_driver.get(f"{FRONT_END_URL}/dashboard")

    find_by_test_id(selenium_driver, "profile-dropdown").click()
    find_by_test_id(selenium_driver, "profile-item").click()
    find_by_test_id(selenium_driver, "update-item").click()

    email = user.email if is_same_email else get_random_email()
    username = user.username if is_same_username else get_random_username()
    bio = get_random_bio()
    password = get_valid_password()

    submit_user_form(selenium_driver, email, username, bio, password, True)
    # Waiting to be redirected to the profile
    wait_for_redirect(selenium_driver, f"{FRONT_END_URL}/profile")

    user = User.objects.filter(
        id=user.id,
        email=email,
        username=username,
        bio=bio
    ).first()
    assert user is not None

    assert_public_account_data(selenium_driver, user)
    assert_private_account_data(selenium_driver, user)
